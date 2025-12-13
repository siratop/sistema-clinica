
from django.contrib import admin
from .models import Paciente  # Importamos tu modelo
from .models import Paciente, Cita

# Registramos el modelo para verlo en el admin
admin.site.register(Paciente)
admin.site.register(Cita)
