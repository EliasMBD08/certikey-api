from abc import ABC, abstractmethod

from apps.resenas.domain.entities.resena_programa import ResenaProgramaEntity


class AbstractResenaProgramaRepository(ABC):
    @abstractmethod
    def create(
        self,
        estudiante_id: int,
        programa_id: int,
        calificacion: int,
        comentario: str,
    ) -> ResenaProgramaEntity: ...

    @abstractmethod
    def list_by_programa(self, programa_id: int) -> list[ResenaProgramaEntity]: ...

    @abstractmethod
    def exists(self, estudiante_id: int, programa_id: int) -> bool: ...
