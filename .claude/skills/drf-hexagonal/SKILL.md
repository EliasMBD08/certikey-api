---
name: drf-hexagonal
description: Guides writing Django REST Framework (DRF) code following hexagonal architecture (ports & adapters), SOLID principles, and decoupled domain logic. Use this skill whenever the user is working on any Django or DRF feature — creating APIs, adding endpoints, writing models, views, serializers, services, or structuring a Django application. Also trigger for keywords like "clean architecture", "hexagonal", "use cases", "repositories", "domain logic", "decoupling", "SOLID", "dependency injection", "ports and adapters" in a Django/Python context. This skill should be consulted before generating any DRF code, even for small features.
---

# DRF + Hexagonal Architecture

## Core philosophy

Business logic must be independent of frameworks, databases, and HTTP. Django and DRF are *delivery mechanisms* — they sit at the edges of the system, not the center. The domain knows nothing about Django.

Dependencies always point inward:

```
Presentation → Application → Domain ← Infrastructure (implements)
```

The domain defines abstract ports (interfaces). Infrastructure provides concrete adapters. The application orchestrates via use cases. The presentation handles only HTTP.

## Folder structure

```
<app_name>/
├── domain/
│   ├── entities/          # Pure Python dataclasses — zero external imports
│   ├── repositories/      # Abstract interfaces (ports) — ABCs only
│   ├── services/          # Domain logic that doesn't belong to a single entity
│   └── exceptions.py      # Named business exceptions
├── application/
│   ├── use_cases/         # One class per use case, one public method (execute)
│   └── dtos/              # Input/output dataclasses for use cases
├── infrastructure/
│   ├── models.py          # Django ORM models (infrastructure detail, not domain)
│   ├── repositories/      # Concrete repository implementations (adapters)
│   └── external/          # Third-party API adapters
└── presentation/
    ├── views/             # DRF ViewSets or APIViews — HTTP in/out only
    ├── serializers/       # DRF Serializers — validation and serialization only
    └── urls.py
```

## Layer responsibilities

| Layer | Responsibility | May import Django? |
|-------|---------------|-------------------|
| **domain** | Business rules, entities, abstract ports | Never |
| **application** | Orchestrates use cases, calls domain | Never |
| **infrastructure** | ORM models, concrete repos, external services | Yes |
| **presentation** | HTTP handling, serialization, routing | Yes (DRF) |

## ViewSet vs APIView — when to use each

**ViewSet** (with router): when the endpoint maps to a resource with standard CRUD operations (list, retrieve, create, update, destroy). Results in clean, predictable URL patterns.

**APIView**: when the endpoint represents an action that doesn't map to a resource (e.g., `POST /auth/login`, `POST /orders/{id}/cancel`, `POST /reports/generate`).

Both must remain thin: validate input via serializer → call use case → return response. No business logic ever lives in a view.

## Dependency injection

For most projects, **manual instantiation in the view** is the right approach — simple, explicit, and easy to follow:

```python
use_case = CreateUserUseCase(user_repository=DjangoUserRepository())
```

Only reach for `dependency-injector` (the library) when the project has many use cases sharing a complex graph of shared dependencies.

## DTOs

Use `dataclasses` for all input and output DTOs. Keep them in the same file as the use case:

```python
@dataclass
class CreateUserInput:
    email: str
    full_name: str

@dataclass
class CreateUserOutput:
    id: int
    email: str
    full_name: str
```

## Error handling pattern

Domain raises named exceptions. The presentation layer translates them to HTTP responses. Never catch domain exceptions in use cases or repositories.

```python
try:
    output = use_case.execute(input_dto)
except EmailAlreadyExists as e:
    return Response({"detail": str(e)}, status=HTTP_409_CONFLICT)
except UserNotFound as e:
    return Response({"detail": str(e)}, status=HTTP_404_NOT_FOUND)
```

## Common pitfalls

- **Fat serializers**: serializers that contain business logic — keep validation only
- **Fat ORM models**: Django models with business methods — domain entities handle behavior
- **Fat views**: views that query the DB directly or contain business conditionals — use cases own that
- **Leaking Django into domain**: importing anything from `django` inside `domain/` — you have crossed a boundary
- **Anemic use cases**: use cases that only forward a call to the repository with no logic — acceptable for simple CRUD, but add an explicit comment so it's intentional

## Reference files

Load these only when needed for the current task:

- **`references/patterns.md`** — Full, copy-paste-ready code examples for every layer: entities, repository interfaces, use cases, Django ORM models, concrete repositories, serializers, APIViews, and ViewSets
- **`references/solid.md`** — SOLID principles applied concretely to this architecture, with examples of violations and correct implementations
- **`references/testing.md`** — Read this **only when the user explicitly asks to write tests**: in-memory repositories, use case unit tests, repository integration tests, and view tests with APIClient
