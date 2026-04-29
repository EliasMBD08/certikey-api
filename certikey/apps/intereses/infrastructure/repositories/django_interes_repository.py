from apps.intereses.domain.repositories.interes_repository import AbstractInteresRepository
from apps.intereses.domain.entities.interes import InteresEntity


class DjangoInteresRepository(AbstractInteresRepository):
    def save(self, estudiante_id, programa_id):
        from apps.intereses.infrastructure.models import Interes
        # Si existe pero estaba inactivo (fue quitado antes), lo reactiva
        obj, created = Interes.todos.get_or_create(
            estudiante_id=estudiante_id,
            programa_id=programa_id,
        )
        if not created and not obj.activo:
            obj.restore()
        return self._to_entity(obj)

    def remove(self, estudiante_id, programa_id):
        from apps.intereses.infrastructure.models import Interes
        Interes.objects.filter(
            estudiante_id=estudiante_id,
            programa_id=programa_id,
        ).first().soft_delete()

    def list_by_estudiante(self, estudiante_id):
        from apps.intereses.infrastructure.models import Interes
        qs = Interes.objects.filter(estudiante_id=estudiante_id)
        return [self._to_entity(i) for i in qs]

    def get(self, estudiante_id, programa_id):
        from apps.intereses.infrastructure.models import Interes
        try:
            obj = Interes.todos.get(
                estudiante_id=estudiante_id,
                programa_id=programa_id,
            )
            return self._to_entity(obj)
        except Interes.DoesNotExist:
            return None

    def _to_entity(self, obj) -> InteresEntity:
        return InteresEntity(
            id=obj.id,
            estudiante_id=obj.estudiante_id,
            programa_id=obj.programa_id,
            fecha_creacion=obj.fecha_creacion,
            activo=obj.activo,
        )
