from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth import login
from django.contrib import messages
import datetime

# --- IMPORTACIÓN DE MODELOS ---
from .models import (
    Paciente, 
    Cita, 
    Documento, 
    PerfilUsuario, 
    CarruselImagen, 
    PreguntaFrecuente, 
    AvisoImportante
)

# --- IMPORTACIÓN DE FORMULARIOS ---
from .forms import (
    PacienteForm, 
    CitaForm, 
    ConsultaForm, 
    DocumentoForm, 
    CarruselForm,   
    PreguntaForm, 
    AvisoForm,
    CitaInvitadoForm  # <--- NUEVO: Formulario para invitados
)

# ==========================================
# 1. VISTAS PÚBLICAS (PORTADA Y CITAS)
# ==========================================
def inicio(request):
    # Traemos solo lo activo para mostrar al público
    slides = CarruselImagen.objects.filter(activo=True).order_by('orden')
    faqs = PreguntaFrecuente.objects.filter(activa=True).order_by('orden')
    # Traemos el último aviso activo (si existe)
    aviso = AvisoImportante.objects.filter(activo=True).last()
    
    return render(request, 'miapp/inicio.html', {
        'slides': slides,
        'faqs': faqs,
        'aviso': aviso
    })

# --- LÓGICA DE CITA RÁPIDA (NUEVO) ---
def cita_invitado(request):
    if request.method == 'POST':
        form = CitaInvitadoForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            
            # 1. BUSCAR O CREAR EL PACIENTE AUTOMÁTICAMENTE
            # Si la cédula ya existe, usamos ese paciente. Si no, creamos uno nuevo.
            paciente, created = Paciente.objects.get_or_create(
                cedula=data['cedula'],
                defaults={
                    'nombre': data['nombre'],
                    'apellido': data['apellido'],
                    'telefono': data['telefono'],
                    'fecha_nacimiento': data['fecha_nacimiento'],
                    'sexo': data['sexo']
                    # Nota: No creamos usuario de login, es solo un registro médico
                }
            )
            
            # Si el paciente ya existía, actualizamos su teléfono por si acaso cambió
            if not created:
                paciente.telefono = data['telefono']
                paciente.save()

            # 2. CREAR LA CITA EN EL SISTEMA
            Cita.objects.create(
                paciente=paciente,
                medico=data['medico'],
                fecha=data['fecha'],
                hora=data['hora'],
                motivo=data['motivo'],
                estado='pendiente'
            )
            
            messages.success(request, f"¡Listo {data['nombre']}! Tu cita ha sido agendada con éxito.")
            return redirect('inicio')
            
    else:
        form = CitaInvitadoForm()
    
    return render(request, 'miapp/cita_invitado.html', {'form': form})

# ==========================================
# 2. CEREBRO DEL SISTEMA (DASHBOARD)
# ==========================================
@login_required
def dashboard(request):
    # A. CASO PACIENTE: Si es paciente, va a su portal
    if hasattr(request.user, 'paciente_perfil'):
        paciente = request.user.paciente_perfil
        mis_citas = Cita.objects.filter(paciente=paciente).order_by('-fecha')
        return render(request, 'miapp/portal_paciente.html', {
            'paciente': paciente, 
            'citas': mis_citas
        })

    # B. CASO PERSONAL (Médico, Admin, etc.)
    try:
        perfil = request.user.perfilusuario
        rol = perfil.rol
    except:
        rol = 'administrador' # Por defecto si es superuser

    if rol == 'contador':
        return render(request, 'miapp/dashboard_admin.html', {'rol_titulo': 'Área Contable', 'solo_finanzas': True})

    if rol == 'medico':
         citas_hoy = Cita.objects.filter(medico=request.user, fecha=datetime.date.today())
         return render(request, 'miapp/panel_medico.html', {'citas': citas_hoy})

    # VISTA DE ADMINISTRADOR (Dashboard General)
    total_pacientes = Paciente.objects.count()
    medicos = PerfilUsuario.objects.filter(rol='medico')
    citas_hoy_total = Cita.objects.filter(fecha=datetime.date.today()).count()
    
    return render(request, 'miapp/dashboard_admin.html', {
        'total_pacientes': total_pacientes,
        'medicos': medicos,
        'citas_hoy': citas_hoy_total
    })

# ==========================================
# 3. GESTIÓN DE PACIENTES
# ==========================================
def registro_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            try:
                # 1. Crear Usuario
                user = User.objects.create_user(
                    username=datos['username'], 
                    password=datos['password'],
                    first_name=datos['nombre'], 
                    last_name=datos['apellido'],
                    email=datos['correo']
                )
                # 2. Asignar Grupo
                grupo, _ = Group.objects.get_or_create(name='Pacientes')
                user.groups.add(grupo)
                
                # 3. Guardar Paciente
                paciente = form.save(commit=False)
                paciente.usuario = user
                paciente.save()
                
                login(request, user)
                messages.success(request, "¡Registro exitoso!")
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f"Error: El usuario ya existe o datos inválidos. {e}")
    else:
        form = PacienteForm()
    return render(request, 'miapp/registro_paciente.html', {'form': form})

