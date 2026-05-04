from django.db import transaction, IntegrityError

from apps.resenas.domain.repositories.resena_certificadora_repository import AbstractResenaCertificadoraRepository
from apps.resenas.domain.entities.resena_certificadora import ResenaCertificadoraEntity
from apps.resenas.domain.exceptions import ResenaYaExiste


class DjangoResenaCertificadoraRepository(AbstractResenaCertificadoraRepository):
    @transaction.atomic
    def create(self, estudiante_id, certificadora_id, calificacion, comentario):
        from apps.resenas.infrastructure.models import ResenaCertificadora
        try:
            r = ResenaCertificadora.objects.create(
                estudiante_id=estudiante_id,
                certificadora_id=certificadora_id,
                calificacion=calificacion,
                comentario=comentario,
            )
        except IntegrityError:
            raise ResenaYaExiste("Ya tienes una reseña para esta certificadora.")
        return self._to_entity(r)

    def list_by_certificadora(self, certificadora_id):
        from apps.resenas.infrastructure.models import ResenaCertificadora
        qs = ResenaCertificadora.objects.filter(certificadora_id=certificadora_id)
        return [self._to_entity(r) for r in qs]

    def exists(self, estudiante_id, certificadora_id):
        from apps.resenas.infrastructure.models import ResenaCertificadora
        return ResenaCertificadora.objects.filter(
            estudiante_id=estudiante_id,
            certificadora_id=certificadora_id,
        ).exists()

    def _to_entity(self, r) -> ResenaCertificadoraEntity:
        return ResenaCertificadoraEntity(
            id=r.id,
            estudiante_id=r.estudiante_id,
            certificadora_id=r.certificadora_id,
            calificacion=r.calificacion,
            comentario=r.comentario,
            fecha_creacion=r.fecha_creacion,
            activo=r.activo,
        )
