# Notifications Microservice — Especificación Técnica

## 1. Contexto del Sistema

### 1.1 Sistema principal: certikey-api

`certikey-api` es una API REST construida con Django + Django REST Framework siguiendo arquitectura hexagonal. Sus entidades relevantes para este microservicio son:

- **Usuario**: modelo de autenticación con `email`, `first_name`, `last_name`, `rol` (estudiante | certificadora | admin).
- **PerfilEstudiante**: extensión del usuario estudiante. Relación 1-a-1 con `Usuario`.
- **PerfilCertificadora**: extensión del usuario certificadora. Tiene `nombre_institucion`. Relación 1-a-1 con `Usuario`.
- **Programa**: publicado por una certificadora. Tiene `titulo`, `es_gratuito`, `otorga_certificado`, `estado`, `certificadora` (FK a `PerfilCertificadora`).
- **Interes**: relación entre un `PerfilEstudiante` y un `Programa`. Soporta soft-delete (campo `activo`).
- **ResenaPrograma**: escrita por un estudiante sobre un `Programa`. Tiene `calificacion` (1–5) y `comentario`.

### 1.2 Decisión de arquitectura: base de datos propia

El microservicio de notificaciones **tiene su propia base de datos PostgreSQL independiente**. No comparte la BD con `certikey-api`.

**Justificación**: cada microservicio debe ser autónomo. Compartir BD genera acoplamiento de esquema — cualquier migración en certikey-api podría romper el microservicio sin advertencia.

**Consecuencia**: `certikey-api` es responsable de resolver todos los datos necesarios (emails, nombres, listas de interesados) **antes** de llamar al microservicio. El microservicio solo recibe payloads completos y los procesa. No realiza llamadas de vuelta a certikey-api ni consulta su BD.

### 1.3 Comunicación: HTTP síncrono

`certikey-api` llama al microservicio mediante HTTP POST con un payload JSON. Las llamadas son **fire-and-forget con timeout corto (3s)**: si el microservicio no responde, certikey-api no falla — el flujo principal continúa.

---

## 2. Triggers de Notificación

### Trigger 1 — Estudiante guarda interés en un programa

**Cuándo**: `POST /api/v1/intereses/` exitoso en certikey-api.  
**A quién se notifica**: a la certificadora dueña del programa.  
**Canal**: email.

### Trigger 2 — Estudiante escribe una reseña de un programa

**Cuándo**: `POST /api/v1/resenas/programas/` exitoso en certikey-api.  
**A quién se notifica**: a la certificadora dueña del programa reseñado.  
**Canal**: email.

### Trigger 3 — Un programa se habilita con certificación gratuita

**Cuándo**: `PATCH /api/v1/programas/{id}/` en certikey-api cuando el resultado final del programa tiene `es_gratuito=True` Y `otorga_certificado=True`, y el valor previo de `es_gratuito` era `False`.  
**A quién se notifica**: a todos los estudiantes con un `Interes` activo en ese programa.  
**Canal**: email.

---

## 3. Modificaciones en certikey-api

> Estas modificaciones deben implementarse en el proyecto `certikey-api` (Django), no en el microservicio FastAPI.

### 3.1 Puerto abstracto de notificaciones

Crear el archivo `certikey/apps/shared/domain/ports/notification_port.py`:

```python
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
    emails_estudiantes: list[str]  # lista de emails de estudiantes interesados


class AbstractNotificationPort(ABC):
    @abstractmethod
    def notify_interes(self, dto: InteresNotificationDTO) -> None: ...

    @abstractmethod
    def notify_resena(self, dto: ResenaNotificationDTO) -> None: ...

    @abstractmethod
    def notify_programa_gratuito(self, dto: ProgramaGratuitoNotificationDTO) -> None: ...
```

### 3.2 Adaptador HTTP

Crear `certikey/apps/shared/infrastructure/adapters/http_notification_adapter.py`:

