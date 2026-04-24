from apps.programas.domain.repositories.programa_repository import AbstractProgramaRepository
from apps.programas.domain.entities.programa import ProgramaEntity


class ListProgramasUseCase:
    # Intentionally anemic: filtering logic lives in the repo query.
    def __init__(self, programa_repository: AbstractProgramaRepository):
        self._repo = programa_repository

    def execute(self, filters: dict) -> list[ProgramaEntity]:
        return self._repo.list_public(filters)
