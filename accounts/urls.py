from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('post-register/', views.post_register, name='post_register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # password change view that clears force flag
    path('password_change/', views.ForcePasswordChangeView.as_view(), name='password_change'),
    # profile routes (shortcuts to members app)
    path('profile/', views.profile_redirect, name='profile'),
    path('profile/edit/', views.edit_profile, name='profile_edit'),
    # include Django's built-in auth views for other auth URLs
    path('', include('django.contrib.auth.urls')),
]
