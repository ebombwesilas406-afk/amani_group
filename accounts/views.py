from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .forms import RegistrationForm
from members.models import PreapprovedMember
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from members.models import Profile
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfilePhotoForm
from django.contrib import messages


@login_required
def profile_redirect(request):
    return redirect('members:profile_view')


@login_required
def edit_profile(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)
    if request.method == 'POST':
        uform = UserUpdateForm(request.POST, instance=user)
        pform = ProfilePhotoForm(request.POST, request.FILES, instance=profile)
        if uform.is_valid() and pform.is_valid():
            uform.save()
            p = pform.save(commit=False)
            p.user = user
            p.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        uform = UserUpdateForm(instance=user)
        pform = ProfilePhotoForm(instance=profile)
    return render(request, 'profile/profile_edit.html', {'uform': uform, 'pform': pform, 'profile': profile})


class ForcePasswordChangeView(LoginRequiredMixin, auth_views.PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('password_change_done')

    def form_valid(self, form):
        # mark the user's profile as no longer forcing password change
        response = super().form_valid(form)
        try:
            profile, _ = Profile.objects.get_or_create(user=self.request.user)
            profile.force_password_change = False
            profile.save()
        except Exception:
            pass
        return response


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            phone = form.cleaned_data.get('phone_number')
            # Check preapproved list
            if PreapprovedMember.objects.filter(phone_number=phone).exists():
                user.status = 'Active'
            else:
                user.status = 'Visitor'
            user.save()
            return redirect('accounts:post_register')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def post_register(request):
    # Simple page to inform visitor vs active
    return render(request, 'accounts/post_register.html')


class LoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'
