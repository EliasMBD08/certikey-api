from abc import ABC, abstractmethod

from apps.intereses.domain.entities.interes import InteresEntity


class AbstractInteresRepository(ABC):
    @abstractmethod
    def save(self, estudiante_id: int, programa_id: int) -> InteresEntity: ...

    @abstractmethod
    def remove(self, estudiante_id: int, programa_id: int) -> None: ...

    @abstractmethod
    def list_by_estudiante(self, estudiante_id: int) -> list[InteresEntity]: ...

    @abstractmethod
    def get(self, estudiante_id: int, programa_id: int) -> InteresEntity | None: ...