```python
import os
import requests
from dataclasses import asdict

from apps.shared.domain.ports.notification_port import (
    AbstractNotificationPort,
    InteresNotificationDTO,
    ResenaNotificationDTO,
    ProgramaGratuitoNotificationDTO,
)

NOTIFICATIONS_SERVICE_URL = os.getenv("NOTIFICATIONS_SERVICE_URL", "http://localhost:8001")
TIMEOUT = 3  # segundos


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
                timeout=TIMEOUT,
            )
        except requests.exceptions.RequestException:
            # Fire-and-forget: no bloquear el flujo principal si el servicio no responde
            pass
```

### 3.3 Modificación en InteresViewSet

En `certikey/apps/intereses/presentation/views/interes_viewset.py`, modificar el método `create` para llamar al adaptador después de guardar el interés exitosamente:

```python
from apps.shared.infrastructure.adapters.http_notification_adapter import HttpNotificationAdapter
from apps.shared.domain.ports.notification_port import InteresNotificationDTO


def create(self, request):
    serializer = SaveInteresSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    input_dto = SaveInteresInput(
        estudiante_id=request.user.perfil_estudiante.id,
        programa_id=serializer.validated_data['programa_id'],
    )
    try:
        interes = SaveInteresUseCase(_repo()).execute(input_dto)
    except InteresYaExiste as e:
        return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)

    # Notificar a la certificadora (fire-and-forget)
    try:
        from apps.programas.infrastructure.models import Programa
        programa = Programa.objects.select_related(
            'certificadora__usuario'
        ).get(id=interes.programa_id)

        estudiante = request.user
        notif_dto = InteresNotificationDTO(
            email_certificadora=programa.certificadora.usuario.email,
            nombre_institucion=programa.certificadora.nombre_institucion,
            nombre_estudiante=f"{estudiante.first_name} {estudiante.last_name}".strip() or estudiante.username,
            titulo_programa=programa.titulo,
            programa_id=programa.id,
        )
        HttpNotificationAdapter().notify_interes(notif_dto)
    except Exception:
        pass  # No interrumpir si falla la notificación

    return Response(asdict(interes), status=status.HTTP_201_CREATED)
```

### 3.4 Modificación en ResenaProgramaViewSet

En `certikey/apps/resenas/presentation/views/resena_programa_viewset.py`, modificar el método `create`:

```python
from apps.shared.infrastructure.adapters.http_notification_adapter import HttpNotificationAdapter
from apps.shared.domain.ports.notification_port import ResenaNotificationDTO


def create(self, request):
    serializer = CreateResenaProgramaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    input_dto = CreateResenaProgramaInput(
        estudiante_id=request.user.perfil_estudiante.id,
        **serializer.validated_data,
    )
    try:
        resena = CreateResenaProgramaUseCase(_repo()).execute(input_dto)
    except ResenaYaExiste as e:
        return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)
    except CalificacionInvalida as e:
        return Response({"detail": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Notificar a la certificadora (fire-and-forget)
    try:
        from apps.programas.infrastructure.models import Programa
        programa = Programa.objects.select_related(
            'certificadora__usuario'
        ).get(id=resena.programa_id)

        estudiante = request.user
        notif_dto = ResenaNotificationDTO(
            email_certificadora=programa.certificadora.usuario.email,
            nombre_institucion=programa.certificadora.nombre_institucion,
            nombre_estudiante=f"{estudiante.first_name} {estudiante.last_name}".strip() or estudiante.username,
            titulo_programa=programa.titulo,
            programa_id=programa.id,
            calificacion=resena.calificacion,
            comentario=resena.comentario,
        )
        HttpNotificationAdapter().notify_resena(notif_dto)
    except Exception:
        pass

    return Response(asdict(resena), status=status.HTTP_201_CREATED)
```

### 3.5 Modificación en ProgramaViewSet (Trigger 3)

En el método `partial_update` (o `update`) del viewset de programas, detectar el cambio de `es_gratuito` y llamar al adaptador:

