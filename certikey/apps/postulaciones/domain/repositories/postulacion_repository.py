from abc import ABC, abstractmethod
from apps.postulaciones.domain.entities.postulacion import PostulacionEntity


class AbstractPostulacionRepository(ABC):
    @abstractmethod
    def create(self, estudiante_id: int, programa_id: int, mensaje: str) -> PostulacionEntity: ...

    @abstractmethod
    def list_by_estudiante(self, estudiante_id: int) -> list[PostulacionEntity]: ...

    @abstractmethod
    def get_by_id(self, postulacion_id: int) -> PostulacionEntity: ...

    @abstractmethod
    def exists(self, estudiante_id: int, programa_id: int) -> bool: ...
