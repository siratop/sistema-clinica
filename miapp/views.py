from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse  # <--- AGREGADO: Necesario para el PDF
from django.db.models import Q
from datetime import date

# Importamos modelos y formularios
from .models import Paciente, Cita, Documento
from .forms import PacienteForm, CitaForm, ConsultaForm, DocumentoForm

# Importamos la utilidad para generar PDF
from .utils import render_to_pdf      # <--- AGREGADO: Necesario para crear el PDF

# --- 1. DASHBOARD (Panel Principal) ---
@login_required
def dashboard(request):
    total_pacientes = Paciente.objects.count()
    total_citas_pendientes = Cita.objects.filter(realizada=False).count()
    citas_hoy = Cita.objects.filter(fecha=date.today(), realizada=False).count()
    
    return render(request, 'miapp/dashboard.html', {
        'total_pacientes': total_pacientes,
        'total_citas_pendientes': total_citas_pendientes,
        'citas_hoy': citas_hoy
    })

# --- 2. LISTADO DE PACIENTES (Con Buscador) ---
@login_required
def saludo(request):
    query = request.GET.get('q')
    if query:
        lista_pacientes = Paciente.objects.filter(
            Q(nombre__icontains=query) | 
            Q(apellido__icontains=query) | 
            Q(dni__icontains=query)
        )
    else:
        lista_pacientes = Paciente.objects.all()
    
    return render(request, 'miapp/lista_pacientes.html', {
        'pacientes': lista_pacientes
    })

# --- 3. DETALLE DE PACIENTE (Ficha con Historial y Docs) ---
@login_required
def detalle_paciente(request, id):
    paciente = get_object_or_404(Paciente, pk=id)
    citas = Cita.objects.filter(paciente=paciente)
    documentos = Documento.objects.filter(paciente=paciente)
    
    return render(request, 'miapp/detalle_paciente.html', {
        'paciente': paciente,
        'citas': citas,
        'documentos': documentos
    })

# --- 4. CREAR PACIENTE ---
@login_required
def crear_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Paciente registrado correctamente.')
            return redirect('lista_pacientes')
    else:
        form = PacienteForm()
    
    return render(request, 'miapp/crear_paciente.html', {'form': form})

# --- 5. EDITAR PACIENTE ---
@login_required
def editar_paciente(request, id):
    paciente = get_object_or_404(Paciente, pk=id)
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, '✏️ Datos actualizados correctamente.')
            return redirect('detalle_paciente', id=paciente.id)
    else:
        form = PacienteForm(instance=paciente)
    
    return render(request, 'miapp/crear_paciente.html', {'form': form})

# --- 6. ELIMINAR PACIENTE ---
@login_required
def eliminar_paciente(request, id):
    paciente = get_object_or_404(Paciente, pk=id)
    paciente.delete()
    messages.success(request, '🗑️ Paciente eliminado del sistema.')
    return redirect('lista_pacientes')

# --- 7. AGENDAR CITA ---
@login_required
def crear_cita(request, id_paciente):
    paciente = get_object_or_404(Paciente, pk=id_paciente)
    
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.paciente = paciente
            cita.save()
            messages.success(request, '📅 Cita agendada con éxito.')
            return redirect('detalle_paciente', id=paciente.id)
    else:
        form = CitaForm()
    
    return render(request, 'miapp/crear_cita.html', {
        'form': form, 
        'paciente': paciente
    })

# --- 8. ELIMINAR CITA ---
@login_required
def eliminar_cita(request, id):
    cita = get_object_or_404(Cita, pk=id)
    paciente_id = cita.paciente.id
    cita.delete()
    messages.warning(request, '❌ Cita cancelada/eliminada.')
    return redirect('detalle_paciente', id=paciente_id)

# --- 9. ATENDER CITA (Consulta Médica) ---
@login_required
def atender_cita(request, id_cita):
    cita = get_object_or_404(Cita, pk=id_cita)
    
    if request.method == 'POST':
        form = ConsultaForm(request.POST, instance=cita)
        if form.is_valid():
            consulta = form.save(commit=False)
            consulta.realizada = True
            consulta.save()
            messages.success(request, '👨‍⚕️ Consulta guardada y finalizada correctamente.')
            return redirect('detalle_paciente', id=cita.paciente.id)
    else:
        form = ConsultaForm(instance=cita)
    
    return render(request, 'miapp/atender_cita.html', {
        'form': form,
        'cita': cita
    })

# --- 10. SUBIR DOCUMENTO (Archivos) ---
@login_required
def subir_documento(request, id_paciente):
    paciente = get_object_or_404(Paciente, pk=id_paciente)
    
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES) 
        if form.is_valid():
            doc = form.save(commit=False)
            doc.paciente = paciente
            doc.save()
            messages.success(request, '📂 Archivo subido correctamente.')
            return redirect('detalle_paciente', id=paciente.id)
    else:
        form = DocumentoForm()
    
    return render(request, 'miapp/subir_documento.html', {
        'form': form,
        'paciente': paciente
    })

# --- 11. GENERAR PDF DE CITA (Receta Médica) ---
@login_required
def imprimir_receta(request, id_cita):
    cita = get_object_or_404(Cita, pk=id_cita)
    
    data = {
        'cita': cita,
        'paciente': cita.paciente,
        'doctor': request.user, 
        'fecha_impresion': date.today()
    }
    
    pdf = render_to_pdf('miapp/receta_pdf.html', data)
    
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Receta_{cita.paciente.nombre}_{cita.paciente.apellido}.pdf"
        content = f"inline; filename={filename}"
        response['Content-Disposition'] = content
        return response
        
    return HttpResponse("Error al generar el PDF")

def inicio(request):
    return render(request, 'miapp/inicio.html')