```python
from apps.shared.infrastructure.adapters.http_notification_adapter import HttpNotificationAdapter
from apps.shared.domain.ports.notification_port import ProgramaGratuitoNotificationDTO


def partial_update(self, request, pk=None):
    # ... lógica existente de actualización ...

    programa_antes = GetProgramaUseCase(_repo()).execute(int(pk))
    # ... ejecutar UpdateProgramaUseCase ...
    programa_despues = UpdateProgramaUseCase(_repo()).execute(input_dto)

    # Detectar activación de certificación gratuita
    activo_antes = programa_antes.es_gratuito
    activo_ahora = programa_despues.es_gratuito and programa_despues.otorga_certificado

    if not activo_antes and activo_ahora:
        try:
            from apps.intereses.infrastructure.models import Interes
            emails = list(
                Interes.objects.filter(programa_id=programa_despues.id)
                .select_related('estudiante__usuario')
                .values_list('estudiante__usuario__email', flat=True)
            )
            if emails:
                notif_dto = ProgramaGratuitoNotificationDTO(
                    titulo_programa=programa_despues.titulo,
                    programa_id=programa_despues.id,
                    emails_estudiantes=emails,
                )
                HttpNotificationAdapter().notify_programa_gratuito(notif_dto)
        except Exception:
            pass

    return Response(asdict(programa_despues))
```

### 3.6 Variable de entorno en certikey-api

Agregar al `.env` del proyecto Django:

```env
NOTIFICATIONS_SERVICE_URL=http://localhost:8001
```

---

## 4. Microservicio FastAPI — notifications-service

### 4.1 Estructura de carpetas

```
notifications-service/
├── app/
│   ├── domain/
│   │   ├── entities/
│   │   │   └── notification.py
│   │   ├── repositories/
│   │   │   └── notification_repository.py
│   │   └── exceptions.py
│   ├── application/
│   │   └── use_cases/
│   │       ├── notify_certificadora_interes.py
│   │       ├── notify_certificadora_resena.py
│   │       └── notify_estudiantes_programa_gratuito.py
│   ├── infrastructure/
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── repositories/
│   │   │   └── sqlalchemy_notification_repository.py
│   │   └── email/
│   │       └── email_sender.py
│   └── presentation/
│       ├── routers/
│       │   └── notification_router.py
│       └── schemas/
│           └── notification_schemas.py
├── main.py
├── .env
├── requirements.txt
└── Dockerfile
```

### 4.2 Base de datos propia

El microservicio usa su **propia base de datos PostgreSQL** con una única tabla: `notificaciones`.

No realiza migraciones en la BD de certikey-api ni lee de ella.

---

## 5. Capa de Dominio

### 5.1 `app/domain/entities/notification.py`

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TipoNotificacion(str, Enum):
    INTERES_EN_PROGRAMA = "interes_en_programa"
    RESENA_PROGRAMA = "resena_programa"
    PROGRAMA_GRATUITO = "programa_gratuito"


class EstadoEnvio(str, Enum):
    ENVIADO = "enviado"
    FALLIDO = "fallido"


@dataclass
class NotificationEntity:
    id: int
    tipo: TipoNotificacion
    destinatario_email: str
    asunto: str
    cuerpo_html: str
    estado: EstadoEnvio
    fecha_creacion: datetime
    error: str | None = None
    programa_id: int | None = None
```

### 5.2 `app/domain/repositories/notification_repository.py`

```python
from abc import ABC, abstractmethod
from app.domain.entities.notification import NotificationEntity, TipoNotificacion, EstadoEnvio


class AbstractNotificationRepository(ABC):

    @abstractmethod
    async def save(
        self,
        tipo: TipoNotificacion,
        destinatario_email: str,
        asunto: str,
        cuerpo_html: str,
        estado: EstadoEnvio,
        programa_id: int | None = None,
        error: str | None = None,
    ) -> NotificationEntity: ...

    @abstractmethod
    async def list_by_programa(self, programa_id: int) -> list[NotificationEntity]: ...
