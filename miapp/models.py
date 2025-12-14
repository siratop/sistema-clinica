from django.db import models
from django.contrib.auth.models import User
from datetime import date

# --- 1. MODELO PARA ESPECIALIDADES MÉDICAS ---
class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Especialidad")
    descripcion = models.TextField(blank=True, verbose_name="Descripción (Opcional)")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Especialidades"

# --- 2. EXTENSIÓN DEL USUARIO (PERFIL MÉDICO/PERSONAL) ---
# Esto nos permitirá saber si un usuario es Doctor, Secretaria, etc.
class PerfilUsuario(models.Model):
    ROLES = [
        ('medico', 'Médico'),
        ('secretaria', 'Secretaria/Recepción'),
        ('administrador', 'Administrador'),
        ('contador', 'Contador'),
        ('paciente', 'Paciente (Usuario Web)'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROLES, default='paciente')
    cedula_identidad = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name="Cédula (C.I.)")
    telefono = models.CharField(max_length=20, blank=True)
    # Solo para médicos:
    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True, blank=True)
    codigo_colegio_medicos = models.CharField(max_length=20, blank=True, verbose_name="Cód. Colegio Médicos")

    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()}"

# --- 3. MODELO DE PACIENTE (RENOVADO) ---
class Paciente(models.Model):
    SEXO_OPCIONES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    
    # Datos Personales
    cedula = models.CharField(max_length=15, unique=True, verbose_name="Cédula (V- / E-)")
    numero_historia = models.CharField(max_length=20, unique=True, verbose_name="Nº Historia Clínica")
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    sexo = models.CharField(max_length=1, choices=SEXO_OPCIONES)
    
    # Contacto
    telefono = models.CharField(max_length=20, verbose_name="Teléfono Celular")
    correo = models.EmailField(blank=True, null=True)
    direccion = models.TextField(verbose_name="Dirección de Habitación")
    
    # Antecedentes Médicos (Resumen)
    tipo_sangre = models.CharField(max_length=5, blank=True, verbose_name="Tipo de Sangre")
    alergias = models.TextField(blank=True, verbose_name="Alergias Conocidas")
    enfermedades_cronicas = models.TextField(blank=True, verbose_name="Enfermedades Crónicas")
    
    # Auditoría
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.cedula})"

    # Cálculo automático de la edad
    @property
    def edad(self):
        today = date.today()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))

# --- 4. MODELO DE CITA (ACTUALIZADO) ---
class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(User, on_delete=models.CASCADE, related_name="citas_como_medico", verbose_name="Médico Tratante")
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.TextField()
    realizada = models.BooleanField(default=False)
    
    # Datos Médicos (Post-Consulta)
    diagnostico = models.TextField(blank=True)
    tratamiento = models.TextField(blank=True)
    sintomas = models.TextField(blank=True, verbose_name="Observaciones / Signos Vitales")

    def __str__(self):
        return f"Cita: {self.paciente} - {self.fecha}"

# --- 5. DOCUMENTOS (Igual que antes) ---
class Documento(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='documentos_pacientes/')
    descripcion = models.CharField(max_length=200)
    fecha_subida = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.descripcion