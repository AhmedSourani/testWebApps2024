from django.urls import path, include
from payapp.views import send_money
from . import views
from django.contrib.auth import views as auth_views

from django.urls import path
from .views import register_admin  # make sure to import the view

urlpatterns = [
    path('home/', views.home, name='home'),
    path('', views.home),
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('register/', views.register_user, name='register_user'),
    path('register/admin_registration', register_admin, name='register_admin'),
    path('payapp/', include('payapp.urls')),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # path('signup/', views.signup, name='signup'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),


]
