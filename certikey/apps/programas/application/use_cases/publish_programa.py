from apps.programas.domain.repositories.programa_repository import AbstractProgramaRepository
from apps.programas.domain.entities.programa import ProgramaEntity
from apps.programas.domain.exceptions import (
    ProgramaNotFound, AccesoDenegado, CertificadoraNoVerificada, ProgramaYaPublicado,
)


class PublishProgramaUseCase:
    def __init__(self, programa_repository: AbstractProgramaRepository):
        self._repo = programa_repository

    def execute(self, programa_id: int, certificadora_id: int, puede_publicar: bool) -> ProgramaEntity:
        programa = self._repo.get_by_id(programa_id)

        if programa.certificadora_id != certificadora_id:
            raise AccesoDenegado("No tienes permiso para publicar este programa.")

        if not puede_publicar:
            raise CertificadoraNoVerificada(
                "Tu institución aún no está verificada. Contacta al administrador."
            )

        if programa.estado_slug == 'publicado':
            raise ProgramaYaPublicado("El programa ya está publicado.")

        return self._repo.update_estado(programa_id, 'publicado')
