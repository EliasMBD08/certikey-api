from dataclasses import dataclass
from apps.postulaciones.domain.repositories.postulacion_repository import AbstractPostulacionRepository
from apps.postulaciones.domain.entities.postulacion import PostulacionEntity
from apps.postulaciones.domain.exceptions import PostulacionDuplicada, ProgramaSinInscripciones


@dataclass
class CreatePostulacionInput:
    estudiante_id: int
    programa_id: int
    mensaje: str = ''


class CreatePostulacionUseCase:
    def __init__(
        self,
        postulacion_repository: AbstractPostulacionRepository,
        programa_repository,
    ):
        self._repo = postulacion_repository
        self._programa_repo = programa_repository

    def execute(self, input_dto: CreatePostulacionInput) -> PostulacionEntity:
        if self._repo.exists(input_dto.estudiante_id, input_dto.programa_id):
            raise PostulacionDuplicada("Ya existe una postulación para este programa.")

        programa = self._programa_repo.get_by_id(input_dto.programa_id)
        if not programa.inscripciones_abiertas:
            raise ProgramaSinInscripciones("Este programa no está aceptando postulaciones.")

        return self._repo.create(
            estudiante_id=input_dto.estudiante_id,
            programa_id=input_dto.programa_id,
            mensaje=input_dto.mensaje,
        )
