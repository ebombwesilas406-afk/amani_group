from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, full_name, password=None, email=None, **extra_fields):
        if not phone_number:
            raise ValueError('Phone number required')
        phone_number = str(phone_number)
        user = self.model(phone_number=phone_number, full_name=full_name, email=email or '', **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, full_name, password, email=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, full_name, password, email=email, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('Chairman', 'Chairman'),
        ('Secretary', 'Secretary'),
        ('Treasurer', 'Treasurer'),
        ('Member', 'Member'),
    ]
    STATUS_CHOICES = [
        ('Visitor', 'Visitor'),
        ('Active', 'Active'),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=32, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Member')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Visitor')

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"
