from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Importamos todos los modelos necesarios
from .models import (
    Paciente, Cita, Documento, 
    CarruselImagen, PreguntaFrecuente, AvisoImportante,
    PerfilUsuario, PersonalAutorizado, MovimientoContable, OrdenMedica
)

# ==========================================
# 1. GESTIÓN DE PACIENTES Y CITAS
# ==========================================

class PacienteForm(forms.ModelForm):
    # Campos extra para crear el usuario de Login
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
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'alergias': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Escribe "Ninguna" si no tienes.'}),
            'enfermedades_cronicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ej: Asma, Hipertensión... o "Ninguna".'}),
        }

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

class CitaInvitadoForm(forms.Form):
    # Formulario especial que no guarda usuario, solo datos básicos + cita
    cedula = forms.CharField(label="Cédula", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: V-12345678'}))
    nombre = forms.CharField(label="Nombre", widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellido = forms.CharField(label="Apellido", widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(label="Teléfono", widget=forms.TextInput(attrs={'class': 'form-control'}))
    fecha_nacimiento = forms.DateField(label="Fecha de Nacimiento", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    sexo = forms.ChoiceField(label="Sexo", choices=[('M', 'Masculino'), ('F', 'Femenino')], widget=forms.Select(attrs={'class': 'form-select'}))

    medico = forms.ModelChoiceField(
        queryset=User.objects.filter(perfilusuario__rol='medico'), # Solo mostramos médicos
        label="Médico Especialista", 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fecha = forms.DateField(label="Fecha Deseada", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    hora = forms.TimeField(label="Hora Preferida", widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))
    motivo = forms.CharField(label="Motivo de Consulta", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))

# ==========================================
# 2. ÁREA MÉDICA Y ENFERMERÍA
# ==========================================

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['diagnostico', 'tratamiento', 'realizada']
        widgets = {
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'realizada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['descripcion', 'archivo']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class OrdenMedicaForm(forms.ModelForm):
    class Meta:
        model = OrdenMedica
        fields = ['paciente', 'indicacion']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'indicacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Indique tratamiento o cuidados...'}),
        }

class EjecucionOrdenForm(forms.ModelForm):
    class Meta:
        model = OrdenMedica
        fields = ['ejecutada', 'nota_enfermeria']
        widgets = {
            'ejecutada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'nota_enfermeria': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Observaciones al aplicar...'}),
        }

# ==========================================
# 3. SEGURIDAD Y PERSONAL (LISTA BLANCA)
# ==========================================

class RegistroPersonalForm(forms.ModelForm):
    # Campos para crear el usuario Django
    username = forms.CharField(label="Usuario", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    cedula_identidad = forms.CharField(label="Cédula de Identidad", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: V-12345678'}))

    class Meta:
        model = PerfilUsuario
        fields = ['telefono']

    def clean_cedula_identidad(self):
        cedula = self.cleaned_data.get('cedula_identidad')
        
        # 1. Verificar si la cédula está autorizada por el Admin
        try:
            autorizado = PersonalAutorizado.objects.get(cedula=cedula)
        except PersonalAutorizado.DoesNotExist:
            raise ValidationError("Esta cédula no está autorizada para registrarse como personal. Contacte a Administración.")

        # 2. Verificar si ya se registró
        if autorizado.usado:
            raise ValidationError("Esta cédula ya tiene un usuario registrado en el sistema.")
            
        return cedula

# ==========================================
# 4. CONTABILIDAD (ADMINISTRACIÓN)
# ==========================================

class MovimientoContableForm(forms.ModelForm):
    class Meta:
        model = MovimientoContable
        fields = ['tipo', 'descripcion', 'monto', 'es_divisa', 'tasa_cambio', 'referencia', 'fecha']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Pago Consulta Juan Pérez'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'tasa_cambio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tasa BCV'}),
            'referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nro Ref Bancaria'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'es_divisa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# ==========================================
# 5. GESTIÓN CMS (PÁGINA WEB)
# ==========================================

class CarruselForm(forms.ModelForm):
    class Meta:
        model = CarruselImagen
        fields = ['orden', 'titulo', 'subtitulo', 'imagen', 'overlay', 'activo']
        widgets = {
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'subtitulo': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'overlay': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'imagen': '<strong class="text-danger">Importante:</strong> Se recomiendan imágenes horizontales de 1920x600 px.',
            'overlay': 'Oscurece la imagen para que el texto sea legible.',
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