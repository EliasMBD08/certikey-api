from apps.resenas.domain.repositories.resena_programa_repository import AbstractResenaProgramaRepository
from apps.resenas.domain.entities.resena_programa import ResenaProgramaEntity


class ListResenasProgramaUseCase:
    def __init__(self, repository: AbstractResenaProgramaRepository):
        self._repo = repository

    def execute(self, programa_id: int) -> list[ResenaProgramaEntity]:
        return self._repo.list_by_programa(programa_id)
