from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.send_money, name='send_money'),
    path('request/', views.request_money, name='request_money'),
    path('transactions/', views.view_transactions, name='view_transactions'),
    path('requests/', views.view_requests, name='view_requests'),
    path('admin_transactions/', views.view_admin_transactions, name='view_admin_transactions'),
    path('admin_requests/', views.view_admin_requests, name='view_admin_requests'),
    path('admin_home/', views.view_admin_home, name='view_admin_home'),
]