```

### 5.3 `app/domain/exceptions.py`

```python
class NotificationError(Exception):
    """Error base del dominio de notificaciones."""
```

---

## 6. Capa de Aplicación — Casos de Uso

### 6.1 `app/application/use_cases/notify_certificadora_interes.py`

Recibe los datos del interés, construye el email y lo envía a la certificadora.

```python
from dataclasses import dataclass
from app.domain.repositories.notification_repository import AbstractNotificationRepository
from app.domain.entities.notification import TipoNotificacion, EstadoEnvio
from app.infrastructure.email.email_sender import AbstractEmailSender


@dataclass
class NotifyCertificadoraInteresInput:
    email_certificadora: str
    nombre_institucion: str
    nombre_estudiante: str
    titulo_programa: str
    programa_id: int


class NotifyCertificadoraInteresUseCase:
    def __init__(
        self,
        repo: AbstractNotificationRepository,
        email_sender: AbstractEmailSender,
    ):
        self._repo = repo
        self._email = email_sender

    async def execute(self, input_dto: NotifyCertificadoraInteresInput) -> None:
        asunto = f"Nuevo interés en tu programa: {input_dto.titulo_programa}"
        cuerpo_html = f"""
        <h2>Nuevo interés registrado</h2>
        <p>Hola <strong>{input_dto.nombre_institucion}</strong>,</p>
        <p>El estudiante <strong>{input_dto.nombre_estudiante}</strong> ha guardado
        tu programa <strong>{input_dto.titulo_programa}</strong> como interés.</p>
        <p>Esto indica que un potencial participante está evaluando inscribirse.</p>
        """

        estado = EstadoEnvio.ENVIADO
        error = None
        try:
            await self._email.send(
                to=input_dto.email_certificadora,
                subject=asunto,
                html_body=cuerpo_html,
            )
        except Exception as e:
            estado = EstadoEnvio.FALLIDO
            error = str(e)

        await self._repo.save(
            tipo=TipoNotificacion.INTERES_EN_PROGRAMA,
            destinatario_email=input_dto.email_certificadora,
            asunto=asunto,
            cuerpo_html=cuerpo_html,
            estado=estado,
            programa_id=input_dto.programa_id,
            error=error,
        )
```

### 6.2 `app/application/use_cases/notify_certificadora_resena.py`

```python
from dataclasses import dataclass
from app.domain.repositories.notification_repository import AbstractNotificationRepository
from app.domain.entities.notification import TipoNotificacion, EstadoEnvio
from app.infrastructure.email.email_sender import AbstractEmailSender

ESTRELLAS = {1: "★☆☆☆☆", 2: "★★☆☆☆", 3: "★★★☆☆", 4: "★★★★☆", 5: "★★★★★"}


@dataclass
class NotifyCertificadoraResenaInput:
    email_certificadora: str
    nombre_institucion: str
    nombre_estudiante: str
    titulo_programa: str
    programa_id: int
    calificacion: int
    comentario: str


class NotifyCertificadoraResenaUseCase:
    def __init__(
        self,
        repo: AbstractNotificationRepository,
        email_sender: AbstractEmailSender,
    ):
        self._repo = repo
        self._email = email_sender

    async def execute(self, input_dto: NotifyCertificadoraResenaInput) -> None:
        estrellas = ESTRELLAS.get(input_dto.calificacion, "")
        asunto = f"Nueva reseña en tu programa: {input_dto.titulo_programa}"
        cuerpo_html = f"""
        <h2>Nueva reseña recibida</h2>
        <p>Hola <strong>{input_dto.nombre_institucion}</strong>,</p>
        <p>El estudiante <strong>{input_dto.nombre_estudiante}</strong> ha dejado
        una reseña en tu programa <strong>{input_dto.titulo_programa}</strong>.</p>
        <p><strong>Calificación:</strong> {estrellas} ({input_dto.calificacion}/5)</p>
        <p><strong>Comentario:</strong></p>
        <blockquote>{input_dto.comentario}</blockquote>
        """

        estado = EstadoEnvio.ENVIADO
        error = None
        try:
            await self._email.send(
                to=input_dto.email_certificadora,
                subject=asunto,
                html_body=cuerpo_html,
            )
        except Exception as e:
            estado = EstadoEnvio.FALLIDO
            error = str(e)

        await self._repo.save(
            tipo=TipoNotificacion.RESENA_PROGRAMA,
            destinatario_email=input_dto.email_certificadora,
            asunto=asunto,
            cuerpo_html=cuerpo_html,
            estado=estado,
            programa_id=input_dto.programa_id,
            error=error,
        )
