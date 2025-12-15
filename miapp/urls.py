from django.urls import path
from . import views
# Importamos la vista de login estándar de Django
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # --- PÚBLICO ---
    path('', views.inicio, name='inicio'),
    path('cita-invitado/', views.cita_invitado, name='cita_invitado'),
    
    # --- AUTENTICACIÓN (LOGIN / LOGOUT) ---
    # Usamos la vista estándar para login
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    # Usamos nuestra vista personalizada para logout (para evitar el error 405)
    path('salir/', views.cerrar_sesion, name='logout'),

    # --- REGISTROS ---
    path('registro/', views.registro_paciente, name='registro_paciente'),
    path('registro-personal/', views.registro_personal, name='registro_personal'),

    # --- DASHBOARD Y GESTIÓN ---
    path('dashboard/', views.dashboard, name='dashboard'),
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('pacientes/nuevo/', views.crear_paciente, name='crear_paciente'),
    path('pacientes/<int:id>/', views.detalle_paciente, name='detalle_paciente'),

    # --- CMS ---
    path('cms/', views.gestion_cms, name='gestion_cms'),
    path('cms/slide/nuevo/', views.crear_slide, name='crear_slide'),
    path('cms/slide/<int:id>/', views.editar_slide, name='editar_slide'),
    path('cms/slide/eliminar/<int:id>/', views.eliminar_slide, name='eliminar_slide'),
    path('cms/faq/nuevo/', views.crear_faq, name='crear_faq'),
    path('cms/faq/<int:id>/', views.editar_faq, name='editar_faq'),
    path('cms/faq/eliminar/<int:id>/', views.eliminar_faq, name='eliminar_faq'),
    path('cms/aviso/editar/', views.editar_aviso, name='editar_aviso'),

    # --- ENFERMERÍA ---
    path('orden/ejecutar/<int:id>/', views.ejecutar_orden, name='ejecutar_orden'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)