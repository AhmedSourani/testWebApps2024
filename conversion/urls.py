from django.urls import path
from . import views

# urlpatterns = [
#     path('conversion/<str:currency1>/<str:currency2>/<str:amount_of_currency1>/', views.convert_currency, name='convert_currency'),
#     # path('<str:currency1>/<str:currency2>/<str:amount_of_currency1>/', views.convert_currency, name='convert_currency'),
#     # path('<str:currency1>/<str:currency2>/<str:amount_of_currency1>/', views.convert_currency, name='convert_currency'),
# ]
urlpatterns = [
    path('<str:currency1>/<str:currency2>/<str:amount_of_currency1>/', views.convert_currency, name='convert_currency'),
]