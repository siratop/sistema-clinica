from django.urls import path
from . import views

urlpatterns = [
    # Portada Pública
    path('', views.inicio, name='inicio'),
    
    # Área Privada
    path('dashboard/', views.dashboard, name='dashboard'),
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('pacientes/nuevo/', views.crear_paciente, name='crear_paciente'),
    path('registro/', views.registro_paciente, name='registro_paciente'),
    path('cita-invitado/', views.cita_invitado, name='cita_invitado'),
    path('pacientes/<int:id>/', views.detalle_paciente, name='detalle_paciente'), # Historial Clínico
    path('cms/', views.gestion_cms, name='gestion_cms'), # Panel bonito CMS
    path('cms/slide/<int:id>/', views.editar_slide, name='editar_slide'),
    path('cms/faq/<int:id>/', views.editar_faq, name='editar_faq'),
    
    path('registro/', views.registro_paciente, name='registro_paciente'),
    path('cita-invitado/', views.cita_invitado, name='cita_invitado'),
    path('accounts/login/', views.login, name='login'), # Asegúrate de que esto no choque con el login de django

    # CMS GESTIÓN
    path('cms/', views.gestion_cms, name='gestion_cms'),
    
    # Rutas para CREAR (NUEVAS)
    path('cms/slide/nuevo/', views.crear_slide, name='crear_slide'),
    path('cms/faq/nuevo/', views.crear_faq, name='crear_faq'),

    # Rutas para EDITAR (YA LAS TENÍAS)
    path('cms/slide/<int:id>/', views.editar_slide, name='editar_slide'),
    path('cms/faq/<int:id>/', views.editar_faq, name='editar_faq'),
]