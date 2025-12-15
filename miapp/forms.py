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
        fields = ['orden', 'titulo', 'subtitulo', 'imagen', 'overlay', 'activo'] # Agregamos 'overlay'
        widgets = {
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'subtitulo': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'overlay': forms.Select(attrs={'class': 'form-select'}), # Selector desplegable
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        # AQUÍ PONEMOS EL CONSEJO DE LAS MEDIDAS
        help_texts = {
            'imagen': '<strong class="text-danger">Importante:</strong> Para que se vea perfecto, usa imágenes horizontales de <strong>1920 x 600 pixeles</strong> (o formato 16:9).',
            'overlay': 'Elige qué tan oscura quieres la imagen para que el texto blanco se pueda leer.',
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

    # --- FORMULARIO CITA RÁPIDA (INVITADO) ---
from django.contrib.auth.models import User # Asegúrate de importar User

class CitaInvitadoForm(forms.Form):
    # 1. Datos del Paciente (Para identificarlo)
    cedula = forms.CharField(label="Cédula", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: V-12345678'}))
    nombre = forms.CharField(label="Nombre", widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellido = forms.CharField(label="Apellido", widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(label="Teléfono", widget=forms.TextInput(attrs={'class': 'form-control'}))
    fecha_nacimiento = forms.DateField(label="Fecha de Nacimiento", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    sexo = forms.ChoiceField(label="Sexo", choices=[('M', 'Masculino'), ('F', 'Femenino')], widget=forms.Select(attrs={'class': 'form-select'}))

    # 2. Datos de la Cita
    medico = forms.ModelChoiceField(
        queryset=User.objects.filter(perfilusuario__rol='medico'), # Solo mostramos doctores
        label="Médico Especialista", 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fecha = forms.DateField(label="Fecha Deseada", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    hora = forms.TimeField(label="Hora Preferida", widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))
    motivo = forms.CharField(label="Motivo de Consulta", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))    