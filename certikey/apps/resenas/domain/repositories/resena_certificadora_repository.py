from abc import ABC, abstractmethod

from apps.resenas.domain.entities.resena_certificadora import ResenaCertificadoraEntity


class AbstractResenaCertificadoraRepository(ABC):
    @abstractmethod
    def create(
        self,
        estudiante_id: int,
        certificadora_id: int,
        calificacion: int,
        comentario: str,
    ) -> ResenaCertificadoraEntity: ...

    @abstractmethod
    def list_by_certificadora(self, certificadora_id: int) -> list[ResenaCertificadoraEntity]: ...

    @abstractmethod
    def exists(self, estudiante_id: int, certificadora_id: int) -> bool: ...
