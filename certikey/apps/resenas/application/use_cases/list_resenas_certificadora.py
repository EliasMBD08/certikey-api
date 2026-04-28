from apps.resenas.domain.repositories.resena_certificadora_repository import AbstractResenaCertificadoraRepository
from apps.resenas.domain.entities.resena_certificadora import ResenaCertificadoraEntity


class ListResenasCertificadoraUseCase:
    def __init__(self, repository: AbstractResenaCertificadoraRepository):
        self._repo = repository

    def execute(self, certificadora_id: int) -> list[ResenaCertificadoraEntity]:
        return self._repo.list_by_certificadora(certificadora_id)
