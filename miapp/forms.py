from django import forms
# CORRECCIÓN: Quitamos ConsultaForm de esta lista de importación
from .models import Paciente, Cita, Documento, CarruselImagen, PreguntaFrecuente, AvisoImportante

# --- FORMULARIO PACIENTE ---
class PacienteForm(forms.ModelForm):
    # Campos EXTRA para crear el usuario
    username = forms.CharField(label="Nombre de Usuario", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: mariaperez2025'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Crea una contraseña segura'}))

    class Meta:
        model = Paciente
        exclude = ['usuario', 'fecha_registro']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: V-12345678'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ayuda a recuperar tu clave (Opcional)'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'alergias': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Escribe "Ninguna conocida" si no tienes.'}),
            'enfermedades_cronicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ej: Asma, Hipertensión... o "Ninguna conocida".'}),
        }

# --- FORMULARIO PARA CREAR CITAS (Paciente/Secretaria) ---
class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['medico', 'fecha', 'hora', 'motivo']
        widgets = {
            'medico': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

# --- FORMULARIO PARA LA CONSULTA MÉDICA (Diagnóstico) ---
class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['diagnostico', 'tratamiento', 'realizada']
        widgets = {
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'realizada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# --- FORMULARIO DOCUMENTOS ---
class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['descripcion', 'archivo']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
        }

# ==========================================
# FORMULARIOS CMS (ADMINISTRADOR)
# ==========================================

class CarruselForm(forms.ModelForm):
    class Meta:
        model = CarruselImagen
        fields = ['orden', 'titulo', 'subtitulo', 'imagen', 'activo']
        widgets = {
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'subtitulo': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PreguntaForm(forms.ModelForm):
    class Meta:
        model = PreguntaFrecuente
        fields = ['orden', 'pregunta', 'respuesta', 'activa']
        widgets = {
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
            'pregunta': forms.TextInput(attrs={'class': 'form-control'}),
            'respuesta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AvisoForm(forms.ModelForm):
    class Meta:
        model = AvisoImportante
        fields = ['titulo', 'mensaje', 'activo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }