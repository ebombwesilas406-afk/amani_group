from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import CustomUser
from members.models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        # create an empty profile for the user
        try:
            Profile.objects.create(user=instance)
        except Exception:
            # members app may not be ready in some contexts; silently ignore
            pass
