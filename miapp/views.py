from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, logout  # <--- IMPORTANTE: AGREGADO LOGOUT
from django.contrib import messages
import datetime
from django.db.models import Sum

# --- IMPORTACIÓN DE MODELOS ---
from .models import (
    Paciente, Cita, Documento, PerfilUsuario, 
    CarruselImagen, PreguntaFrecuente, AvisoImportante,
    PersonalAutorizado, MovimientoContable, OrdenMedica, Especialidad
)

# --- IMPORTACIÓN DE FORMULARIOS (AQUÍ ESTABA EL ERROR) ---
from .forms import (
    PacienteForm, CitaForm, CitaInvitadoForm, ConsultaForm, DocumentoForm, 
    CarruselForm,   # <--- AHORA SÍ ESTÁ INCLUIDO
    PreguntaForm, AvisoForm,
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

# --- NUEVA FUNCIÓN PARA CERRAR SESIÓN SIN ERRORES ---
def cerrar_sesion(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('inicio')

# ==========================================
# 2. SISTEMA DE REGISTRO
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
    if request.method == 'POST':
        form = RegistroPersonalForm(request.POST)
        if form.is_valid():
            try:
                cedula = form.cleaned_data['cedula_identidad']
                autorizado = PersonalAutorizado.objects.get(cedula=cedula)
                
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                    first_name=autorizado.nombre_completo,
                    email=f"{form.cleaned_data['username']}@clinica.com"
                )
                
                PerfilUsuario.objects.create(
                    usuario=user, cedula=cedula, rol=autorizado.rol,
                    especialidad=autorizado.especialidad_asignada,
                    telefono=form.cleaned_data.get('telefono', '')
                )
                
                autorizado.usado = True
                autorizado.save()
                
                login(request, user)
                messages.success(request, f"Bienvenido: {autorizado.nombre_completo}")
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f"Error: {e}")
    else:
        form = RegistroPersonalForm()
    return render(request, 'miapp/registro_personal.html', {'form': form})

# ==========================================
# 3. DASHBOARD
# ==========================================

@login_required
def dashboard(request):
    if hasattr(request.user, 'paciente_perfil'):
        paciente = request.user.paciente_perfil
        mis_citas = Cita.objects.filter(paciente=paciente).order_by('-fecha')
        return render(request, 'miapp/portal_paciente.html', {'paciente': paciente, 'citas': mis_citas})

    try:
        perfil = request.user.perfilusuario
    except:
        return dashboard_admin_general(request)

    if perfil.rol == 'medico': return dashboard_medico(request)
    elif perfil.rol in ['contador', 'gerente']: return dashboard_contable(request)
    elif perfil.rol == 'enfermera': return dashboard_enfermera(request)
    elif perfil.rol == 'secretaria': return dashboard_admin_general(request)
    
    return redirect('inicio')

def dashboard_medico(request):
    citas_hoy = Cita.objects.filter(medico=request.user, fecha=datetime.date.today())
    ordenes = OrdenMedica.objects.filter(medico=request.user).order_by('-fecha_creacion')[:10]
    
    if request.method == 'POST':
        form_orden = OrdenMedicaForm(request.POST)
        if form_orden.is_valid():
            orden = form_orden.save(commit=False)
            orden.medico = request.user
            orden.save()
            messages.success(request, "Orden enviada.")
            return redirect('dashboard')
    else:
        form_orden = OrdenMedicaForm()

    return render(request, 'miapp/panel_medico.html', {'citas': citas_hoy, 'ordenes': ordenes, 'form_orden': form_orden})

def dashboard_contable(request):
    movimientos = MovimientoContable.objects.all().order_by('-fecha')
    total_ingresos = sum(m.monto for m in movimientos if m.tipo == 'ingreso')
    total_egresos = sum(m.monto for m in movimientos if m.tipo in ['egreso', 'nomina', 'impuesto'])
    balance = total_ingresos - total_egresos
    
    if request.method == 'POST':
        form = MovimientoContableForm(request.POST)
        if form.is_valid():
            mov = form.save(commit=False)
            mov.responsable = request.user
            mov.save()
            messages.success(request, "Movimiento registrado.")
            return redirect('dashboard')
    else:
        form = MovimientoContableForm()
        
    return render(request, 'miapp/panel_contable.html', {'movimientos': movimientos, 'ingresos': total_ingresos, 'egresos': total_egresos, 'balance': balance, 'form': form})

