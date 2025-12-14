from django.contrib import admin
from .models import PerfilUsuario, Paciente, Cita, Especialidad, CarruselImagen, PreguntaFrecuente

# Esto permite ver los datos en el panel /admin
admin.site.register(PerfilUsuario)
admin.site.register(Paciente)
admin.site.register(Cita)
admin.site.register(Especialidad)
admin.site.register(CarruselImagen)
admin.site.register(PreguntaFrecuente)
