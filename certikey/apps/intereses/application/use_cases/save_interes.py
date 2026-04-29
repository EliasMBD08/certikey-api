from dataclasses import dataclass

from apps.intereses.domain.repositories.interes_repository import AbstractInteresRepository
from apps.intereses.domain.entities.interes import InteresEntity
from apps.intereses.domain.exceptions import InteresYaExiste


@dataclass
class SaveInteresInput:
    estudiante_id: int
    programa_id: int


class SaveInteresUseCase:
    def __init__(self, repository: AbstractInteresRepository):
        self._repo = repository

    def execute(self, input_dto: SaveInteresInput) -> InteresEntity:
        existing = self._repo.get(input_dto.estudiante_id, input_dto.programa_id)
        if existing and existing.activo:
            raise InteresYaExiste("Ya tienes este programa guardado.")
        return self._repo.save(input_dto.estudiante_id, input_dto.programa_id)