```

### 6.3 `app/application/use_cases/notify_estudiantes_programa_gratuito.py`

```python
from dataclasses import dataclass
from app.domain.repositories.notification_repository import AbstractNotificationRepository
from app.domain.entities.notification import TipoNotificacion, EstadoEnvio
from app.infrastructure.email.email_sender import AbstractEmailSender


@dataclass
class NotifyEstudiantesProgramaGratuitoInput:
    titulo_programa: str
    programa_id: int
    emails_estudiantes: list[str]


class NotifyEstudiantesProgramaGratuitoUseCase:
    def __init__(
        self,
        repo: AbstractNotificationRepository,
        email_sender: AbstractEmailSender,
    ):
        self._repo = repo
        self._email = email_sender

    async def execute(self, input_dto: NotifyEstudiantesProgramaGratuitoInput) -> None:
        asunto = f"¡Buenas noticias! {input_dto.titulo_programa} ahora es gratuito con certificado"
        cuerpo_html = f"""
        <h2>¡Un programa que te interesa ahora es gratuito!</h2>
        <p>El programa <strong>{input_dto.titulo_programa}</strong> que guardaste
        ahora ofrece <strong>certificación gratuita</strong>.</p>
        <p>¡No pierdas la oportunidad de inscribirte!</p>
        """

        for email in input_dto.emails_estudiantes:
            estado = EstadoEnvio.ENVIADO
            error = None
            try:
                await self._email.send(
                    to=email,
                    subject=asunto,
                    html_body=cuerpo_html,
                )
            except Exception as e:
                estado = EstadoEnvio.FALLIDO
                error = str(e)

            await self._repo.save(
                tipo=TipoNotificacion.PROGRAMA_GRATUITO,
                destinatario_email=email,
                asunto=asunto,
                cuerpo_html=cuerpo_html,
                estado=estado,
                programa_id=input_dto.programa_id,
                error=error,
            )
```

---

## 7. Capa de Infraestructura

### 7.1 `app/infrastructure/db.py`

Configurar SQLAlchemy async con la BD propia del microservicio.

```python
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/notifications_db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

### 7.2 `app/infrastructure/models.py`

```python
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db import Base


class NotificationModel(Base):
    __tablename__ = "notificaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo: Mapped[str] = mapped_column(String(50))                    # TipoNotificacion value
    destinatario_email: Mapped[str] = mapped_column(String(255))
    asunto: Mapped[str] = mapped_column(String(255))
    cuerpo_html: Mapped[str] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(String(20))                  # EstadoEnvio value
    programa_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

### 7.3 `app/infrastructure/repositories/sqlalchemy_notification_repository.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.repositories.notification_repository import AbstractNotificationRepository
from app.domain.entities.notification import NotificationEntity, TipoNotificacion, EstadoEnvio
from app.infrastructure.models import NotificationModel


