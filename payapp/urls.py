from django.urls import path
from . import views
from .views import register_admin, show_conversion_form  # make sure to import the view
from django.urls import path
from .views import admin_dashboard  # Ensure this import is correct

urlpatterns = [
    path('send/', views.send_money, name='send_money'),
    path('request/', views.request_money, name='request_money'),
    path('transactions/', views.view_transactions, name='view_transactions'),
    path('requests/', views.view_requests, name='view_requests'),
    path('admin_transactions/', views.view_admin_transactions, name='view_admin_transactions'),
    path('admin_requests/', views.view_admin_requests, name='view_admin_requests'),
    path('admin_home/', views.view_admin_home, name='view_admin_home'),
    path('register/admin_registration', register_admin, name='register_admin'),

    path('conversion/form/', show_conversion_form, name='show_conversion_form'),
    # path('conversion/<str:currency1>/<str:currency2>/<str:amount_of_currency1>/', views.convert_currency, name='convert_currency'),

    path('process-payment/', views.process_payment, name='process_payment'),


    # Correctly reference views that exist in payapp.views
    #path('conversion/<str:currency1>/<str:currency2>/<float:amount_of_currency1>/', views.convert_currency, name='convert_currency'),
    # Add other payapp specific paths
    # # path('register/', views.admin_login, name='admin_login'),
    # path('signup/', views.signup, name='signup'),
    # path('login/', views.login, name='login'),
    # path('logout/', views.logout, name='logout'),
    #
    #
    # path('conversion/<str:currency1>/<str:currency2>/<float:amount_of_currency1>/', views.convert_currency, name='convert_currency'),

]
