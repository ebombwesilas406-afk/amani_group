from .models import Profile

def current_profile(request):
    """Context processor to provide the logged-in user's Profile as `profile` in templates."""
    profile = None
    try:
        if request.user and request.user.is_authenticated:
            profile, _ = Profile.objects.get_or_create(user=request.user)
    except Exception:
        profile = None
    return {'profile': profile}
