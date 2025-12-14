from django import forms
from .models import Paciente, Cita, Documento

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: V-12345678'}),
            'numero_historia': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tipo_sangre': forms.TextInput(attrs={'class': 'form-control'}),
            'alergias': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'enfermedades_cronicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['medico', 'fecha', 'hora', 'motivo']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'medico': forms.Select(attrs={'class': 'form-select'}),
        }

# Este formulario NO se importa de models, se define AQUÍ
class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['diagnostico', 'tratamiento', 'sintomas']
        widgets = {
            'diagnostico': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'tratamiento': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'sintomas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Peso, Tensión, Temperatura...'}),
        }

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['archivo', 'descripcion']
        widgets = {
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
        }