def dashboard_enfermera(request):
    ordenes_pendientes = OrdenMedica.objects.filter(ejecutada=False).order_by('fecha_creacion')
    return render(request, 'miapp/panel_enfermera.html', {'ordenes': ordenes_pendientes})

def dashboard_admin_general(request):
    # 1. Estadísticas Generales
    total_pacientes = Paciente.objects.count()
    medicos_count = PerfilUsuario.objects.filter(rol='medico').count()
    citas_hoy = Cita.objects.filter(fecha=datetime.date.today()).count()
    
    # 2. Resumen Financiero
    movimientos = MovimientoContable.objects.all()
    
    # Calculamos
    ingresos_raw = sum(m.monto for m in movimientos if m.tipo == 'ingreso')
    egresos_raw = sum(m.monto for m in movimientos if m.tipo in ['egreso', 'nomina', 'impuesto'])
    balance_raw = ingresos_raw - egresos_raw

    # REDONDEO EN PYTHON (Para evitar el error de floatform en tu versión)
    total_ingresos = round(ingresos_raw, 2)
    total_egresos = round(egresos_raw, 2)
    balance = round(balance_raw, 2)

    return render(request, 'miapp/dashboard_admin.html', {
        'total_pacientes': total_pacientes,
        'medicos_count': medicos_count,
        'citas_hoy': citas_hoy,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'balance': balance
    })
# ==========================================
# 4. GESTIÓN PACIENTES Y CMS
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
            messages.success(request, 'Paciente registrado.')
            return redirect('lista_pacientes')
    else:
        form = PacienteForm()
    return render(request, 'miapp/crear_paciente.html', {'form': form})

