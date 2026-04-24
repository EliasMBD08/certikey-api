# Code Patterns by Layer

Full examples for every layer. Adapt names to the actual domain — these use `User` as a sample entity.

---

## Domain — Entity

```python
# domain/entities/user.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    email: str
    full_name: str
    id: int | None = None
    created_at: datetime | None = None
```

Entities are pure Python. Never import Django or any external library here. Business behavior (methods, validations) lives on these classes.

---

## Domain — Repository interface (port)

```python
# domain/repositories/user_repository.py
from abc import ABC, abstractmethod
from domain.entities.user import User

class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def save(self, user: User) -> User: ...

    @abstractmethod
    def delete(self, user_id: int) -> None: ...
```

---

## Domain — Exceptions

```python
# domain/exceptions.py
class UserNotFound(Exception): ...
class EmailAlreadyExists(Exception): ...
class InvalidUserData(Exception): ...
```

Name exceptions after business events, not technical ones. `UserNotFound` is correct; `DoesNotExist` is a Django detail.

---

## Application — Use case with DTOs

```python
# application/use_cases/create_user.py
from dataclasses import dataclass
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from domain.exceptions import EmailAlreadyExists

@dataclass
class CreateUserInput:
    email: str
    full_name: str

@dataclass
class CreateUserOutput:
    id: int
    email: str
    full_name: str

class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self._repo = user_repository

    def execute(self, input_dto: CreateUserInput) -> CreateUserOutput:
        if self._repo.get_by_email(input_dto.email):
            raise EmailAlreadyExists(f"Email {input_dto.email} is already registered")

        user = User(email=input_dto.email, full_name=input_dto.full_name)
        saved = self._repo.save(user)

        return CreateUserOutput(id=saved.id, email=saved.email, full_name=saved.full_name)
```

One class, one public method (`execute`), one responsibility. The use case receives its dependencies — it never instantiates them.

---

## Infrastructure — Django ORM model

```python
# infrastructure/models.py
from django.db import models

class UserModel(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"
```

ORM models are an infrastructure detail. They do not inherit from domain entities and carry no business logic.

---

## Infrastructure — Concrete repository (adapter)

```python
# infrastructure/repositories/django_user_repository.py
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from infrastructure.models import UserModel

class DjangoUserRepository(UserRepository):
    def get_by_id(self, user_id: int) -> User | None:
        try:
            return self._to_entity(UserModel.objects.get(pk=user_id))
        except UserModel.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> User | None:
        model = UserModel.objects.filter(email=email).first()
        return self._to_entity(model) if model else None

    def save(self, user: User) -> User:
        if user.id:
            model, _ = UserModel.objects.update_or_create(
                pk=user.id,
                defaults={"email": user.email, "full_name": user.full_name},
            )
        else:
            model = UserModel.objects.create(email=user.email, full_name=user.full_name)
        return self._to_entity(model)

    def delete(self, user_id: int) -> None:
        UserModel.objects.filter(pk=user_id).delete()

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.pk,
            email=model.email,
            full_name=model.full_name,
            created_at=model.created_at,
        )
```

The private `_to_entity` method is the only place that knows both ORM models and domain entities. Keep the mapping here, not in the use case.

---

## Presentation — Serializers

```python
# presentation/serializers/user_serializers.py
from rest_framework import serializers

class CreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField(max_length=255)

class UserOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    full_name = serializers.CharField()
```

Serializers validate input format and serialize output. They never call business logic or touch the database.

---

## Presentation — APIView (for action-based endpoints)

Use when the endpoint is an action, not a resource: login, cancel, approve, generate.

```python
# presentation/views/user_views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.use_cases.create_user import CreateUserInput, CreateUserUseCase
from domain.exceptions import EmailAlreadyExists
from infrastructure.repositories.django_user_repository import DjangoUserRepository
from presentation.serializers.user_serializers import CreateUserSerializer, UserOutputSerializer

class UserCreateView(APIView):
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case = CreateUserUseCase(user_repository=DjangoUserRepository())

        try:
            output = use_case.execute(CreateUserInput(**serializer.validated_data))
        except EmailAlreadyExists as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)

        return Response(UserOutputSerializer(output).data, status=status.HTTP_201_CREATED)
```

---

## Presentation — ViewSet (for resource CRUD)

Use when the endpoint maps to a resource with standard CRUD operations.

```python
# presentation/views/user_views.py
from rest_framework import status, viewsets
from rest_framework.response import Response

from application.use_cases.create_user import CreateUserInput, CreateUserUseCase
from application.use_cases.get_user import GetUserInput, GetUserUseCase
from domain.exceptions import EmailAlreadyExists, UserNotFound
from infrastructure.repositories.django_user_repository import DjangoUserRepository
from presentation.serializers.user_serializers import CreateUserSerializer, UserOutputSerializer

class UserViewSet(viewsets.ViewSet):
    def _repo(self):
        return DjangoUserRepository()

    def create(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            output = CreateUserUseCase(self._repo()).execute(
                CreateUserInput(**serializer.validated_data)
            )
        except EmailAlreadyExists as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)

        return Response(UserOutputSerializer(output).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            output = GetUserUseCase(self._repo()).execute(GetUserInput(user_id=int(pk)))
        except UserNotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response(UserOutputSerializer(output).data)
```

---

## URLs

```python
# presentation/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from presentation.views.user_views import UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [path("", include(router.urls))]
```
