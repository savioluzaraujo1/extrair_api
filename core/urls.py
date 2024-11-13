# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('mostrar_dados/', views.mostrar_dados, name='mostrar_dados'),
    path('download_dados/', views.download_dados, name='download_dados'),
]
