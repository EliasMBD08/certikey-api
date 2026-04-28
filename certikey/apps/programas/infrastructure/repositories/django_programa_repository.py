from apps.programas.domain.repositories.programa_repository import AbstractProgramaRepository
from apps.programas.domain.entities.programa import ProgramaEntity
from apps.programas.domain.exceptions import ProgramaNotFound


class DjangoProgramaRepository(AbstractProgramaRepository):
    def create(self, certificadora_id, **kwargs):
        from apps.programas.infrastructure.models import Programa
        from apps.catalogos.infrastructure.models import EstadoPrograma

        tags_ids = kwargs.pop('tags_ids', [])
        categorias_ids = kwargs.pop('categorias_ids', [])
        estado_borrador = EstadoPrograma.objects.get(slug='borrador')

        programa = Programa.objects.create(
            certificadora_id=certificadora_id,
            estado=estado_borrador,
            **kwargs,
        )
        if tags_ids:
            programa.tags.set(tags_ids)
        if categorias_ids:
            programa.categorias.set(categorias_ids)
        return self._to_entity(programa)

    def get_by_id(self, programa_id):
        from apps.programas.infrastructure.models import Programa
        try:
            p = Programa.objects.select_related('estado').prefetch_related('tags', 'categorias').get(id=programa_id)
        except Programa.DoesNotExist:
            raise ProgramaNotFound(f"Programa {programa_id} no encontrado.")
        return self._to_entity(p)

    def get_by_slug(self, slug):
        from apps.programas.infrastructure.models import Programa
        try:
            p = Programa.objects.select_related('estado').prefetch_related('tags', 'categorias').get(slug=slug)
        except Programa.DoesNotExist:
            raise ProgramaNotFound(f"Programa '{slug}' no encontrado.")
        return self._to_entity(p)

    def list_public(self, filters):
        from apps.programas.infrastructure.models import Programa
        qs = Programa.objects.filter(
            estado__es_visible_publico=True
        ).select_related('estado', 'tipo', 'modalidad', 'certificadora__usuario').prefetch_related('tags', 'categorias')

        if filters.get('categorias'):
            qs = qs.filter(categorias__id__in=filters['categorias']).distinct()
        if filters.get('tipo'):
            qs = qs.filter(tipo_id=filters['tipo'])
        if filters.get('modalidad'):
            qs = qs.filter(modalidad_id=filters['modalidad'])
        if filters.get('nivel'):
            qs = qs.filter(nivel_id=filters['nivel'])
        if filters.get('es_gratuito') is not None:
            qs = qs.filter(es_gratuito=filters['es_gratuito'])
        if filters.get('inscripciones_abiertas') is not None:
            qs = qs.filter(inscripciones_abiertas=filters['inscripciones_abiertas'])
        if filters.get('precio_max') is not None:
            qs = qs.filter(precio__lte=filters['precio_max'])
        if filters.get('search'):
            qs = qs.filter(titulo__icontains=filters['search'])

        return [self._to_entity(p) for p in qs]

    def list_by_certificadora(self, certificadora_id):
        from apps.programas.infrastructure.models import Programa
        qs = Programa.objects.filter(certificadora_id=certificadora_id).select_related('estado').prefetch_related('tags', 'categorias')
        return [self._to_entity(p) for p in qs]

    def update(self, programa_id, **kwargs):
        from apps.programas.infrastructure.models import Programa
        tags_ids = kwargs.pop('tags_ids', None)
        categorias_ids = kwargs.pop('categorias_ids', None)
        Programa.objects.filter(id=programa_id).update(**kwargs)
        programa = Programa.objects.select_related('estado').prefetch_related('tags', 'categorias').get(id=programa_id)
        if tags_ids is not None:
            programa.tags.set(tags_ids)
        if categorias_ids is not None:
            programa.categorias.set(categorias_ids)
        return self._to_entity(programa)

    def update_estado(self, programa_id, estado_slug):
        from apps.programas.infrastructure.models import Programa
        from apps.catalogos.infrastructure.models import EstadoPrograma
        estado = EstadoPrograma.objects.get(slug=estado_slug)
        Programa.objects.filter(id=programa_id).update(estado=estado)
        programa = Programa.objects.select_related('estado').prefetch_related('tags', 'categorias').get(id=programa_id)
        return self._to_entity(programa)

    def _to_entity(self, p) -> ProgramaEntity:
        return ProgramaEntity(
            id=p.id,
            titulo=p.titulo,
            slug=p.slug,
            descripcion_corta=p.descripcion_corta,
            descripcion=p.descripcion,
            certificadora_id=p.certificadora_id,
            categorias_ids=list(p.categorias.values_list('id', flat=True)),
            tipo_id=p.tipo_id,
            modalidad_id=p.modalidad_id,
            nivel_id=p.nivel_id,
            estado_slug=p.estado.slug,
            es_gratuito=p.es_gratuito,
            precio=p.precio,
            moneda_id=p.moneda_id,
            duracion_horas=p.duracion_horas,
            duracion_semanas=p.duracion_semanas,
            otorga_certificado=p.otorga_certificado,
            descripcion_certificado=p.descripcion_certificado,
            fecha_inicio=p.fecha_inicio,
            fecha_fin=p.fecha_fin,
            inscripciones_abiertas=p.inscripciones_abiertas,
            url_inscripcion=p.url_inscripcion,
            fecha_creacion=p.fecha_creacion,
            tags_ids=list(p.tags.values_list('id', flat=True)),
        )
