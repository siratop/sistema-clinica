from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth import login
from django.contrib import messages
import datetime
from django.db.models import Sum

# --- IMPORTACIÓN DE MODELOS ---
from .models import (
    Paciente, Cita, Documento, PerfilUsuario, 
    CarruselImagen, PreguntaFrecuente, AvisoImportante,
    PersonalAutorizado, MovimientoContable, OrdenMedica, Especialidad
)

# --- IMPORTACIÓN DE FORMULARIOS ---
from .forms import (
    PacienteForm, CitaForm, CitaInvitadoForm, ConsultaForm, DocumentoForm, 
    CarruselForm, PreguntaForm, AvisoForm,
    RegistroPersonalForm, MovimientoContableForm, OrdenMedicaForm, EjecucionOrdenForm
)

# ==========================================
# 1. VISTAS PÚBLICAS (PORTADA)
# ==========================================

def inicio(request):
    slides = CarruselImagen.objects.filter(activo=True).order_by('orden')
    faqs = PreguntaFrecuente.objects.filter(activa=True).order_by('orden')
    aviso = AvisoImportante.objects.filter(activo=True).last()
    
    return render(request, 'miapp/inicio.html', {
        'slides': slides,
        'faqs': faqs,
        'aviso': aviso
    })

def cita_invitado(request):
    if request.method == 'POST':
        form = CitaInvitadoForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            
            # Buscar o crear paciente (sin usuario)
            paciente, created = Paciente.objects.get_or_create(
                cedula=data['cedula'],
                defaults={
                    'nombre': data['nombre'], 'apellido': data['apellido'],
                    'telefono': data['telefono'], 'fecha_nacimiento': data['fecha_nacimiento'],
                    'sexo': data['sexo']
                }
            )
            if not created:
                paciente.telefono = data['telefono']
                paciente.save()

            Cita.objects.create(
                paciente=paciente, medico=data['medico'],
                fecha=data['fecha'], hora=data['hora'],
                motivo=data['motivo'], estado='pendiente'
            )
            messages.success(request, f"Cita agendada para {data['nombre']}.")
            return redirect('inicio')
    else:
        form = CitaInvitadoForm()
    return render(request, 'miapp/cita_invitado.html', {'form': form})

# ==========================================
# 2. SISTEMA DE REGISTRO (SEGURIDAD)
# ==========================================

def registro_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            try:
                user = User.objects.create_user(
                    username=datos['username'], password=datos['password'],
                    first_name=datos['nombre'], last_name=datos['apellido'],
                    email=datos['correo']
                )
                grupo, _ = Group.objects.get_or_create(name='Pacientes')
                user.groups.add(grupo)
                
                paciente = form.save(commit=False)
                paciente.usuario = user
                paciente.save()
                
                login(request, user)
                messages.success(request, "Registro de paciente exitoso.")
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f"Error: {e}")
    else:
        form = PacienteForm()
    return render(request, 'miapp/registro_paciente.html', {'form': form})

def registro_personal(request):
    # Solo permite registro si la cédula está en la LISTA BLANCA (PersonalAutorizado)
    if request.method == 'POST':
        form = RegistroPersonalForm(request.POST)
        if form.is_valid():
            try:
                cedula = form.cleaned_data['cedula_identidad']
                autorizado = PersonalAutorizado.objects.get(cedula=cedula)
                
                # Crear Usuario
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                    first_name=autorizado.nombre_completo,
                    email=f"{form.cleaned_data['username']}@clinica.com"
                )
                
                # Crear Perfil con Rol asignado por Admin
                PerfilUsuario.objects.create(
                    usuario=user,
                    cedula=cedula,
                    rol=autorizado.rol,
                    especialidad=autorizado.especialidad_asignada,
                    telefono=form.cleaned_data.get('telefono', '')
                )
                
                # Marcar cédula como usada para que no se duplique
                autorizado.usado = True
                autorizado.save()
                
                login(request, user)
                messages.success(request, f"Bienvenido al sistema: {autorizado.nombre_completo}")
                return redirect('dashboard')
                
            except Exception as e:
                messages.error(request, f"Error en registro: {e}")
    else:
        form = RegistroPersonalForm()
    return render(request, 'miapp/registro_personal.html', {'form': form})