class SqlalchemyNotificationRepository(AbstractNotificationRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(
        self,
        tipo: TipoNotificacion,
        destinatario_email: str,
        asunto: str,
        cuerpo_html: str,
        estado: EstadoEnvio,
        programa_id: int | None = None,
        error: str | None = None,
    ) -> NotificationEntity:
        model = NotificationModel(
            tipo=tipo.value,
            destinatario_email=destinatario_email,
            asunto=asunto,
            cuerpo_html=cuerpo_html,
            estado=estado.value,
            programa_id=programa_id,
            error=error,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def list_by_programa(self, programa_id: int) -> list[NotificationEntity]:
        result = await self._session.execute(
            select(NotificationModel).where(NotificationModel.programa_id == programa_id)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, m: NotificationModel) -> NotificationEntity:
        return NotificationEntity(
            id=m.id,
            tipo=TipoNotificacion(m.tipo),
            destinatario_email=m.destinatario_email,
            asunto=m.asunto,
            cuerpo_html=m.cuerpo_html,
            estado=EstadoEnvio(m.estado),
            fecha_creacion=m.fecha_creacion,
            error=m.error,
            programa_id=m.programa_id,
        )
```

### 7.4 `app/infrastructure/email/email_sender.py`

Usar `fastapi-mail` para el envío real. Definir también una clase abstracta para facilitar testing.

```python
import os
from abc import ABC, abstractmethod
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType


class AbstractEmailSender(ABC):
    @abstractmethod
    async def send(self, to: str, subject: str, html_body: str) -> None: ...


class FastApiMailSender(AbstractEmailSender):
    def __init__(self):
        self._conf = ConnectionConfig(
            MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
            MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
            MAIL_FROM=os.getenv("MAIL_FROM"),
            MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
            MAIL_SERVER=os.getenv("MAIL_SERVER"),
            MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "true").lower() == "true",
            MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "false").lower() == "true",
            USE_CREDENTIALS=True,
        )

    async def send(self, to: str, subject: str, html_body: str) -> None:
        message = MessageSchema(
            subject=subject,
            recipients=[to],
            body=html_body,
            subtype=MessageType.html,
        )
        fm = FastMail(self._conf)
        await fm.send_message(message)
```

---

## 8. Capa de Presentación

### 8.1 `app/presentation/schemas/notification_schemas.py`

Estos son los **payloads exactos** que certikey-api enviará al microservicio.

```python
from pydantic import BaseModel, EmailStr


# ── Trigger 1: Estudiante guarda interés ──────────────────────────────────────

class InteresPayload(BaseModel):
    email_certificadora: str        # email del usuario certificadora dueño del programa
    nombre_institucion: str         # PerfilCertificadora.nombre_institucion
    nombre_estudiante: str          # first_name + last_name del usuario estudiante
    titulo_programa: str            # Programa.titulo
    programa_id: int                # Programa.id


# ── Trigger 2: Estudiante escribe reseña ──────────────────────────────────────

class ResenaPayload(BaseModel):
    email_certificadora: str
    nombre_institucion: str
    nombre_estudiante: str
    titulo_programa: str
    programa_id: int
    calificacion: int               # 1–5
    comentario: str


# ── Trigger 3: Programa habilita certificación gratuita ───────────────────────

class ProgramaGratuitoPayload(BaseModel):
    titulo_programa: str
    programa_id: int
    emails_estudiantes: list[str]   # emails de todos los estudiantes con Interes activo


# ── Respuesta estándar ────────────────────────────────────────────────────────

class NotificacionResponse(BaseModel):
    status: str
    enviadas: int
```

### 8.2 `app/presentation/routers/notification_router.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db import get_session
from app.infrastructure.repositories.sqlalchemy_notification_repository import SqlalchemyNotificationRepository
from app.infrastructure.email.email_sender import FastApiMailSender
from app.application.use_cases.notify_certificadora_interes import (
    NotifyCertificadoraInteresUseCase,
    NotifyCertificadoraInteresInput,
)
from app.application.use_cases.notify_certificadora_resena import (
    NotifyCertificadoraResenaUseCase,
    NotifyCertificadoraResenaInput,
)
from app.application.use_cases.notify_estudiantes_programa_gratuito import (
    NotifyEstudiantesProgramaGratuitoUseCase,
    NotifyEstudiantesProgramaGratuitoInput,
)
from app.presentation.schemas.notification_schemas import (
    InteresPayload,
    ResenaPayload,
    ProgramaGratuitoPayload,
    NotificacionResponse,
)

