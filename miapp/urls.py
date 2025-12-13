from django.urls import path
from . import views

urlpatterns = [
   
    path('', views.dashboard, name='home'),
    path('pacientes/', views.saludo, name='lista_pacientes'), 
    path('paciente/<int:id>/', views.detalle_paciente, name='detalle_paciente'),
    path('paciente/nuevo/', views.crear_paciente, name='crear_paciente'),
    path('paciente/editar/<int:id>/', views.editar_paciente, name='editar_paciente'),
    path('paciente/eliminar/<int:id>/', views.eliminar_paciente, name='eliminar_paciente'),
    path('cita/nueva/<int:id_paciente>/', views.crear_cita, name='crear_cita'),
    path('cita/eliminar/<int:id>/', views.eliminar_cita, name='eliminar_cita'),
    path('cita/atender/<int:id_cita>/', views.atender_cita, name='atender_cita'),
    path('paciente/subir_archivo/<int:id_paciente>/', views.subir_documento, name='subir_documento'),
    path('cita/imprimir/<int:id_cita>/', views.imprimir_receta, name='imprimir_receta'),
]