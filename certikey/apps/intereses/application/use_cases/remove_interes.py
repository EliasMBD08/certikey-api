from apps.intereses.domain.repositories.interes_repository import AbstractInteresRepository
from apps.intereses.domain.exceptions import InteresNotFound


class RemoveInteresUseCase:
    def __init__(self, repository: AbstractInteresRepository):
        self._repo = repository

    def execute(self, estudiante_id: int, programa_id: int) -> None:
        existing = self._repo.get(estudiante_id, programa_id)
        if not existing or not existing.activo:
            raise InteresNotFound("No tienes este programa guardado.")
        self._repo.remove(estudiante_id, programa_id)