@login_required
def detalle_paciente(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    historial = Cita.objects.filter(paciente=paciente).order_by('-fecha')
    ordenes = OrdenMedica.objects.filter(paciente=paciente).order_by('-fecha_creacion')
    return render(request, 'miapp/detalle_paciente.html', {'paciente': paciente, 'historial': historial, 'ordenes': ordenes})

@login_required
def gestion_cms(request):
    if not request.user.is_staff: return redirect('dashboard')
    slides = CarruselImagen.objects.all().order_by('orden')
    faqs = PreguntaFrecuente.objects.all().order_by('orden')
    aviso = AvisoImportante.objects.last()
    return render(request, 'miapp/gestion_cms.html', {'slides': slides, 'faqs': faqs, 'aviso': aviso})

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
            messages.success(request, "Actualizado.")
            return redirect('gestion_cms')
    else:
        form = CarruselForm(instance=slide)
    return render(request, 'miapp/editar_generico.html', {'form': form, 'titulo': 'Editar Imagen'})

@login_required
def eliminar_slide(request, id):
    if not request.user.is_staff: return redirect('dashboard')
    slide = get_object_or_404(CarruselImagen, id=id)
    slide.delete()
    return redirect('gestion_cms')

@login_required
def crear_faq(request):
    if not request.user.is_staff: return redirect('dashboard')
    if request.method == 'POST':
        form = PreguntaForm(request.POST)
        if form.is_valid():
            form.save()
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
            return redirect('gestion_cms')
    else:
        form = PreguntaForm(instance=faq)
    return render(request, 'miapp/editar_generico.html', {'form': form, 'titulo': 'Editar Pregunta'})

@login_required
def eliminar_faq(request, id):
    if not request.user.is_staff: return redirect('dashboard')
    faq = get_object_or_404(PreguntaFrecuente, id=id)
    faq.delete()
    return redirect('gestion_cms')

@login_required
def editar_aviso(request):
    if not request.user.is_staff: return redirect('dashboard')
    aviso = AvisoImportante.objects.last()
    if request.method == 'POST':
        form = AvisoForm(request.POST, instance=aviso) if aviso else AvisoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion_cms')
    else:
        form = AvisoForm(instance=aviso) if aviso else AvisoForm()
    return render(request, 'miapp/editar_generico.html', {'form': form, 'titulo': 'Editar Aviso'})

@login_required
def ejecutar_orden(request, id):
    orden = get_object_or_404(OrdenMedica, id=id)
    if request.method == 'POST':
        form = EjecucionOrdenForm(request.POST, instance=orden)
        if form.is_valid():
            ord_act = form.save(commit=False)
            ord_act.enfermera_responsable = request.user
            ord_act.fecha_ejecucion = datetime.datetime.now()
            ord_act.save()
            return redirect('dashboard')
    else:
        form = EjecucionOrdenForm(instance=orden)
    return render(request, 'miapp/editar_generico.html', {'form': form, 'titulo': 'Ejecutar Orden'})

# --- VISTAS ADMINISTRATIVAS NUEVAS ---

@login_required
def panel_finanzas(request):
    if not request.user.is_staff: return redirect('dashboard')
    
    # Procesar formulario de nuevo movimiento
    if request.method == 'POST':
        form = MovimientoContableForm(request.POST)
        if form.is_valid():
            mov = form.save(commit=False)
            mov.responsable = request.user
            mov.save()
            messages.success(request, "Movimiento registrado correctamente.")
            return redirect('panel_finanzas')
    else:
        form = MovimientoContableForm()

    # Cálculos
    movimientos = MovimientoContable.objects.all().order_by('-fecha')
    ingresos_raw = sum(m.monto for m in movimientos if m.tipo == 'ingreso')
    egresos_raw = sum(m.monto for m in movimientos if m.tipo in ['egreso', 'nomina', 'impuesto'])
    balance_raw = ingresos_raw - egresos_raw
    
    # Redondeo seguro para la plantilla
    total_ingresos = round(ingresos_raw, 2)
    total_egresos = round(egresos_raw, 2)
    balance = round(balance_raw, 2)

    return render(request, 'miapp/panel_finanzas.html', {
        'form': form,
        'movimientos': movimientos,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'balance': balance
    })

@login_required
def gestion_staff(request):
    # Solo muestra médicos activos
    medicos = PerfilUsuario.objects.filter(rol='medico')
    return render(request, 'miapp/gestion_staff.html', {'medicos': medicos})

@login_required
def gestion_autorizaciones(request):
    # Aquí el Admin agrega gente a la Lista Blanca
    if not request.user.is_superuser: return redirect('dashboard')

    # Guardar nueva autorización
    if request.method == 'POST':
        # Procesamos manualmente rápido o podrías crear un Form en forms.py
        cedula = request.POST.get('cedula')
        nombre = request.POST.get('nombre')
        rol = request.POST.get('rol')
        # Buscar especialidad si aplica
        esp_id = request.POST.get('especialidad')
        especialidad = None
        if esp_id:
            especialidad = Especialidad.objects.get(id=esp_id)

        PersonalAutorizado.objects.create(
            cedula=cedula, nombre_completo=nombre, rol=rol, especialidad_asignada=especialidad
        )
        messages.success(request, f"Autorizado: {nombre}")
        return redirect('gestion_autorizaciones')

    autorizados = PersonalAutorizado.objects.all().order_by('-id')
    especialidades = Especialidad.objects.all()
    
    return render(request, 'miapp/gestion_autorizaciones.html', {
        'autorizados': autorizados,
        'especialidades': especialidades
    })

@login_required
def bloquear_personal(request, id):
    # Solo el Super Admin puede hacer esto
    if not request.user.is_superuser: return redirect('dashboard')
    
    personal = get_object_or_404(PersonalAutorizado, id=id)
    
    # 1. Buscamos si ya tiene un usuario creado
    try:
        perfil = PerfilUsuario.objects.get(cedula=personal.cedula)
        usuario = perfil.usuario
        
        # 2. LO BLOQUEAMOS (No lo borramos)
        usuario.is_active = False  # Esto impide que inicie sesión
        usuario.save()
        messages.warning(request, f"El acceso de {personal.nombre_completo} ha sido BLOQUEADO. Sus citas se mantienen.")
    except PerfilUsuario.DoesNotExist:
        # Si no se había registrado aún, solo borramos la autorización
        messages.info(request, "Se eliminó la autorización (aún no tenía usuario).")

    # 3. Borramos/Marcamos la autorización para que no se pueda volver a registrar con esa cédula
    personal.delete() 
    
    return redirect('gestion_autorizaciones')