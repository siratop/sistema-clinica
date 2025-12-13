from django.db import models

# 1. Modelo de Paciente
class Paciente(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    dni = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=20)
    creado_el = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# 2. Modelo de Cita (Incluye datos médicos)
class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.TextField()
    realizada = models.BooleanField(default=False)
    
    # Campos Médicos
    sintomas = models.TextField(blank=True, null=True, help_text="Descripción de lo que siente el paciente")
    diagnostico = models.TextField(blank=True, null=True, help_text="Conclusión médica")
    tratamiento = models.TextField(blank=True, null=True, help_text="Medicamentos y recomendaciones")

    def __str__(self):
        return f"Cita de {self.paciente} - {self.fecha}"

# 3. Modelo de Documento (Archivos adjuntos)
class Documento(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100, verbose_name="Título del archivo")
    archivo = models.FileField(upload_to='documentos/') 
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.paciente}"
