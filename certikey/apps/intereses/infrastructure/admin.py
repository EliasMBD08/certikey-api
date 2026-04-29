from django.contrib import admin

from apps.intereses.infrastructure.models import Interes


@admin.register(Interes)
class InteresAdmin(admin.ModelAdmin):
    list_display = ('id', 'estudiante', 'programa', 'fecha_creacion', 'activo')
    list_filter = ('activo',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
