from django.contrib import admin
from apps.catalogos.infrastructure.models import (
    Pais, Ciudad, Moneda, Rol, TipoPrograma, Modalidad,
    NivelAcademico, EstadoPrograma, EstadoVerificacion,
    Categoria, Tag,
)

admin.site.register(Pais)
admin.site.register(Ciudad)
admin.site.register(Moneda)
admin.site.register(Rol)
admin.site.register(TipoPrograma)
admin.site.register(Modalidad)
admin.site.register(NivelAcademico)
admin.site.register(EstadoPrograma)
admin.site.register(EstadoVerificacion)
admin.site.register(Categoria)
admin.site.register(Tag)
