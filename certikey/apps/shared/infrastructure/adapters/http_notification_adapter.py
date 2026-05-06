import os

import requests

from apps.shared.domain.ports.notification_port import (
    AbstractNotificationPort,
    InteresNotificationDTO,
    ResenaNotificationDTO,
    ProgramaGratuitoNotificationDTO,
)
from dataclasses import asdict

NOTIFICATIONS_SERVICE_URL = os.getenv("NOTIFICATIONS_SERVICE_URL", "http://localhost:8001")
_TIMEOUT = 3


class HttpNotificationAdapter(AbstractNotificationPort):

    def notify_interes(self, dto: InteresNotificationDTO) -> None:
        self._post("/api/notificaciones/interes", asdict(dto))

    def notify_resena(self, dto: ResenaNotificationDTO) -> None:
        self._post("/api/notificaciones/resena", asdict(dto))

    def notify_programa_gratuito(self, dto: ProgramaGratuitoNotificationDTO) -> None:
        self._post("/api/notificaciones/programa-gratuito", asdict(dto))

    def _post(self, path: str, payload: dict) -> None:
        try:
            requests.post(
                f"{NOTIFICATIONS_SERVICE_URL}{path}",
                json=payload,
                timeout=_TIMEOUT,
            )
        except requests.exceptions.RequestException:
            pass
