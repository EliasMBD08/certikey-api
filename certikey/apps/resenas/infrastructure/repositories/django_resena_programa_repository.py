from apps.resenas.domain.repositories.resena_programa_repository import AbstractResenaProgramaRepository
from apps.resenas.domain.entities.resena_programa import ResenaProgramaEntity


class DjangoResenaProgramaRepository(AbstractResenaProgramaRepository):
    def create(self, estudiante_id, programa_id, calificacion, comentario):
        from apps.resenas.infrastructure.models import ResenaPrograma
        r = ResenaPrograma.objects.create(
            estudiante_id=estudiante_id,
            programa_id=programa_id,
            calificacion=calificacion,
            comentario=comentario,
        )
        return self._to_entity(r)

    def list_by_programa(self, programa_id):
        from apps.resenas.infrastructure.models import ResenaPrograma
        qs = ResenaPrograma.objects.filter(programa_id=programa_id)
        return [self._to_entity(r) for r in qs]

    def exists(self, estudiante_id, programa_id):
        from apps.resenas.infrastructure.models import ResenaPrograma
        return ResenaPrograma.objects.filter(
            estudiante_id=estudiante_id,
            programa_id=programa_id,
        ).exists()

    def _to_entity(self, r) -> ResenaProgramaEntity:
        return ResenaProgramaEntity(
            id=r.id,
            estudiante_id=r.estudiante_id,
            programa_id=r.programa_id,
            calificacion=r.calificacion,
            comentario=r.comentario,
            fecha_creacion=r.fecha_creacion,
            activo=r.activo,
        )
