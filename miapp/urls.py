from django.urls import path
from . import views

urlpatterns = [
    # Portada Pública
    path('', views.inicio, name='inicio'),
    
    # Área Privada
    path('dashboard/', views.dashboard, name='dashboard'),
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('pacientes/nuevo/', views.crear_paciente, name='crear_paciente'),
]