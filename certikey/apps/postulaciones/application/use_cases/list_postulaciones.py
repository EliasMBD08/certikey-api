from apps.postulaciones.domain.repositories.postulacion_repository import AbstractPostulacionRepository
from apps.postulaciones.domain.entities.postulacion import PostulacionEntity


class ListPostulacionesUseCase:
    def __init__(self, postulacion_repository: AbstractPostulacionRepository):
        self._repo = postulacion_repository

    def execute(self, estudiante_id: int) -> list[PostulacionEntity]:
        return self._repo.list_by_estudiante(estudiante_id)
