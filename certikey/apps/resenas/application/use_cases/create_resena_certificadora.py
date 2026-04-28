from dataclasses import dataclass

from apps.resenas.domain.repositories.resena_certificadora_repository import AbstractResenaCertificadoraRepository
from apps.resenas.domain.entities.resena_certificadora import ResenaCertificadoraEntity
from apps.resenas.domain.exceptions import ResenaYaExiste, CalificacionInvalida


@dataclass
class CreateResenaCertificadoraInput:
    estudiante_id: int
    certificadora_id: int
    calificacion: int
    comentario: str


class CreateResenaCertificadoraUseCase:
    def __init__(self, repository: AbstractResenaCertificadoraRepository):
        self._repo = repository

    def execute(self, input_dto: CreateResenaCertificadoraInput) -> ResenaCertificadoraEntity:
        if not (1 <= input_dto.calificacion <= 5):
            raise CalificacionInvalida("La calificación debe estar entre 1 y 5.")
        if self._repo.exists(input_dto.estudiante_id, input_dto.certificadora_id):
            raise ResenaYaExiste("Ya tienes una reseña para esta certificadora.")
        return self._repo.create(
            estudiante_id=input_dto.estudiante_id,
            certificadora_id=input_dto.certificadora_id,
            calificacion=input_dto.calificacion,
            comentario=input_dto.comentario,
        )
