from django.urls import path, include
from . import views
urlpatterns = [
    path('',views.home,name='home'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('updates/',views.updates,name='updates'),
    path('rules/',views.rules,name='rules'),
    path('operations/',views.operations,name='support'),
    path('membership/',views.membership,name='membership'),
]