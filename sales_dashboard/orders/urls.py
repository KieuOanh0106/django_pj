# sales/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/sales-data/', views.api_sales_data, name='api_sales_data'),
    path('api/test/', views.api_test, name='api_test'),
]
