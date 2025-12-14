from django.db import models
from django.contrib.auth.models import User
from datetime import date

# 1. Especialidades Médicas
class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Especialidad")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Especialidades"

# 2. Perfil Extendido (Médico/Secretaria)
class PerfilUsuario(models.Model):
    ROLES = [
        ('medico', 'Médico'),
        ('secretaria', 'Secretaria/Recepción'),
        ('administrador', 'Administrador'),
        ('contador', 'Contador'),
        ('paciente', 'Paciente'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROLES, default='paciente')
    cedula_identidad = models.CharField(max_length=15, blank=True, null=True, verbose_name="C.I.")
    telefono = models.CharField(max_length=20, blank=True)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()}"

# 3. Paciente (Datos Reales Venezolanos)
class Paciente(models.Model):
    SEXO_OPCIONES = [('M', 'Masculino'), ('F', 'Femenino')]
    
    cedula = models.CharField(max_length=15, unique=True, verbose_name="Cédula (V-/E-)")
    numero_historia = models.CharField(max_length=20, unique=True, verbose_name="Nº Historia")
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1, choices=SEXO_OPCIONES)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True)
    
    # Antecedentes
    tipo_sangre = models.CharField(max_length=5, blank=True)
    alergias = models.TextField(blank=True)
    enfermedades_cronicas = models.TextField(blank=True)
    
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def edad(self):
        today = date.today()
        if self.fecha_nacimiento:
            return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return 0

# 4. Citas
class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(User, on_delete=models.CASCADE, related_name="citas_medico")
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.TextField()
    realizada = models.BooleanField(default=False)
    
    # Resultados Médicos
    diagnostico = models.TextField(blank=True)
    tratamiento = models.TextField(blank=True)
    sintomas = models.TextField(blank=True, verbose_name="Signos Vitales / Observaciones")

    def __str__(self):
        return f"Cita: {self.paciente} - {self.fecha}"

# 5. Documentos
class Documento(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='documentos/')
    descripcion = models.CharField(max_length=200)
    fecha_subida = models.DateField(auto_now_add=True)