@login_required
def lista_pacientes(request):
    # Buscador simple
    query = request.GET.get('q')
    if query:
        pacientes = Paciente.objects.filter(nombre__icontains=query) | Paciente.objects.filter(cedula__icontains=query)
    else:
        pacientes = Paciente.objects.all().order_by('-id')
    return render(request, 'miapp/lista_pacientes.html', {'pacientes': pacientes})

@login_required
def crear_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente registrado manualmente.')
            return redirect('lista_pacientes')
    else:
        form = PacienteForm()
    return render(request, 'miapp/crear_paciente.html', {'form': form})

@login_required
def detalle_paciente(request, id):
    # Ficha técnica e historial
    paciente = get_object_or_404(Paciente, id=id)
    historial = Cita.objects.filter(paciente=paciente).order_by('-fecha')
    return render(request, 'miapp/detalle_paciente.html', {
        'paciente': paciente,
        'historial': historial
    })

# ==========================================
# 4. GESTIÓN CMS (CARRUSEL, FAQ, AVISOS)
# ==========================================
@login_required
def gestion_cms(request):
    if not request.user.is_staff: return redirect('dashboard')

    slides = CarruselImagen.objects.all().order_by('orden')
    faqs = PreguntaFrecuente.objects.all().order_by('orden')
    
    # Busca el aviso existente o toma el último creado
    aviso = AvisoImportante.objects.last()
    
    return render(request, 'miapp/gestion_cms.html', {
        'slides': slides,
        'faqs': faqs,
        'aviso': aviso
    })

# --- CARRUSEL (SLIDES) ---
@login_required
def crear_slide(request):
    if not request.user.is_staff: return redirect('dashboard')
    
    if request.method == 'POST':
        # request.FILES es OBLIGATORIO para subir imágenes
        form = CarruselForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Imagen agregada al carrusel.")
            return redirect('gestion_cms')
    else:
        form = CarruselForm()
    
    return render(request, 'miapp/editar_generico.html', {'form': form, 'titulo': 'Agregar Nueva Imagen'})

@login_required
def editar_slide(request, id):
    slide = get_object_or_404(CarruselImagen, id=id)
    if request.method == 'POST':
        form = CarruselForm(request.POST, request.FILES, instance=slide)
        if form.is_valid():
            form.save()
            messages.success(request, "Imagen actualizada.")
            return redirect('gestion_cms')
    else:
        form = CarruselForm(instance=slide)
    return render(request, 'miapp/editar_generico.html', {'form': form, 'titulo': 'Editar Imagen Carrusel'})

@login_required
def eliminar_slide(request, id):
    if not request.user.is_staff: return redirect('dashboard')
    slide = get_object_or_404(CarruselImagen, id=id)
    slide.delete()
    messages.success(request, "Imagen eliminada del carrusel.")
    return redirect('gestion_cms')

# --- PREGUNTAS FRECUENTES (FAQ) ---
@login_required
def crear_faq(request):
    if not request.user.is_staff: return redirect('dashboard')
    if request.method == 'POST':
        form = PreguntaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Pregunta frecuente creada.")
            return redirect('gestion_cms')
    else:
        form = PreguntaForm()
    return render(request, 'miapp/editar_generico.html', {'form': form, 'titulo': 'Crear Pregunta Frecuente'})

@login_required
def editar_faq(request, id):
    faq = get_object_or_404(PreguntaFrecuente, id=id)
    if request.method == 'POST':
        form = PreguntaForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            messages.success(request, "Pregunta actualizada.")
            return redirect('gestion_cms')
    else:
        form = PreguntaForm(instance=faq)
    return render(request, 'miapp/editar_generico.html', {'form': form, 'titulo': 'Editar Pregunta'})

@login_required
def eliminar_faq(request, id):
    if not request.user.is_staff: return redirect('dashboard')
    faq = get_object_or_404(PreguntaFrecuente, id=id)
    faq.delete()
    messages.success(request, "Pregunta eliminada.")
    return redirect('gestion_cms')

# --- AVISO IMPORTANTE ---
@login_required
def editar_aviso(request):
    if not request.user.is_staff: return redirect('dashboard')
    
    # Buscar el último aviso o crear uno temporal en memoria si no existe
    aviso = AvisoImportante.objects.last()
    
    if request.method == 'POST':
        if aviso:
            form = AvisoForm(request.POST, instance=aviso)
        else:
            form = AvisoForm(request.POST) # Crea uno nuevo si no había
            
        if form.is_valid():
            form.save()
            messages.success(request, "Aviso importante actualizado.")
            return redirect('gestion_cms')
    else:
        if aviso:
            form = AvisoForm(instance=aviso)
        else:
            form = AvisoForm()
            
    return render(request, 'miapp/editar_generico.html', {'form': form, 'titulo': 'Editar Aviso Importante'})