# ==========================================
# 3. DASHBOARD INTELIGENTE (ROLES)
# ==========================================

@login_required
def dashboard(request):
    # 1. Si es PACIENTE
    if hasattr(request.user, 'paciente_perfil'):
        paciente = request.user.paciente_perfil
        mis_citas = Cita.objects.filter(paciente=paciente).order_by('-fecha')
        return render(request, 'miapp/portal_paciente.html', {'paciente': paciente, 'citas': mis_citas})

    # 2. Si es PERSONAL
    try:
        perfil = request.user.perfilusuario
    except:
        # Si es superusuario (Admin) sin perfil creado
        return dashboard_admin_general(request)

    # Redirección según ROL
    if perfil.rol == 'medico':
        return dashboard_medico(request)
    elif perfil.rol == 'contador' or perfil.rol == 'gerente':
        return dashboard_contable(request)
    elif perfil.rol == 'enfermera':
        return dashboard_enfermera(request)
    elif perfil.rol == 'secretaria':
        # La secretaria usa una vista similar al admin pero limitada
        return dashboard_admin_general(request)
    
    return redirect('inicio')

# --- SUB-DASHBOARDS ---

def dashboard_medico(request):
    # Citas del día y gestión de órdenes
    citas_hoy = Cita.objects.filter(medico=request.user, fecha=datetime.date.today())
    ordenes = OrdenMedica.objects.filter(medico=request.user).order_by('-fecha_creacion')[:10]
    
    if request.method == 'POST':
        # Formulario rápido para crear orden médica desde el dashboard
        form_orden = OrdenMedicaForm(request.POST)
        if form_orden.is_valid():
            orden = form_orden.save(commit=False)
            orden.medico = request.user
            orden.save()
            messages.success(request, "Orden médica enviada a enfermería.")
            return redirect('dashboard')
    else:
        form_orden = OrdenMedicaForm()

    return render(request, 'miapp/panel_medico.html', {
        'citas': citas_hoy, 
        'ordenes': ordenes,
        'form_orden': form_orden
    })

def dashboard_contable(request):
    movimientos = MovimientoContable.objects.all().order_by('-fecha')
    
    # Cálculos Financieros
    total_ingresos = sum(m.monto for m in movimientos if m.tipo == 'ingreso')
    total_egresos = sum(m.monto for m in movimientos if m.tipo in ['egreso', 'nomina', 'impuesto'])
    balance = total_ingresos - total_egresos
    
    if request.method == 'POST':
        form = MovimientoContableForm(request.POST)
        if form.is_valid():
            mov = form.save(commit=False)
            mov.responsable = request.user
            mov.save()
            messages.success(request, "Movimiento contable registrado.")
            return redirect('dashboard')
    else:
        form = MovimientoContableForm()
        
    return render(request, 'miapp/panel_contable.html', {
        'movimientos': movimientos,
        'ingresos': total_ingresos,
        'egresos': total_egresos,
        'balance': balance,
        'form': form
    })

def dashboard_enfermera(request):
    # Ver órdenes pendientes de ejecutar
    ordenes_pendientes = OrdenMedica.objects.filter(ejecutada=False).order_by('fecha_creacion')
    return render(request, 'miapp/panel_enfermera.html', {'ordenes': ordenes_pendientes})

def dashboard_admin_general(request):
    # Vista global
    total_pacientes = Paciente.objects.count()
    medicos = PerfilUsuario.objects.filter(rol='medico')
    citas_hoy = Cita.objects.filter(fecha=datetime.date.today()).count()
    return render(request, 'miapp/dashboard_admin.html', {
        'total_pacientes': total_pacientes,
        'medicos': medicos,
        'citas_hoy': citas_hoy
    })

