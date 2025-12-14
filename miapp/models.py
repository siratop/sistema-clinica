from django.db import models
from django.contrib.auth.models import User
from datetime import date

# ==========================================
# 1. GESTIÓN DE ROLES (Médicos, Admin, etc.)
# ==========================================
class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class PerfilUsuario(models.Model):
    ROLES = [
        ('medico', 'Médico'),
        ('secretaria', 'Secretaria'),
        ('contador', 'Contador'),
        ('administrador', 'Administrador'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROLES, default='medico')
    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()}"

# ==========================================
# 2. GESTIÓN DE PACIENTES
# ==========================================
class Paciente(models.Model):
    # Enlace con el Usuario de Login (Para que puedan entrar al sistema)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="paciente_perfil")
    
    SEXO_OPCIONES = [('M', 'Masculino'), ('F', 'Femenino')]
    
    # Datos Personales
    cedula = models.CharField(max_length=15, unique=True, verbose_name="Cédula (V-/E-)")
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1, choices=SEXO_OPCIONES)
    
    # Contacto
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    correo = models.EmailField(blank=True, null=True, verbose_name="Correo Electrónico (Opcional)")
    direccion = models.TextField(blank=True)
    
    # Antecedentes Médicos
    alergias = models.TextField(blank=True, verbose_name="Alergias (Escribe 'Ninguna' si no tienes)")
    enfermedades_cronicas = models.TextField(blank=True, verbose_name="Enfermedades Crónicas")
    
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    # Calcular edad automáticamente
    @property
    def edad(self):
        today = date.today()
        if self.fecha_nacimiento:
            return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return 0

# ==========================================
# 3. GESTIÓN DE CITAS MÉDICAS
# ==========================================
class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(User, on_delete=models.CASCADE, related_name='citas_medico')
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.TextField()
    estado = models.CharField(max_length=20, default='pendiente') # pendiente, confirmada, finalizada
    
    # Datos post-consulta
    diagnostico = models.TextField(blank=True, null=True)
    tratamiento = models.TextField(blank=True, null=True)
    realizada = models.BooleanField(default=False)

    def __str__(self):
        return f"Cita: {self.paciente} - {self.fecha}"

class Documento(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='resultados/')
    descripcion = models.CharField(max_length=200)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.descripcion

# ==========================================
# 4. GESTIÓN DE CONTENIDO WEB (CMS)
# ==========================================

# Carrusel de Imágenes (Portada)
class CarruselImagen(models.Model):
    titulo = models.CharField(max_length=100)
    subtitulo = models.CharField(max_length=200, blank=True)
    # CAMBIO IMPORTANTE: ImageField permite subir archivos desde la PC
    imagen = models.ImageField(upload_to='carrusel/', verbose_name="Subir Imagen") 
    orden = models.IntegerField(default=1, help_text="Define el orden (1 sale primero)")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.orden}. {self.titulo}"
    
    class Meta:
        ordering = ['orden'] # Ordena automáticamente por el número

# Preguntas Frecuentes (FAQ)
class PreguntaFrecuente(models.Model):
    pregunta = models.CharField(max_length=255)
    respuesta = models.TextField()
    orden = models.IntegerField(default=1)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.pregunta

    class Meta:
        ordering = ['orden']

# Aviso Importante (Barra amarilla en portada)
class AvisoImportante(models.Model):
    titulo = models.CharField(max_length=100, default="Información Importante")
    mensaje = models.TextField()
    activo = models.BooleanField(default=True, verbose_name="Mostrar en portada")
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo