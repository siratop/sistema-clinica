from django.db import models
from django.contrib.auth.models import User
from datetime import date

# ==========================================
# 1. SEGURIDAD Y ROLES (LISTA BLANCA)
# ==========================================

# El Admin debe llenar esto PRIMERO. Si la cédula no está aquí, no se pueden registrar.
class PersonalAutorizado(models.Model):
    ROLES = [
        ('medico', 'Médico'),
        ('secretaria', 'Secretaria'),
        ('contador', 'Administrativo/Contable'),
        ('enfermera', 'Enfermera'),
        ('gerente', 'Jefe de Clínica'),
    ]
    cedula = models.CharField(max_length=15, unique=True, verbose_name="Cédula Autorizada")
    nombre_completo = models.CharField(max_length=150)
    rol = models.CharField(max_length=20, choices=ROLES)
    especialidad_asignada = models.ForeignKey('Especialidad', on_delete=models.SET_NULL, null=True, blank=True, help_text="Solo para médicos")
    usado = models.BooleanField(default=False, help_text="Marcará si ya se registró el usuario")

    def __str__(self):
        return f"{self.cedula} - {self.nombre_completo} ({self.get_rol_display()})"

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nombre

class PerfilUsuario(models.Model):
    # Heredamos los roles del modelo de autorización
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula = models.CharField(max_length=15, unique=True, null=True) # Vinculo con la identidad real
    rol = models.CharField(max_length=20, choices=PersonalAutorizado.ROLES)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.rol}"

# ==========================================
# 2. MÓDULO ADMINISTRATIVO Y CONTABLE
# ==========================================
class MovimientoContable(models.Model):
    TIPOS = [
        ('ingreso', 'Ingreso (Consulta/Cirugía)'),
        ('egreso', 'Egreso (Gasto Operativo)'),
        ('nomina', 'Pago de Nómina'),
        ('impuesto', 'Pago de Impuestos (SENIAT/Alcaldía)'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPOS)
    monto = models.DecimalField(max_digits=12, decimal_places=2) # Soporta bolívares/dólares
    descripcion = models.CharField(max_length=255, verbose_name="Concepto")
    fecha = models.DateField(default=date.today)
    referencia = models.CharField(max_length=50, blank=True, help_text="Nro de Factura o Referencia Bancaria")
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) # Quién registró el movimiento
    
    # Campo para control venezolano
    es_divisa = models.BooleanField(default=False, verbose_name="¿Es en Dólares?")
    tasa_cambio = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Tasa BCV del día")

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.monto}"

# ==========================================
# 3. MÓDULO ENFERMERÍA Y ÓRDENES
# ==========================================
class OrdenMedica(models.Model):
    """ Comunicación: El Médico escribe -> Enfermería lee/ejecuta """
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE)
    medico = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ordenes_creadas")
    indicacion = models.TextField(help_text="Tratamiento, medicina a suministrar o cuidados.")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Respuesta de Enfermería
    ejecutada = models.BooleanField(default=False)
    nota_enfermeria = models.TextField(blank=True, help_text="Observaciones de la enfermera al aplicar")
    enfermera_responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="ordenes_atendidas")
    fecha_ejecucion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Orden para {self.paciente} - Dr. {self.medico.last_name}"

# ==========================================
# 4. GESTIÓN DE PACIENTES Y CITAS (EXISTENTE)
# ==========================================
class Paciente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="paciente_perfil")
    cedula = models.CharField(max_length=15, unique=True, verbose_name="Cédula")
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino')])
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True)
    alergias = models.TextField(blank=True, default="Ninguna")
    enfermedades_cronicas = models.TextField(blank=True, default="Ninguna")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    @property
    def edad(self):
        today = date.today()
        if self.fecha_nacimiento:
            return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return 0

class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'perfilusuario__rol': 'medico'})
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.TextField()
    estado = models.CharField(max_length=20, default='pendiente')
    diagnostico = models.TextField(blank=True, null=True)
    tratamiento = models.TextField(blank=True, null=True)
    realizada = models.BooleanField(default=False)

    def __str__(self):
        return f"Cita {self.paciente} con Dr. {self.medico.last_name}"

class Documento(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='resultados/')
    descripcion = models.CharField(max_length=200)
    fecha_subida = models.DateTimeField(auto_now_add=True)

# ==========================================
# 5. CMS (EXISTENTE)
# ==========================================
class CarruselImagen(models.Model):
    OPACIDAD_CHOICES = [('0', '0%'), ('0.3', '30%'), ('0.5', '50%'), ('0.7', '70%')]
    titulo = models.CharField(max_length=100)
    subtitulo = models.CharField(max_length=200, blank=True)
    imagen = models.ImageField(upload_to='carrusel/')
    overlay = models.CharField(max_length=5, choices=OPACIDAD_CHOICES, default='0.5')
    orden = models.IntegerField(default=1)
    activo = models.BooleanField(default=True)
    class Meta: ordering = ['orden']

class PreguntaFrecuente(models.Model):
    pregunta = models.CharField(max_length=255)
    respuesta = models.TextField()
    orden = models.IntegerField(default=1)
    activa = models.BooleanField(default=True)
    class Meta: ordering = ['orden']

class AvisoImportante(models.Model):
    titulo = models.CharField(max_length=100, default="Información Importante")
    mensaje = models.TextField()
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)