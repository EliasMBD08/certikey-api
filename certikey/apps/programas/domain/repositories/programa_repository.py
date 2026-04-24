from abc import ABC, abstractmethod
from apps.programas.domain.entities.programa import ProgramaEntity


class AbstractProgramaRepository(ABC):
    @abstractmethod
    def create(self, certificadora_id: int, **kwargs) -> ProgramaEntity: ...

    @abstractmethod
    def get_by_id(self, programa_id: int) -> ProgramaEntity: ...

    @abstractmethod
    def get_by_slug(self, slug: str) -> ProgramaEntity: ...

    @abstractmethod
    def list_public(self, filters: dict) -> list[ProgramaEntity]: ...

    @abstractmethod
    def list_by_certificadora(self, certificadora_id: int) -> list[ProgramaEntity]: ...

    @abstractmethod
    def update(self, programa_id: int, **kwargs) -> ProgramaEntity: ...

    @abstractmethod
    def update_estado(self, programa_id: int, estado_slug: str) -> ProgramaEntity: ...
