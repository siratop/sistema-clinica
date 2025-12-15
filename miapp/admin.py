from django.contrib import admin
from .models import (
    Paciente, 
    Cita, 
    Documento, 
    PerfilUsuario, 
    CarruselImagen, 
    PreguntaFrecuente, 
    AvisoImportante,
    PersonalAutorizado, 
    MovimientoContable, 
    OrdenMedica, 
    Especialidad
)

# ==========================================
# 1. SEGURIDAD Y ROLES (LISTA BLANCA)
# ==========================================
class PersonalAutorizadoAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre_completo', 'rol', 'especialidad_asignada', 'usado')
    list_filter = ('rol', 'usado')
    search_fields = ('cedula', 'nombre_completo')
    ordering = ('nombre_completo',)
    list_per_page = 20

class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cedula', 'rol', 'especialidad', 'telefono')
    list_filter = ('rol', 'especialidad')
    search_fields = ('cedula', 'usuario__username', 'usuario__first_name')

# ==========================================
# 2. CONTABILIDAD
# ==========================================
class MovimientoContableAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tipo', 'descripcion', 'monto', 'es_divisa', 'responsable')
    list_filter = ('tipo', 'fecha', 'es_divisa')
    search_fields = ('descripcion', 'referencia')
    date_hierarchy = 'fecha'
    list_editable = ('tipo',) # Esto funciona porque 'fecha' es el link por defecto (el primero)

# ==========================================
# 3. GESTIÓN MÉDICA
# ==========================================
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre', 'apellido', 'telefono', 'fecha_registro')
    search_fields = ('cedula', 'nombre', 'apellido')
    list_display_links = ('cedula', 'nombre')

class CitaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora', 'paciente', 'medico', 'estado', 'realizada')
    list_filter = ('fecha', 'estado', 'medico', 'realizada')
    search_fields = ('paciente__nombre', 'paciente__cedula', 'medico__username')
    date_hierarchy = 'fecha'

class OrdenMedicaAdmin(admin.ModelAdmin):
    list_display = ('fecha_creacion', 'paciente', 'medico', 'ejecutada', 'enfermera_responsable')
    list_filter = ('ejecutada', 'fecha_creacion')

# ==========================================
# 4. CMS (WEB) - CORREGIDO AQUÍ
# ==========================================
class CarruselAdmin(admin.ModelAdmin):
    list_display = ('orden', 'titulo', 'activo')
    list_editable = ('orden', 'activo') 
    # SOLUCIÓN: Hacemos que 'titulo' sea el link, liberando a 'orden' para editarse
    list_display_links = ('titulo',) 
    ordering = ('orden',)

class PreguntaAdmin(admin.ModelAdmin):
    list_display = ('orden', 'pregunta', 'activa')
    list_editable = ('orden', 'activa')
    # SOLUCIÓN: Hacemos que 'pregunta' sea el link
    list_display_links = ('pregunta',)
    ordering = ('orden',)

# ==========================================
# REGISTRO DE MODELOS
# ==========================================
admin.site.register(PersonalAutorizado, PersonalAutorizadoAdmin)
admin.site.register(PerfilUsuario, PerfilUsuarioAdmin)
admin.site.register(MovimientoContable, MovimientoContableAdmin)
admin.site.register(Paciente, PacienteAdmin)
admin.site.register(Cita, CitaAdmin)
admin.site.register(OrdenMedica, OrdenMedicaAdmin)
admin.site.register(Especialidad)
admin.site.register(Documento)
admin.site.register(CarruselImagen, CarruselAdmin)
admin.site.register(PreguntaFrecuente, PreguntaAdmin)
admin.site.register(AvisoImportante)