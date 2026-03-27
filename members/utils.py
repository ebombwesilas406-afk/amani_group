import secrets
import string
import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_password(length=10):
    """Generate a secure alphanumeric password of given length (8-12 recommended)."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def send_welcome_email(full_name, phone, password, email):
    """Send welcome email with credentials. Returns (sent_bool, error_or_None).

    This function will not log or return the password; it only returns success status.
    """
    if not email:
        logger.warning('No email provided for %s (%s); skipping welcome email', full_name, phone)
        return False, 'no-email'

    subject = 'Welcome to Amani Western Youth Collective'
    site_base = getattr(settings, 'SITE_DOMAIN', None) or getattr(settings, 'SITE_BASE_URL', None)
    if site_base:
        if site_base.startswith('http'):
            login_url = site_base.rstrip('/') + '/accounts/login/'
        else:
            login_url = 'http://' + site_base.rstrip('/') + '/accounts/login/'
    else:
        login_url = 'http://127.0.0.1:8000/accounts/login/'
    message = (
        f"Hello {full_name},\n\n"
        "You have been successfully registered as an active member of Amani Western Youth Collective.\n\n"
        "Login Details:\n"
        f"Phone: {phone}\n"
        f"Password: {password}\n\n"
        f"Login here: {login_url}\n\n"
        "Please change your password after logging in.\n\n"
        "Together in every season."
    )

    try:
        send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [email], fail_silently=False)
        return True, None
    except Exception as e:
        logger.exception('Error sending welcome email to %s: %s', email, e)
        return False, str(e)
