from apps.postulaciones.domain.repositories.postulacion_repository import AbstractPostulacionRepository
from apps.postulaciones.domain.entities.postulacion import PostulacionEntity
from apps.postulaciones.domain.exceptions import PostulacionNotFound


class DjangoPostulacionRepository(AbstractPostulacionRepository):
    def create(self, estudiante_id, programa_id, mensaje):
        from apps.postulaciones.infrastructure.models import Postulacion
        from apps.catalogos.infrastructure.models import EstadoPostulacion

        estado_guardado = EstadoPostulacion.objects.get(slug='guardado')
        postulacion = Postulacion.objects.create(
            estudiante_id=estudiante_id,
            programa_id=programa_id,
            estado=estado_guardado,
            mensaje=mensaje,
        )
        return self._to_entity(postulacion)

    def list_by_estudiante(self, estudiante_id):
        from apps.postulaciones.infrastructure.models import Postulacion
        qs = Postulacion.objects.select_related('estado', 'programa').filter(estudiante_id=estudiante_id)
        return [self._to_entity(p) for p in qs]

    def get_by_id(self, postulacion_id):
        from apps.postulaciones.infrastructure.models import Postulacion
        try:
            p = Postulacion.objects.select_related('estado').get(id=postulacion_id)
        except Postulacion.DoesNotExist:
            raise PostulacionNotFound(f"Postulación {postulacion_id} no encontrada.")
        return self._to_entity(p)

    def exists(self, estudiante_id, programa_id):
        from apps.postulaciones.infrastructure.models import Postulacion
        return Postulacion.objects.filter(estudiante_id=estudiante_id, programa_id=programa_id).exists()

    def _to_entity(self, p) -> PostulacionEntity:
        return PostulacionEntity(
            id=p.id,
            estudiante_id=p.estudiante_id,
            programa_id=p.programa_id,
            estado_slug=p.estado.slug,
            mensaje=p.mensaje,
            fecha_postulacion=p.fecha_postulacion,
        )
