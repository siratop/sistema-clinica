from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth import login
from django.contrib import messages
from .models import Paciente, Cita, Documento, PerfilUsuario, CarruselImagen, PreguntaFrecuente
from .forms import PacienteForm, CitaForm, ConsultaForm, DocumentoForm
import datetime

# --- 1. PORTADA CON CMS (CONTENIDO DINÁMICO) ---
def inicio(request):
    # Traemos las imágenes y preguntas activas desde la Base de Datos
    slides = CarruselImagen.objects.filter(activo=True).order_by('orden')
    faqs = PreguntaFrecuente.objects.filter(activa=True).order_by('orden')
    
    return render(request, 'miapp/inicio.html', {
        'slides': slides,
        'faqs': faqs
    })

# --- 2. CEREBRO DEL SISTEMA (DASHBOARD MULTI-ROL) ---
@login_required
def dashboard(request):
    # A. CASO PACIENTE: Si el usuario es un paciente, va a su portal
    if hasattr(request.user, 'paciente_perfil'):
        paciente = request.user.paciente_perfil
        mis_citas = Cita.objects.filter(paciente=paciente).order_by('-fecha')
        return render(request, 'miapp/portal_paciente.html', {
            'paciente': paciente, 
            'citas': mis_citas
        })

    # B. CASO PERSONAL: Verificamos qué rol tiene (Médico, Contador, Admin)
    try:
        perfil = request.user.perfilusuario
        rol = perfil.rol
    except:
        # Si es superusuario y no tiene perfil creado, lo tratamos como Admin
        rol = 'administrador'

    # --- VISTA DE CONTADOR ---
    if rol == 'contador':
        # Aquí puedes crear 'miapp/panel_contador.html' después
        return render(request, 'miapp/dashboard_admin.html', {
            'rol_titulo': 'Área Contable',
            'solo_finanzas': True # Variable para ocultar cosas médicas en el template si quieres
        })

    # --- VISTA DE MÉDICO ---
    if rol == 'medico':
         # El médico ve sus citas de HOY
         citas_hoy = Cita.objects.filter(medico=request.user, fecha=datetime.date.today())
         return render(request, 'miapp/panel_medico.html', {'citas': citas_hoy})

    # --- VISTA DE ADMINISTRADOR (CONTROL TOTAL) ---
    # Estadísticas Generales
    total_pacientes = Paciente.objects.count()
    medicos = PerfilUsuario.objects.filter(rol='medico')
    citas_hoy_total = Cita.objects.filter(fecha=datetime.date.today()).count()
    
    return render(request, 'miapp/dashboard_admin.html', {
        'total_pacientes': total_pacientes,
        'medicos': medicos,
        'citas_hoy': citas_hoy_total
    })

# --- 3. REGISTRO DE PACIENTES (CON USUARIO PERSONALIZADO) ---
def registro_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            # Obtener datos limpios del formulario
            datos = form.cleaned_data
            username_elegido = datos['username']
            password_elegido = datos['password']
            
            try:
                # 1. Crear el Usuario de Login
                user = User.objects.create_user(
                    username=username_elegido, 
                    password=password_elegido,
                    first_name=datos['nombre'], 
                    last_name=datos['apellido'],
                    email=datos['correo']
                )
                
                # 2. Asignar Grupo "Pacientes"
                grupo_pacientes, created = Group.objects.get_or_create(name='Pacientes')
                user.groups.add(grupo_pacientes)
                
                # 3. Guardar Ficha Médica enlazada
                paciente = form.save(commit=False)
                paciente.usuario = user
                paciente.save()
                
                # 4. Iniciar sesión automáticamente
                login(request, user)
                messages.success(request, "¡Registro exitoso! Bienvenido a tu portal.")
                return redirect('dashboard')
                
            except Exception as e:
                messages.error(request, f"Error: El nombre de usuario '{username_elegido}' ya está en uso. Prueba con otro.")
    else:
        form = PacienteForm()
    
    return render(request, 'miapp/registro_paciente.html', {'form': form})

# --- 4. CITA INVITADO (SIN REGISTRO) ---
def cita_invitado(request):
    return render(request, 'miapp/cita_invitado.html')

# --- 5. GESTIÓN ADMINISTRATIVA (Listados) ---
@login_required
def lista_pacientes(request):
    # Solo personal debería ver esto
    if hasattr(request.user, 'paciente_perfil'):
        return redirect('dashboard') # Expulsar si es paciente
        
    pacientes = Paciente.objects.all().order_by('-id')
    return render(request, 'miapp/lista_pacientes.html', {'pacientes': pacientes})

@login_required
def crear_paciente(request):
    # Vista para que el Admin cree pacientes manualmente
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save() # Aquí habría que ajustar si quieres crear usuario también
            messages.success(request, 'Paciente registrado manualmente.')
            return redirect('lista_pacientes')
    else:
        form = PacienteForm()
    return render(request, 'miapp/crear_paciente.html', {'form': form})

# --- GESTIÓN DE CONTENIDOS (PANEL AMIGABLE) ---
@login_required
def gestion_cms(request):
    # Verificamos que sea staff/admin
    if not request.user.is_staff:
        messages.error(request, "Acceso denegado.")
        return redirect('dashboard')

    # Procesar formularios si se envían cambios
    if request.method == 'POST':
        # Aquí podrías separar lógica para crear/editar, 
        # pero para simplificar, mostraremos la lista y botones de editar
        pass 

    slides = CarruselImagen.objects.all().order_by('orden')
    faqs = PreguntaFrecuente.objects.all().order_by('orden')
    
    return render(request, 'miapp/gestion_cms.html', {
        'slides': slides,
        'faqs': faqs
    })

# --- VISTA PARA EDITAR UN SLIDE ESPECÍFICO ---
@login_required
def editar_slide(request, id):
    slide = get_object_or_404(CarruselImagen, id=id)
    if request.method == 'POST':
        form = CarruselForm(request.POST, instance=slide)
        if form.is_valid():
            form.save()
            messages.success(request, "Imagen actualizada correctamente.")
            return redirect('gestion_cms')
    else:
        form = CarruselForm(instance=slide)
    return render(request, 'miapp/editar_generico.html', {'form': form, 'titulo': 'Editar Imagen Carrusel'})

# --- VISTA PARA EDITAR UNA PREGUNTA ---
@login_required
def editar_faq(request, id):
    faq = get_object_or_404(PreguntaFrecuente, id=id)
    if request.method == 'POST':
        form = PreguntaForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            messages.success(request, "Pregunta actualizada correctamente.")
            return redirect('gestion_cms')
    else:
        form = PreguntaForm(instance=faq)
    return render(request, 'miapp/editar_generico.html', {'form': form, 'titulo': 'Editar Pregunta Frecuente'})


# --- HISTORIAL CLÍNICO DEL PACIENTE (ADMIN/MÉDICO) ---
@login_required
def detalle_paciente(request, id):
    # Solo personal médico o admin puede ver esto
    if hasattr(request.user, 'paciente_perfil'):
        return redirect('dashboard')

    paciente = get_object_or_404(Paciente, id=id)
    # Traemos todas las citas, ordenadas por fecha reciente
    historial = Cita.objects.filter(paciente=paciente).order_by('-fecha')

    return render(request, 'miapp/detalle_paciente.html', {
        'paciente': paciente,
        'historial': historial
    })