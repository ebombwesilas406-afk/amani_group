from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.utils import role_required
from .models import Profile, NextOfKin, Beneficiary, Payment
from .forms import ProfileForm, NextOfKinForm, BeneficiaryForm
from django.db.models import Q
from .forms import UploadMembersForm
from django.forms import modelformset_factory
from django.contrib import messages
from django.utils.safestring import mark_safe
from .forms import LeaderMemberForm
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import logging
from django.conf import settings
from .utils import generate_password, send_welcome_email

User = get_user_model()


@login_required
def dashboard(request):
    user = request.user
    # Ensure profile exists
    profile, _ = Profile.objects.get_or_create(user=user)
    # Notify users who must change their password
    try:
        if profile.force_password_change:
            pwd_change_url = reverse('password_change')
            full_url = request.build_absolute_uri(pwd_change_url)
            messages.warning(request, mark_safe(f'Please change your temporary password. <a href="{full_url}">Change now</a>'))
    except Exception:
        pass
    completion = 100 if profile.completed else 40
    context = {'user': user, 'profile': profile, 'completion': completion}
    # Leaders see leader dashboard
    if user.role in ('Chairman', 'Secretary', 'Treasurer') or user.is_superuser:
        return render(request, 'members/dashboard_leader.html', context)
    return render(request, 'members/dashboard_member.html', context)


@login_required
def profile_edit(request):
    user = request.user
    if user.status != 'Active':
        messages.info(request, 'Only active members may complete the official form.')
        return redirect('members:dashboard')

    profile, _ = Profile.objects.get_or_create(user=user)
    NokForm = NextOfKinForm
    BeneficiaryFormSet = modelformset_factory(Beneficiary, form=BeneficiaryForm, extra=1, can_delete=True)

    if request.method == 'POST':
        pform = ProfileForm(request.POST, request.FILES, instance=profile)
        nok_form = NokForm(request.POST, instance=NextOfKin.objects.filter(user=user).first())
        bformset = BeneficiaryFormSet(request.POST, queryset=Beneficiary.objects.filter(user=user))
        if pform.is_valid() and nok_form.is_valid() and bformset.is_valid():
            p = pform.save(commit=False)
            p.user = user
            p.completed = True
            p.save()
            nok = nok_form.save(commit=False)
            nok.user = user
            nok.save()
            for bf in bformset:
                if bf.cleaned_data and not bf.cleaned_data.get('DELETE'):
                    ben = bf.save(commit=False)
                    ben.user = user
                    ben.save()
            messages.success(request, 'Profile saved')
            return redirect('members:dashboard')
    else:
        pform = ProfileForm(instance=profile)
        nok, _ = NextOfKin.objects.get_or_create(user=user)
        nok_form = NokForm(instance=nok)
        bformset = BeneficiaryFormSet(queryset=Beneficiary.objects.filter(user=user))

    return render(request, 'profile/official_form.html', {'pform': pform, 'nok_form': nok_form, 'bformset': bformset, 'profile': profile})


@login_required
def profile_view(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)
    completion = profile.completion_percentage()
    return render(request, 'profile/profile.html', {'user': user, 'profile': profile, 'completion': completion})


@login_required
def generate_pdf(request, user_id=None):
    # user_id: only leaders can request other users' PDFs
    from django.http import HttpResponse
    from django.template.loader import render_to_string

    if user_id:
        if not (request.user.role in ('Chairman', 'Secretary', 'Treasurer') or request.user.is_superuser):
            return HttpResponse('Forbidden', status=403)
        user = get_object_or_404(User, id=user_id)
    else:
        user = request.user

    profile, _ = Profile.objects.get_or_create(user=user)
    try:
        nok = user.nextofkin
    except Exception:
        nok = None
    beneficiaries = user.beneficiaries.all()

    from django.template.loader import render_to_string
    from django.http import HttpResponse
    try:
        from weasyprint import HTML
    except Exception:
        return HttpResponse('PDF generation library missing. Install WeasyPrint.', status=500)

    html_string = render_to_string('profile/pdf.html', {'user': user, 'profile': profile, 'nok': nok, 'beneficiaries': beneficiaries})
    try:
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf = html.write_pdf()
    except Exception as e:
        return HttpResponse(f'Error rendering PDF: {e}', status=500)

    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"membership_{user.phone_number}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@role_required(['Chairman', 'Secretary', 'Treasurer'])
