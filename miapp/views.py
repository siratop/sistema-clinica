from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Paciente, Cita, Documento
from .forms import PacienteForm, CitaForm, ConsultaForm, DocumentoForm
import datetime
from django.contrib.auth import login
from django.contrib.auth.models import Group

# --- PÁGINA DE INICIO (PORTADA PÚBLICA) ---
def inicio(request):
    return render(request, 'miapp/inicio.html')

@login_required
def dashboard(request):
    # 1. VERIFICAR SI ES PACIENTE
    # Si el usuario tiene un perfil de paciente enlazado, le mostramos SU portal
    if hasattr(request.user, 'paciente_perfil'):
        paciente = request.user.paciente_perfil
        mis_citas = Cita.objects.filter(paciente=paciente).order_by('-fecha')
        return render(request, 'miapp/portal_paciente.html', {'paciente': paciente, 'citas': mis_citas})

    # 2. SI ES PERSONAL (MÉDICO/ADMIN) - MUESTRA EL DASHBOARD DE SIEMPRE
    total_pacientes = Paciente.objects.count()
    citas_hoy = Cita.objects.filter(fecha=datetime.date.today()).count()
    citas_pendientes = Cita.objects.filter(realizada=False).count()
    
    return render(request, 'miapp/dashboard.html', {
        'total_pacientes': total_pacientes,
        'citas_hoy': citas_hoy,
        'citas_pendientes': citas_pendientes
    })

# --- LISTA DE PACIENTES ---
@login_required
def lista_pacientes(request):
    pacientes = Paciente.objects.all().order_by('-id')
    return render(request, 'miapp/lista_pacientes.html', {'pacientes': pacientes})

# --- CREAR PACIENTE ---
@login_required
def crear_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente registrado correctamente.')
            return redirect('lista_pacientes')
    else:
        form = PacienteForm()
    return render(request, 'miapp/crear_paciente.html', {'form': form})

# --- VISTA DE REGISTRO DE PACIENTES ---
def registro_paciente(request):
    if request.method == 'POST':
        # Usamos 2 formularios: uno para usuario (clave) y otro para datos médicos
        # Nota: Por simplicidad en este paso, usaremos el PacienteForm y crearemos el usuario 'dummy' o 
        # mejor aún: creamos un formulario unificado. 
        # Para no complicarte, vamos a hacer que el paciente primero cree su usuario.
        
        form = PacienteForm(request.POST)
        if form.is_valid():
            # 1. Guardar datos del paciente
            paciente = form.save(commit=False)
            
            # 2. Crear Usuario de Login automáticamente basado en la Cédula
            # El usuario será la Cédula y la contraseña será su Cédula (temporalmente)
            user = User.objects.create_user(
                username=paciente.cedula, 
                password=paciente.cedula,  # Contraseña inicial = Cédula
                first_name=paciente.nombre, 
                last_name=paciente.apellido
            )
            
            # 3. Asignar Grupo "Pacientes"
            grupo_pacientes, created = Group.objects.get_or_create(name='Pacientes')
            user.groups.add(grupo_pacientes)
            
            # 4. Conectar y Guardar
            paciente.usuario = user
            paciente.save()
            
            # 5. Loguear y mandar a su perfil
            login(request, user)
            messages.success(request, f"¡Bienvenido {paciente.nombre}! Tu usuario y clave es tu Cédula.")
            return redirect('dashboard')
            
    else:
        form = PacienteForm()
    
    return render(request, 'miapp/registro_paciente.html', {'form': form})