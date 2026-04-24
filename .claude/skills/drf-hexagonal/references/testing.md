# Testing Strategy

Only read this file when the user explicitly asks to write tests.

## Philosophy

Each layer has a distinct testing strategy that matches its nature:

| Layer | Test type | Uses DB? | Uses Django? |
|-------|-----------|----------|-------------|
| **domain** | Unit | No | No |
| **application** | Unit (in-memory repo) | No | No |
| **infrastructure** | Integration | Yes | Yes |
| **presentation** | Integration (APIClient) | Yes | Yes |

Test use cases first — they are the most valuable tests because they exercise business logic without any infrastructure overhead.

---

## In-memory repository

The in-memory repository is a fake adapter that satisfies the port interface. It lets you test use cases at full speed, without a database, without Django.

```python
# tests/fakes/in_memory_user_repository.py
from dataclasses import replace
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository

class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._store: dict[int, User] = {}
        self._counter = 1

    def get_by_id(self, user_id: int) -> User | None:
        return self._store.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._store.values() if u.email == email), None)

    def save(self, user: User) -> User:
        if not user.id:
            user = replace(user, id=self._counter)
            self._counter += 1
        self._store[user.id] = user
        return user

    def delete(self, user_id: int) -> None:
        self._store.pop(user_id, None)
```

---

## Use case unit tests

Fast, no fixtures, no database. Test business rules and edge cases here.

```python
# tests/unit/test_create_user.py
import pytest
from application.use_cases.create_user import CreateUserInput, CreateUserUseCase
from domain.exceptions import EmailAlreadyExists
from tests.fakes.in_memory_user_repository import InMemoryUserRepository

class TestCreateUserUseCase:
    def setup_method(self):
        self.repo = InMemoryUserRepository()
        self.use_case = CreateUserUseCase(user_repository=self.repo)

    def test_creates_user_successfully(self):
        output = self.use_case.execute(CreateUserInput(email="ana@example.com", full_name="Ana"))

        assert output.id is not None
        assert output.email == "ana@example.com"
        assert output.full_name == "Ana"

    def test_persists_user_in_repository(self):
        output = self.use_case.execute(CreateUserInput(email="ana@example.com", full_name="Ana"))

        stored = self.repo.get_by_id(output.id)
        assert stored is not None
        assert stored.email == "ana@example.com"

    def test_raises_if_email_already_exists(self):
        self.use_case.execute(CreateUserInput(email="ana@example.com", full_name="Ana"))

        with pytest.raises(EmailAlreadyExists):
            self.use_case.execute(CreateUserInput(email="ana@example.com", full_name="Other"))
```

---

## Repository integration tests

Verify the concrete Django implementation against a real (test) database. Mark with `@pytest.mark.django_db`.

```python
# tests/integration/test_django_user_repository.py
import pytest
from domain.entities.user import User
from infrastructure.repositories.django_user_repository import DjangoUserRepository

@pytest.mark.django_db
class TestDjangoUserRepository:
    def setup_method(self):
        self.repo = DjangoUserRepository()

    def test_saves_and_retrieves_by_id(self):
        user = self.repo.save(User(email="ana@example.com", full_name="Ana"))

        found = self.repo.get_by_id(user.id)
        assert found is not None
        assert found.email == "ana@example.com"

    def test_saves_and_retrieves_by_email(self):
        self.repo.save(User(email="ana@example.com", full_name="Ana"))

        found = self.repo.get_by_email("ana@example.com")
        assert found is not None

    def test_returns_none_for_missing_id(self):
        assert self.repo.get_by_id(99999) is None

    def test_returns_none_for_missing_email(self):
        assert self.repo.get_by_email("nobody@example.com") is None

    def test_updates_existing_user(self):
        user = self.repo.save(User(email="ana@example.com", full_name="Ana"))
        from dataclasses import replace
        updated = self.repo.save(replace(user, full_name="Ana Updated"))

        assert updated.id == user.id
        assert updated.full_name == "Ana Updated"

    def test_deletes_user(self):
        user = self.repo.save(User(email="ana@example.com", full_name="Ana"))
        self.repo.delete(user.id)

        assert self.repo.get_by_id(user.id) is None
```

---

## View tests (presentation layer)

Use DRF's `APIClient` to test the full HTTP contract. These tests go through the real stack including serializers, use cases, and infrastructure.

```python
# tests/integration/test_user_views.py
import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestUserCreateView:
    def setup_method(self):
        self.client = APIClient()

    def test_creates_user_and_returns_201(self):
        response = self.client.post(
            "/api/users/",
            {"email": "ana@example.com", "full_name": "Ana"},
            format="json",
        )

        assert response.status_code == 201
        assert response.data["email"] == "ana@example.com"
        assert "id" in response.data

    def test_returns_409_on_duplicate_email(self):
        payload = {"email": "ana@example.com", "full_name": "Ana"}
        self.client.post("/api/users/", payload, format="json")

        response = self.client.post("/api/users/", payload, format="json")
        assert response.status_code == 409

    def test_returns_400_on_invalid_email(self):
        response = self.client.post(
            "/api/users/",
            {"email": "not-an-email", "full_name": "Ana"},
            format="json",
        )
        assert response.status_code == 400
```

---

## conftest.py setup (pytest + Django)

```python
# conftest.py (project root)
import django
from django.conf import settings

def pytest_configure():
    settings.configure(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "<your_app>.infrastructure",  # adjust to your app name
        ],
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    )
```

Or use `pytest-django` with a `pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
```
