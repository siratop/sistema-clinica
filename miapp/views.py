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
        form = PacienteForm(request.POST)
        if form.is_valid():
            # 1. Obtener datos del formulario
            datos = form.cleaned_data
            username_elegido = datos['username']
            password_elegido = datos['password']
            
            # 2. Crear Usuario con los datos que la persona eligió
            try:
                user = User.objects.create_user(
                    username=username_elegido, 
                    password=password_elegido,
                    first_name=datos['nombre'], 
                    last_name=datos['apellido'],
                    email=datos['correo'] # Guardamos el correo en el usuario también
                )
                
                # 3. Asignar Grupo "Pacientes"
                grupo_pacientes, created = Group.objects.get_or_create(name='Pacientes')
                user.groups.add(grupo_pacientes)
                
                # 4. Guardar Paciente (sin volver a guardar user/pass en el modelo Paciente)
                paciente = form.save(commit=False)
                paciente.usuario = user
                paciente.save()
                
                # 5. Loguear y entrar
                login(request, user)
                messages.success(request, "¡Registro exitoso! Bienvenido a tu portal.")
                return redirect('dashboard')
                
            except Exception as e:
                messages.error(request, f"Error al crear usuario: {e}. Quizás ese nombre de usuario ya existe.")
    else:
        form = PacienteForm()
    
    return render(request, 'miapp/registro_paciente.html', {'form': form})