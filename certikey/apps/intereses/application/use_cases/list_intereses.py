from apps.intereses.domain.repositories.interes_repository import AbstractInteresRepository
from apps.intereses.domain.entities.interes import InteresEntity


class ListInteresesUseCase:
    def __init__(self, repository: AbstractInteresRepository):
        self._repo = repository

    def execute(self, estudiante_id: int) -> list[InteresEntity]:
        return self._repo.list_by_estudiante(estudiante_id)
