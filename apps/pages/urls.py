from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "apps.pages"

urlpatterns = [
  path('', views.index,  name='index'),
  path('credentials/', views.credentials, name='credentials'),
  path('whatsapp/connect/<str:instance_name>/', views.whatsapp_connect, name='whatsapp_connect'),
  path('whatsapp/refresh-qr/<str:instance_name>/', views.whatsapp_refresh_qr, name='whatsapp_refresh_qr'),
]