router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])


def _deps(session: AsyncSession = Depends(get_session)):
    repo = SqlalchemyNotificationRepository(session)
    email_sender = FastApiMailSender()
    return repo, email_sender


@router.post("/interes", response_model=NotificacionResponse)
async def notificar_interes(
    payload: InteresPayload,
    deps=Depends(_deps),
):
    repo, email_sender = deps
    await NotifyCertificadoraInteresUseCase(repo, email_sender).execute(
        NotifyCertificadoraInteresInput(**payload.model_dump())
    )
    return {"status": "ok", "enviadas": 1}


@router.post("/resena", response_model=NotificacionResponse)
async def notificar_resena(
    payload: ResenaPayload,
    deps=Depends(_deps),
):
    repo, email_sender = deps
    await NotifyCertificadoraResenaUseCase(repo, email_sender).execute(
        NotifyCertificadoraResenaInput(**payload.model_dump())
    )
    return {"status": "ok", "enviadas": 1}


@router.post("/programa-gratuito", response_model=NotificacionResponse)
async def notificar_programa_gratuito(
    payload: ProgramaGratuitoPayload,
    deps=Depends(_deps),
):
    repo, email_sender = deps
    await NotifyEstudiantesProgramaGratuitoUseCase(repo, email_sender).execute(
        NotifyEstudiantesProgramaGratuitoInput(**payload.model_dump())
    )
    return {"status": "ok", "enviadas": len(payload.emails_estudiantes)}
```

### 8.3 `main.py`

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.infrastructure.db import init_db
from app.presentation.routers.notification_router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Certikey Notifications Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
```

---

## 9. Configuración y Dependencias

### 9.1 `requirements.txt`

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy[asyncio]==2.0.35
asyncpg==0.29.0
fastapi-mail==1.4.1
pydantic[email]==2.9.0
python-dotenv==1.0.1
alembic==1.13.3
```

### 9.2 `.env`

```env
# Base de datos propia del microservicio (NO la de certikey-api)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/notifications_db

# Configuración SMTP (ejemplo con Gmail)
MAIL_USERNAME=notificaciones@certikey.com
MAIL_PASSWORD=tu_app_password
MAIL_FROM=notificaciones@certikey.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_STARTTLS=true
MAIL_SSL_TLS=false
```

### 9.3 `Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

---

## 10. Resumen de Contratos API

| Endpoint | Método | Disparado por | Descripción |
|---|---|---|---|
| `/api/notificaciones/interes` | POST | certikey-api al guardar `Interes` | Notifica a la certificadora de un nuevo interés |
| `/api/notificaciones/resena` | POST | certikey-api al crear `ResenaPrograma` | Notifica a la certificadora de una nueva reseña |
| `/api/notificaciones/programa-gratuito` | POST | certikey-api al detectar cambio `es_gratuito=True` | Notifica a los estudiantes interesados |
| `/health` | GET | Load balancer / monitoring | Health check |

---

## 11. Notas para el Agente Implementador

1. **No implementar autenticación entre servicios** en esta versión. Las llamadas son internas (red privada). Si se requiere en el futuro, agregar un `X-Internal-Token` header.

2. **El microservicio corre en el puerto 8001** para no colisionar con certikey-api (puerto 8000).

3. **La BD `notifications_db` debe crearse manualmente** antes de levantar el servicio. El `init_db()` en el startup solo crea las tablas, no la base de datos.

4. **Los use cases absorben errores de envío de email**: si el envío falla, se registra el error en la tabla `notificaciones` con `estado='fallido'` en lugar de lanzar excepción al caller.

5. **El campo `cuerpo_html` en la tabla** almacena el HTML completo del email para auditoría y reenvíos futuros.

6. **Respetar arquitectura hexagonal**: dominio no debe importar de infraestructura. Los use cases dependen de las interfaces abstractas (`AbstractNotificationRepository`, `AbstractEmailSender`), no de las implementaciones concretas.