# ==========================================
# 4. GESTIÓN DE PACIENTES
# ==========================================

@login_required
def lista_pacientes(request):
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
    paciente = get_object_or_404(Paciente, id=id)
    historial = Cita.objects.filter(paciente=paciente).order_by('-fecha')
    
    # Si es enfermera, puede ver órdenes asociadas a este paciente
    ordenes = OrdenMedica.objects.filter(paciente=paciente).order_by('-fecha_creacion')
    
    return render(request, 'miapp/detalle_paciente.html', {
        'paciente': paciente,
        'historial': historial,
        'ordenes': ordenes
    })

# ==========================================
# 5. GESTIÓN CMS (ADMINISTRADOR WEB)
# ==========================================
@login_required
def gestion_cms(request):
    if not request.user.is_staff: return redirect('dashboard')
    slides = CarruselImagen.objects.all().order_by('orden')
    faqs = PreguntaFrecuente.objects.all().order_by('orden')
    aviso = AvisoImportante.objects.last()
    return render(request, 'miapp/gestion_cms.html', {'slides': slides, 'faqs': faqs, 'aviso': aviso})

# --- CRUD Carrusel ---
@login_required
def crear_slide(request):
    if not request.user.is_staff: return redirect('dashboard')
    if request.method == 'POST':
        form = CarruselForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Imagen agregada.")
            return redirect('gestion_cms')
    else:
        form = CarruselForm()
    return render(request, 'miapp/editar_generico.html', {'form': form, 'titulo': 'Agregar Imagen'})

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
    return render(request, 'miapp/editar_generico.html', {'form': form, 'titulo': 'Editar Imagen'})

@login_required
def eliminar_slide(request, id):
    if not request.user.is_staff: return redirect('dashboard')
    slide = get_object_or_404(CarruselImagen, id=id)
    slide.delete()
    messages.success(request, "Imagen eliminada.")
    return redirect('gestion_cms')

# --- CRUD FAQ ---
@login_required
def crear_faq(request):
    if not request.user.is_staff: return redirect('dashboard')
    if request.method == 'POST':
        form = PreguntaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Pregunta creada.")
            return redirect('gestion_cms')
    else:
        form = PreguntaForm()
    return render(request, 'miapp/editar_generico.html', {'form': form, 'titulo': 'Crear Pregunta'})

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

# --- CRUD Aviso ---
@login_required
def editar_aviso(request):
    if not request.user.is_staff: return redirect('dashboard')
    aviso = AvisoImportante.objects.last()
    if request.method == 'POST':
        if aviso: form = AvisoForm(request.POST, instance=aviso)
        else: form = AvisoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Aviso actualizado.")
            return redirect('gestion_cms')
    else:
        form = AvisoForm(instance=aviso) if aviso else AvisoForm()
    return render(request, 'miapp/editar_generico.html', {'form': form, 'titulo': 'Editar Aviso'})

# ==========================================
# 6. ACCIONES DE ENFERMERÍA
# ==========================================
@login_required
def ejecutar_orden(request, id):
    # Vista para que la enfermera marque como realizada una orden
    orden = get_object_or_404(OrdenMedica, id=id)
    
    if request.method == 'POST':
        form = EjecucionOrdenForm(request.POST, instance=orden)
        if form.is_valid():
            ord_actualizada = form.save(commit=False)
            ord_actualizada.enfermera_responsable = request.user
            ord_actualizada.fecha_ejecucion = datetime.datetime.now()
            ord_actualizada.save()
            messages.success(request, "Orden ejecutada correctamente.")
            return redirect('dashboard')
    else:
        form = EjecucionOrdenForm(instance=orden)
        
    return render(request, 'miapp/editar_generico.html', {'form': form, 'titulo': f'Ejecutar Orden: {orden.paciente}'})