def member_detail(request, user_id):
    member = get_object_or_404(User, id=user_id)
    profile, _ = Profile.objects.get_or_create(user=member)
    try:
        nok = member.nextofkin
    except Exception:
        nok = None
    beneficiaries = member.beneficiaries.all()
    return render(request, 'dashboard/member_detail.html', {'member': member, 'profile': profile, 'nok': nok, 'beneficiaries': beneficiaries})


@role_required(['Chairman', 'Secretary', 'Treasurer'])
def members_list(request):
    q = request.GET.get('q', '')
    if q:
        users = User.objects.filter(
            Q(full_name__icontains=q) |
            Q(phone_number__icontains=q) |
            Q(profile__national_id__icontains=q)
        ).order_by('-date_joined')
    else:
        users = User.objects.all().order_by('-date_joined')
    return render(request, 'dashboard/members.html', {'users': users, 'q': q})


@role_required(['Chairman', 'Secretary', 'Treasurer'])
def verify_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    payment.status = 'Confirmed'
    payment.verified_by = request.user
    payment.save()
    messages.success(request, 'Payment confirmed')
    return redirect('members:members_list')


@role_required(['Chairman', 'Secretary', 'Treasurer'])
def leader_home(request):
    # simple stats overview
    total = User.objects.count()
    active = User.objects.filter(status='Active').count()
    visitors = User.objects.filter(status='Visitor').count()
    return render(request, 'dashboard/home.html', {'total': total, 'active': active, 'visitors': visitors})


@role_required(['Chairman', 'Secretary', 'Treasurer'])
def add_member(request):
    if request.method == 'POST':
        form = LeaderMemberForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            pwd = data.get('password') or None
            user = User.objects.create_user(phone_number=data['phone_number'], full_name=data['full_name'], password=pwd)
            user.role = data['role']
            user.status = data['status']
            # staff flag for leaders only
            if user.role in ('Chairman',):
                user.is_staff = True
            user.save()
            messages.success(request, 'Member created')
            return redirect('members:members_list')
    else:
        form = LeaderMemberForm()
    return render(request, 'dashboard/add_member.html', {'form': form})


@role_required(['Chairman', 'Secretary'])
def upload_members(request):
    """Bulk upload members via CSV or XLSX. Only Chairman and Secretary allowed."""
    from django.http import HttpResponse
    import csv
    import io

    if request.method == 'POST':
        form = UploadMembersForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.cleaned_data['file']
            name = upload.name.lower()
            added = 0
            skipped = 0
            errors = []
            # Try pandas for Excel support
            try:
                import pandas as pd
            except Exception:
                pd = None

            rows = []
            try:
                if name.endswith('.xlsx') or name.endswith('.xls'):
                    if pd is None:
                        return HttpResponse('Excel support requires pandas/openpyxl. Install dependencies.', status=500)
                    df = pd.read_excel(upload)
                    rows = df.to_dict(orient='records')
                else:
                    # assume CSV
                    text = io.TextIOWrapper(upload.file, encoding='utf-8')
                    reader = csv.DictReader(text)
                    rows = list(reader)
            except Exception as e:
                return HttpResponse(f'Error reading file: {e}', status=400)

            from django.contrib.auth import get_user_model
            User = get_user_model()

            total_rows = len(rows)
            created = 0
            emails_sent = 0
            skipped = 0
            errors = []

            for idx, row in enumerate(rows, start=1):
                full_name = (row.get('Full Name') or row.get('full_name') or row.get('full name') or '').strip()
                phone = (row.get('Phone') or row.get('phone') or row.get('Phone Number') or row.get('phone_number') or '').strip()
                national_id = (row.get('National ID') or row.get('national_id') or row.get('id') or '').strip()
                role = (row.get('Role') or row.get('role') or 'Member').strip() or 'Member'
                status = (row.get('Status') or row.get('status') or 'Visitor').strip() or 'Visitor'
                email = (row.get('Email') or row.get('email') or '').strip()

                if not full_name or not phone:
                    skipped += 1
                    errors.append(f'Row {idx}: missing required full_name or phone')
                    continue

                # check duplicates by phone or email
                dup_q = Q(phone_number__iexact=phone)
                if email:
                    dup_q |= Q(email__iexact=email)
                if User.objects.filter(dup_q).exists():
                    skipped += 1
                    errors.append(f'Row {idx}: duplicate phone/email ({phone} / {email})')
                    continue

                try:
                    # generate secure password (10 chars)
                    pwd = generate_password(10)
                    user = User.objects.create_user(phone_number=phone, full_name=full_name, password=pwd, email=email)
                    user.role = role if role in dict(User.ROLE_CHOICES) else 'Member'
                    user.status = status if status in dict(User.STATUS_CHOICES) else 'Visitor'
                    user.save()

                    # ensure profile exists and force password change
                    from .models import Profile
                    profile, created_profile = Profile.objects.get_or_create(user=user)
                    profile.force_password_change = True
                    # populate national id if provided
                    if national_id and (not profile.national_id):
                        profile.national_id = national_id
                    profile.save()

                    # send welcome email only for Active users with email
                    try:
                        if user.status == 'Active' and email:
                            sent, err = send_welcome_email(full_name, phone, pwd, email)
                            if sent:
                                emails_sent += 1
                                profile.email_sent = True
                                profile.save()
                            else:
                                errors.append(f'Row {idx}: email not sent to {email} ({err})')
                        else:
                            if not email:
                                errors.append(f'Row {idx}: no email provided; skipping send')
                    except Exception as e:
                        logging.exception('Error sending welcome email for row %s: %s', idx, e)
                        errors.append(f'Row {idx}: email error {e}')

                    created += 1
                except Exception as e:
                    skipped += 1
                    logging.exception('Error creating user for row %s: %s', idx, e)
                    errors.append(f'Row {idx}: error creating user')

            summary = {
                'total_rows': total_rows,
                'created': created,
                'emails_sent': emails_sent,
                'skipped': skipped,
                'errors_count': len(errors),
            }
            return render(request, 'dashboard/upload_result.html', {'summary': summary, 'errors': errors})
    else:
        form = UploadMembersForm()
    return render(request, 'dashboard/upload_members.html', {'form': form})


