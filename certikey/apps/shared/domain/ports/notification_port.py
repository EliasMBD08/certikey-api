from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class InteresNotificationDTO:
    email_certificadora: str
    nombre_institucion: str
    nombre_estudiante: str
    titulo_programa: str
    programa_id: int


@dataclass
class ResenaNotificationDTO:
    email_certificadora: str
    nombre_institucion: str
    nombre_estudiante: str
    titulo_programa: str
    programa_id: int
    calificacion: int
    comentario: str


@dataclass
class ProgramaGratuitoNotificationDTO:
    titulo_programa: str
    programa_id: int
    emails_estudiantes: list[str]


class AbstractNotificationPort(ABC):
    @abstractmethod
    def notify_interes(self, dto: InteresNotificationDTO) -> None: ...

    @abstractmethod
    def notify_resena(self, dto: ResenaNotificationDTO) -> None: ...

    @abstractmethod
    def notify_programa_gratuito(self, dto: ProgramaGratuitoNotificationDTO) -> None: ...
