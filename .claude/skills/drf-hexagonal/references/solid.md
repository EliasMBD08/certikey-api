# SOLID Applied to DRF + Hexagonal Architecture

Each principle has a direct, concrete manifestation in this architecture. These aren't abstract rules — they're design decisions with a specific place in the codebase.

---

## S — Single Responsibility

Each class has exactly one reason to change.

| Class | Changes only when... |
|-------|----------------------|
| `UserModel` | The database schema changes |
| `DjangoUserRepository` | The persistence strategy changes |
| `CreateUserUseCase` | The business rule for creating a user changes |
| `UserCreateView` | The HTTP contract changes |
| `CreateUserSerializer` | The API input format changes |

**Violation to avoid — the fat view:**

```python
# BAD: one class doing three jobs
class UserCreateView(APIView):
    def post(self, request):
        if User.objects.filter(email=request.data["email"]).exists():  # business logic
            return Response({"error": "exists"}, status=409)
        user = User.objects.create(**request.data)  # persistence
        send_welcome_email(user)                     # side effect
        return Response({"id": user.pk})
```

**Correct: split across three classes:**

```python
# View: HTTP only
class UserCreateView(APIView):
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            output = CreateUserUseCase(DjangoUserRepository()).execute(
                CreateUserInput(**serializer.validated_data)
            )
        except EmailAlreadyExists as e:
            return Response({"detail": str(e)}, status=409)
        return Response(UserOutputSerializer(output).data, status=201)

# Use case: business rules + orchestration
class CreateUserUseCase:
    def execute(self, input_dto):
        if self._repo.get_by_email(input_dto.email):
            raise EmailAlreadyExists(...)
        user = self._repo.save(User(...))
        self._email_service.send_welcome(user.email)  # side effects belong here
        return CreateUserOutput(...)
```

---

## O — Open/Closed

Open for extension, closed for modification. New behavior is added by writing new code, not editing existing code.

**Adding a new storage backend:** write a new class, don't touch existing ones.

```python
# New requirement: cache users in Redis
class CachedUserRepository(UserRepository):
    def __init__(self, db_repo: UserRepository, cache):
        self._db = db_repo
        self._cache = cache

    def get_by_id(self, user_id: int) -> User | None:
        cached = self._cache.get(f"user:{user_id}")
        if cached:
            return cached
        user = self._db.get_by_id(user_id)
        if user:
            self._cache.set(f"user:{user_id}", user)
        return user
    # ... delegate rest to self._db
```

The use case doesn't change. The view doesn't change. Only the instantiation changes:

```python
use_case = GetUserUseCase(
    user_repository=CachedUserRepository(DjangoUserRepository(), redis_cache)
)
```

---

## L — Liskov Substitution

Any subclass of `UserRepository` must be a valid, drop-in replacement for the abstract port. Use cases must work identically regardless of which implementation they receive.

```python
# All of these are interchangeable in any use case
repo: UserRepository = DjangoUserRepository()
repo: UserRepository = InMemoryUserRepository()   # tests
repo: UserRepository = CachedUserRepository(...)  # with cache layer
```

**Signs you're violating LSP:**
- A subclass raises exceptions not declared in the interface
- A subclass silently ignores a method (e.g., `delete` does nothing)
- A subclass has different semantics (e.g., `save` doesn't persist and `get_by_id` always returns `None`)

---

## I — Interface Segregation

Don't force implementations to satisfy methods they don't need. Split large interfaces into focused, purpose-built ones.

```python
# When a use case only reads data, give it a read-only port
class ReadUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...

class WriteUserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User: ...

    @abstractmethod
    def delete(self, user_id: int) -> None: ...

# Full interface composes both for concrete implementations
class UserRepository(ReadUserRepository, WriteUserRepository, ABC): ...
```

Use cases that only read declare the narrowest dependency they need:

```python
class GetUserUseCase:
    def __init__(self, user_repository: ReadUserRepository) -> None:
        self._repo = user_repository
```

This makes it explicit at the type level that the use case will never write, and makes it easier to test or swap.

---

## D — Dependency Inversion

High-level modules (use cases) must not depend on low-level modules (Django ORM). Both depend on abstractions (the port interfaces).

**Correct:**

```python
class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository) -> None:  # abstract
        self._repo = user_repository
```

**Violation:**

```python
class CreateUserUseCase:
    def __init__(self) -> None:
        self._repo = DjangoUserRepository()  # concrete — tightly coupled to Django
```

The concrete dependency is always provided from outside (injected by the view, a DI container, or a test). This is what makes the domain layer testable without a database.
