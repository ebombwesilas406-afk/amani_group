from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_edit, name='profile_edit'),
    path('profile/view/', views.profile_view, name='profile_view'),
    path('profile/pdf/', views.generate_pdf, name='profile_pdf'),
    path('profile/<int:user_id>/pdf/', views.generate_pdf, name='member_pdf'),
    path('members/', views.members_list, name='members_list'),
    path('payments/verify/<int:payment_id>/', views.verify_payment, name='verify_payment'),
    # Leader dashboard routes
    path('leader/', views.leader_home, name='leader_home'),
    path('leader/members/', views.members_list, name='leader_members'),
    path('leader/members/add/', views.add_member, name='leader_add_member'),
    path('leader/members/upload/', views.upload_members, name='leader_upload_members'),
    path('leader/members/<int:user_id>/edit/', views.edit_member, name='leader_edit_member'),
    path('leader/members/<int:user_id>/', views.member_detail, name='leader_member_detail'),
    path('leader/members/<int:user_id>/delete/', views.delete_member, name='leader_delete_member'),
    path('leader/members/<int:user_id>/suspend/', views.suspend_member, name='leader_suspend_member'),
    path('leader/members/<int:user_id>/unsuspend/', views.unsuspend_member, name='leader_unsuspend_member'),
    path('suspended/', views.suspended_notice, name='suspended'),
]
