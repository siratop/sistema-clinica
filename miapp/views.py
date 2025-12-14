from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Paciente, Cita, Documento
from .forms import PacienteForm, CitaForm, ConsultaForm, DocumentoForm
import datetime

# --- PÁGINA DE INICIO (PORTADA PÚBLICA) ---
def inicio(request):
    return render(request, 'miapp/inicio.html')

# --- PANEL DE CONTROL (PRIVADO) ---
@login_required
def dashboard(request):
    # Estadísticas simples para el tablero
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