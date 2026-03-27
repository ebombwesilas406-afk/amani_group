from django.db import models
from django.conf import settings


class PreapprovedMember(models.Model):
    phone_number = models.CharField(max_length=32, unique=True)
    full_name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.phone_number


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    national_id = models.CharField(max_length=64, blank=True)
    completed = models.BooleanField(default=False)
    declaration_confirmed = models.BooleanField(default=False)
    signature = models.CharField(max_length=255, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    suspended = models.BooleanField(default=False)
    suspended_until = models.DateTimeField(null=True, blank=True)
    force_password_change = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile: {self.user}"

    def completion_percentage(self):
        """Simple completion metric based on required pieces."""
        total = 4
        score = 0
        if self.date_of_birth:
            score += 1
        if self.national_id:
            score += 1
        try:
            nok = self.user.nextofkin
            if nok and nok.full_name and nok.phone_number:
                score += 1
        except Exception:
            pass
        if self.user.beneficiaries.exists():
            score += 1
        return int((score / total) * 100)


class NextOfKin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=32)
    id_number = models.CharField(max_length=64, blank=True)
    address = models.TextField(blank=True)
    relationship = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"NOK: {self.full_name} ({self.user})"


class Beneficiary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='beneficiaries', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    relationship = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Beneficiary: {self.name} ({self.user})"


class Payment(models.Model):
    STATUS = [('Pending', 'Pending'), ('Confirmed', 'Confirmed')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default='Pending')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='verified_payments', on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.user} {self.amount} {self.status}"


class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField(null=True, blank=True)
    ip_address = models.CharField(max_length=50, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    params = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user = self.user.full_name if self.user else 'Anonymous'
        return f"{self.timestamp.isoformat()} {user} {self.method} {self.path}"
