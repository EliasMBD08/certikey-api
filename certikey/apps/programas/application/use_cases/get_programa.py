from apps.programas.domain.repositories.programa_repository import AbstractProgramaRepository
from apps.programas.domain.entities.programa import ProgramaEntity
from apps.programas.domain.exceptions import ProgramaNotFound


class GetProgramaUseCase:
    def __init__(self, programa_repository: AbstractProgramaRepository):
        self._repo = programa_repository

    def execute(self, programa_id: int) -> ProgramaEntity:
        return self._repo.get_by_id(programa_id)
