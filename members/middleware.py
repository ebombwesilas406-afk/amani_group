import json
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import AuditLog, Profile
from django.shortcuts import redirect
from django.urls import reverse


class AuditAndSuspendMiddleware(MiddlewareMixin):
    """Logs requests for authenticated users and redirects suspended users to a notice page.

    Skips logging for static/media/admin paths.
    """
    SKIP_PREFIXES = ('/static/', '/media/', '/admin/')

    def process_request(self, request):
        # Enforce force_password_change: redirect users to password change page
        try:
            path = request.path
            if any(path.startswith(p) for p in self.SKIP_PREFIXES):
                return None
            user = getattr(request, 'user', None)
            if user and getattr(user, 'is_authenticated', False):
                try:
                    profile = user.profile
                    if getattr(profile, 'force_password_change', False):
                        # allow password change and logout views
                        pw_change = reverse('password_change')
                        pw_change_done = reverse('password_change_done')
                        logout = reverse('accounts:logout')
                        allowed = (pw_change, pw_change_done, logout)
                        if not any(path.startswith(a) for a in allowed):
                            return redirect(pw_change)
                except Exception:
                    pass
        except Exception:
            pass
        return None

    def process_response(self, request, response):
        try:
            path = request.path
            if any(path.startswith(p) for p in self.SKIP_PREFIXES):
                return response

            user = getattr(request, 'user', None)
            # Redirect suspended authenticated users to suspended notice
            if user and getattr(user, 'is_authenticated', False):
                try:
                    profile = user.profile
                    # If suspension expired, restore account
                    if profile.suspended and profile.suspended_until and profile.suspended_until <= timezone.now():
                        try:
                            profile.suspended = False
                            profile.suspended_until = None
                            profile.save()
                            # restore user active flag
                            if hasattr(user, 'is_active') and not user.is_active:
                                user.is_active = True
                                user.save()
                        except Exception:
                            pass

                    if profile.suspended and profile.suspended_until and profile.suspended_until > timezone.now():
                        # If current path is the suspended page, allow
                        if path not in ('/suspended/', '/members/suspended/'):
                            from django.shortcuts import redirect
                            return redirect('members:suspended')
                except Exception:
                    pass

            # Only log authenticated users to avoid DB growth from anonymous traffic
            if user and getattr(user, 'is_authenticated', False):
                params = ''
                try:
                    if request.method == 'GET':
                        params = json.dumps(request.GET.dict())
                    else:
                        # POST/PUT: avoid large files
                        try:
                            params = json.dumps({k: v for k, v in request.POST.items()})
                        except Exception:
                            params = ''
                except Exception:
                    params = ''

                ip = request.META.get('REMOTE_ADDR') or request.META.get('HTTP_X_FORWARDED_FOR', '')
                ua = request.META.get('HTTP_USER_AGENT', '')[:300]
                try:
                    AuditLog.objects.create(
                        user=user if user.is_authenticated else None,
                        path=path,
                        method=request.method,
                        status_code=getattr(response, 'status_code', None),
                        ip_address=ip,
                        user_agent=ua,
                        params=params,
                    )
                except Exception:
                    # Don't break the response on logging errors
                    pass
        except Exception:
            pass
        return response
