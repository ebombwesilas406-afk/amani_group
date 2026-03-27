from django.contrib import admin
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings
from .models import Profile, NextOfKin, Beneficiary, Payment, PreapprovedMember
from .models import AuditLog
import logging

logger = logging.getLogger(__name__)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'completed')
    actions = ['resend_password_reset']

    def resend_password_reset(self, request, queryset):
        domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
        sent = 0
        skipped = 0
        for profile in queryset:
            email = getattr(profile.user, 'email', None)
            if not email:
                skipped += 1
                continue
            try:
                form = PasswordResetForm({'email': email})
                if form.is_valid():
                    # provide domain_override so links use correct host
                    form.save(request=request, from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None), use_https=False, email_template_name='registration/password_reset_email.html')
                    profile.email_sent = True
                    profile.save()
                    sent += 1
            except Exception as e:
                logger.exception('Error sending password reset to %s: %s', email, e)
        self.message_user(request, f'Password reset emails sent: {sent}. Skipped (no email): {skipped}.')
    resend_password_reset.short_description = 'Resend password-reset email to selected profiles'


@admin.register(NextOfKin)
class NextOfKinAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user')


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'verified_by', 'date')


@admin.register(PreapprovedMember)
class PreapprovedAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'full_name')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'method', 'path', 'status_code')
    readonly_fields = ('timestamp',)
    search_fields = ('user__full_name', 'path', 'ip_address')