@role_required(['Chairman', 'Secretary', 'Treasurer'])
def edit_member(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = LeaderMemberForm(request.POST)
        # allow editing existing user: ignore phone uniqueness check
        if form.is_valid():
            data = form.cleaned_data
            user.full_name = data['full_name']
            user.role = data['role']
            user.status = data['status']
            if data.get('password'):
                user.set_password(data.get('password'))
            user.save()
            messages.success(request, 'Member updated')
            return redirect('members:members_list')
    else:
        initial = {'full_name': user.full_name, 'phone_number': user.phone_number, 'role': user.role, 'status': user.status}
        form = LeaderMemberForm(initial=initial)
    return render(request, 'dashboard/edit_member.html', {'form': form, 'member': user})


@role_required(['Chairman', 'Secretary', 'Treasurer'])
def delete_member(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        # prevent leaders deleting themselves
        if request.user.id == user.id:
            messages.error(request, "You cannot delete your own account.")
            return redirect('members:members_list')

        action = request.POST.get('action', 'permanent')
        if action == 'suspend':
            # support suspension for a number of days (default 30)
            try:
                days = int(request.POST.get('suspend_days', 30))
            except Exception:
                days = 30
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.suspended = True
            profile.suspended_until = timezone.now() + timedelta(days=days)
            profile.save()
            messages.success(request, f'Member suspended for {days} days')
            return redirect('members:members_list')
        else:
            user.delete()
            messages.success(request, 'Member permanently deleted')
            return redirect('members:members_list')
    return render(request, 'dashboard/confirm_delete.html', {'member': user})


def suspended_notice(request):
    user = request.user
    suspended_until = None
    if user and getattr(user, 'is_authenticated', False):
        try:
            suspended_until = user.profile.suspended_until
        except Exception:
            suspended_until = None
    return render(request, 'accounts/suspended.html', {'suspended_until': suspended_until})


@role_required(['Chairman', 'Secretary', 'Treasurer'])
def suspend_member(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.user.id == user.id:
        messages.error(request, "You cannot suspend your own account.")
        return redirect('members:members_list')

    if request.method == 'POST':
        try:
            days = int(request.POST.get('suspend_days', 30))
        except Exception:
            days = 30
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.suspended = True
        profile.suspended_until = timezone.now() + timedelta(days=days)
        profile.save()
        messages.success(request, f'Member suspended for {days} days')
        return redirect('members:members_list')

    # GET
    default_days = 30
    return render(request, 'dashboard/suspend_member.html', {'member': user, 'default_days': default_days})


@role_required(['Chairman', 'Secretary', 'Treasurer'])
def unsuspend_member(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.user.id == user.id:
        messages.error(request, "You cannot unsuspend your own account.")
        return redirect('members:members_list')

    if request.method == 'POST':
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.suspended = False
        profile.suspended_until = None
        profile.save()
        messages.success(request, f'Member {user.full_name} unsuspended')
        return redirect('members:members_list')

    return render(request, 'dashboard/confirm_unsuspend.html', {'member': user})
