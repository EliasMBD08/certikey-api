from django.contrib import admin
from apps.postulaciones.infrastructure.models import Postulacion


@admin.register(Postulacion)
class PostulacionAdmin(admin.ModelAdmin):
    list_display = ['estudiante', 'programa', 'estado', 'fecha_postulacion']
    list_filter = ['estado']
    raw_id_fields = ['estudiante', 'programa']
