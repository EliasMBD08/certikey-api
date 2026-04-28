from dataclasses import dataclass

from apps.resenas.domain.repositories.resena_programa_repository import AbstractResenaProgramaRepository
from apps.resenas.domain.entities.resena_programa import ResenaProgramaEntity
from apps.resenas.domain.exceptions import ResenaYaExiste, CalificacionInvalida


@dataclass
class CreateResenaProgramaInput:
    estudiante_id: int
    programa_id: int
    calificacion: int
    comentario: str


class CreateResenaProgramaUseCase:
    def __init__(self, repository: AbstractResenaProgramaRepository):
        self._repo = repository

    def execute(self, input_dto: CreateResenaProgramaInput) -> ResenaProgramaEntity:
        if not (1 <= input_dto.calificacion <= 5):
            raise CalificacionInvalida("La calificación debe estar entre 1 y 5.")
        if self._repo.exists(input_dto.estudiante_id, input_dto.programa_id):
            raise ResenaYaExiste("Ya tienes una reseña para este programa.")
        return self._repo.create(
            estudiante_id=input_dto.estudiante_id,
            programa_id=input_dto.programa_id,
            calificacion=input_dto.calificacion,
            comentario=input_dto.comentario,
        )
