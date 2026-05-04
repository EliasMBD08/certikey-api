# Certikey API — Referencia de Endpoints

Base URL: `http://localhost:8000/api/v1`  
Autenticación: `Authorization: Bearer <access_token>` (JWT)  
Paginación por defecto: `page` / `page_size` (20 por página)

---

## AUTH

### `POST /auth/register/`
Crea un nuevo usuario. Sin autenticación.

**Payload**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "secret123",
  "first_name": "John",
  "last_name": "Doe",
  "rol_slug": "estudiante"
}
```
> `rol_slug` opcional. Solo acepta roles con `es_publico=true`. Valores típicos: `"estudiante"`, `"certificadora"`.

**201**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "rol": "estudiante"
}
```
**400** — Validación fallida o `rol_slug` inválido.  
**409** — Email ya registrado.

---

### `POST /auth/login/`
Obtiene tokens JWT. Sin autenticación.

**Payload**
```json
{
  "username": "johndoe",
  "password": "secret123"
}
```

**200**
```json
{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>"
}
```
**401** — Credenciales incorrectas.

---

### `POST /auth/refresh/`
Renueva el access token.

**Payload**
```json
{
  "refresh": "<jwt_refresh_token>"
}
```

**200**
```json
{
  "access": "<new_jwt_access_token>"
}
```
**401** — Refresh token inválido o expirado.

---

## USUARIOS

### `GET /usuarios/me/`
Retorna el usuario autenticado y su perfil según rol. Requiere auth.

**200 — Estudiante**
```json
{
  "usuario": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "rol": "estudiante"
  },
  "perfil": {
    "id": 1,
    "usuario_id": 1,
    "fecha_nacimiento": "1999-05-15",
    "pais_id": 2,
    "ciudad_id": 10,
    "biografia": "...",
    "areas_interes_ids": [1, 3]
  }
}
```

**200 — Certificadora**
```json
{
  "usuario": {
    "id": 2,
    "email": "org@example.com",
    "username": "orgname",
    "first_name": "Org",
    "last_name": "Name",
    "rol": "certificadora"
  },
  "perfil": {
    "id": 1,
    "usuario_id": 2,
    "nombre_institucion": "Universidad XYZ",
    "ruc": "12345678901",
    "descripcion": "...",
    "sitio_web": "https://xyz.edu",
    "pais_id": 2,
    "ciudad_id": 10,
    "direccion": "Av. Principal 123",
    "estado_verificacion_slug": "pendiente",
    "puede_publicar": false
  }
}
```
> Si el usuario no tiene perfil creado, `"perfil": null`.

---

### `PATCH /usuarios/me/`
Actualiza el perfil del usuario autenticado según su rol. Todos los campos son opcionales.

**Payload — Estudiante**
```json
{
  "fecha_nacimiento": "1999-05-15",
  "pais_id": 2,
  "ciudad_id": 10,
  "biografia": "Soy estudiante de ingeniería.",
  "areas_interes_ids": [1, 3, 5]
}
```

**Payload — Certificadora**
```json
{
  "nombre_institucion": "Universidad XYZ",
  "ruc": "12345678901",
  "descripcion": "Institución acreditada.",
  "sitio_web": "https://xyz.edu",
  "pais_id": 2,
  "ciudad_id": 10,
  "direccion": "Av. Principal 123"
}
```

**200** — Perfil actualizado (misma estructura que el `perfil` en `GET /me/`).  
**400** — Rol sin perfil editable (ej. admin).  
**404** — Perfil no encontrado.

---

## CATALOGOS

Todos los endpoints de catálogos son **solo lectura** (`GET list` y `GET detail`) y no requieren autenticación.

### `GET /catalogos/paises/`
**200**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/v1/catalogos/paises/?page=3",
  "previous": "http://localhost:8000/api/v1/catalogos/paises/?page=1",
  "results": [
    { "id": 1, "nombre": "Perú", "codigo_iso": "PER" },
    { "id": 2, "nombre": "Colombia", "codigo_iso": "COL" }
  ]
}
```

### `GET /catalogos/paises/{id}/`
```json
{ "id": 1, "nombre": "Perú", "codigo_iso": "PER" }
```

---

### `GET /catalogos/ciudades/`
Query params: `?pais=<id>` (filtro por país)

**200**
```json
{
  "count": 120,
  "next": "http://localhost:8000/api/v1/catalogos/ciudades/?page=3",
  "previous": "http://localhost:8000/api/v1/catalogos/ciudades/?page=1",
  "results": [
    { "id": 1, "nombre": "Lima", "pais": 1, "pais_nombre": "Perú" }
  ]
}
```

### `GET /catalogos/ciudades/{id}/`
```json
{ "id": 1, "nombre": "Lima", "pais": 1, "pais_nombre": "Perú" }
```

---

### `GET /catalogos/monedas/`
**200**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/v1/catalogos/monedas/?page=2",
  "previous": null,
  "results": [
    { "id": 1, "nombre": "Sol Peruano", "codigo_iso": "PEN", "simbolo": "S/" }
  ]
}
```

---

### `GET /catalogos/roles/`
Solo roles con `es_publico=true`.

**200**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    { "id": 1, "nombre": "Estudiante", "slug": "estudiante", "descripcion": "" },
    { "id": 2, "nombre": "Certificadora", "slug": "certificadora", "descripcion": "" }
  ]
}
> `next` y `previous` son `null` cuando no hay más páginas.
```

---

### `GET /catalogos/tipos-programa/`
Solo tipos con `activo=true`.

**200**
```json
{
  "count": 5,
  "next": "http://localhost:8000/api/v1/catalogos/tipos-programa/?page=2",
  "previous": null,
  "results": [
    { "id": 1, "nombre": "Bootcamp", "slug": "bootcamp", "descripcion": "" }
  ]
}
```

---

### `GET /catalogos/modalidades/`
**200**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    { "id": 1, "nombre": "Virtual", "slug": "virtual", "descripcion": "" }
  ]
}
```

---

### `GET /catalogos/niveles/`
**200**
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    { "id": 1, "nombre": "Básico", "slug": "basico", "orden": 1 }
  ]
}
```

---

### `GET /catalogos/categorias/`
Solo categorías con `activa=true`. Query params: `?search=<texto>`

**200**
```json
{
  "count": 30,
  "next": "http://localhost:8000/api/v1/catalogos/categorias/?page=3",
  "previous": "http://localhost:8000/api/v1/catalogos/categorias/?page=1",
  "results": [
    { "id": 1, "nombre": "Tecnología", "slug": "tecnologia", "icono": "laptop", "descripcion": "" }
  ]
}
```

---

### `GET /catalogos/tags/`
Query params: `?search=<texto>`

**200**
```json
{
  "count": 80,
  "next": "http://localhost:8000/api/v1/catalogos/tags/?page=3",
  "previous": "http://localhost:8000/api/v1/catalogos/tags/?page=1",
  "results": [
    { "id": 1, "nombre": "Python", "slug": "python" }
  ]
}
```

---

## PROGRAMAS

### `GET /programas/`
Listado público de programas. Sin autenticación.

Query params:
| Param | Tipo | Descripción |
|---|---|---|
| `categorias` | int (repetible) | ID de categoría — se puede pasar varias veces: `?categorias=1&categorias=3` |
| `tipo` | int | ID de tipo de programa |
| `modalidad` | int | ID de modalidad |
| `nivel` | int | ID de nivel académico |
| `es_gratuito` | bool | `true` / `false` |
| `inscripciones_abiertas` | bool | `true` / `false` |
| `precio_max` | decimal | Precio máximo |
| `search` | string | Búsqueda en título |

**200**
```json
[
  {
    "id": 1,
    "titulo": "Bootcamp de Python",
    "slug": "bootcamp-de-python",
    "descripcion_corta": "Aprende Python desde cero.",
    "descripcion": "...",
    "certificadora_id": 1,
    "categorias_ids": [1, 2],
    "tipo_id": 1,
    "modalidad_id": 1,
    "nivel_id": 1,
    "estado_slug": "publicado",
    "es_gratuito": false,
    "precio": "299.00",
    "moneda_id": 1,
    "duracion_horas": 120,
    "duracion_semanas": 12,
    "otorga_certificado": true,
    "descripcion_certificado": "Certificado de finalización",
    "fecha_inicio": "2025-03-01",
    "fecha_fin": "2025-05-31",
    "inscripciones_abiertas": true,
    "url_inscripcion": "https://xyz.edu/inscripcion",
    "tags_ids": [1, 2],
    "fecha_creacion": "2025-01-15T10:00:00Z"
  }
]
```

---

### `GET /programas/{id}/`
Sin autenticación.

**200** — Mismo objeto que un ítem del listado.  
**404** — Programa no encontrado.

---

### `POST /programas/`
Crea un programa. Requiere rol `certificadora`.

**Payload**
```json
{
  "titulo": "Bootcamp de Python",
  "slug": "bootcamp-de-python",
  "descripcion_corta": "Aprende Python desde cero.",
  "descripcion": "Contenido detallado del curso...",
  "tipo_id": 1,
  "modalidad_id": 1,
  "categorias_ids": [1, 2],
  "nivel_id": 1,
  "es_gratuito": false,
  "precio": "299.00",
  "moneda_id": 1,
  "duracion_horas": 120,
  "duracion_semanas": 12,
  "otorga_certificado": true,
  "descripcion_certificado": "Certificado de finalización",
  "fecha_inicio": "2025-03-01",
  "fecha_fin": "2025-05-31",
  "inscripciones_abiertas": true,
  "url_inscripcion": "https://xyz.edu/inscripcion",
  "tags_ids": [1, 2]
}
```
> Campos opcionales: `categorias_ids` (máx 5), `nivel_id`, `precio`, `moneda_id`, `duracion_horas`, `duracion_semanas`, `descripcion_certificado`, `fecha_inicio`, `fecha_fin`, `url_inscripcion`, `tags_ids`.

**201** — Objeto programa creado (misma estructura que el GET).  
**403** — Certificadora no verificada.  
**422** — Se superó el límite de 5 categorías.

---

### `PATCH /programas/{id}/`
Actualiza parcialmente un programa propio. Requiere rol `certificadora`.

**Payload** (todos los campos opcionales)
```json
{
  "titulo": "Nuevo título",
  "descripcion_corta": "Nueva descripción corta.",
  "descripcion": "...",
  "categorias_ids": [2, 3],
  "nivel_id": 2,
  "es_gratuito": true,
  "precio": null,
  "moneda_id": null,
  "duracion_horas": 80,
  "duracion_semanas": 8,
  "fecha_inicio": "2025-04-01",
  "fecha_fin": "2025-06-30",
  "inscripciones_abiertas": true,
  "url_inscripcion": "https://xyz.edu/nueva-inscripcion",
  "tags_ids": [3]
}
```

**200** — Objeto programa actualizado.  
**403** — No es el propietario del programa.  
**404** — Programa no encontrado.  
**422** — Se superó el límite de 5 categorías.

---

### `POST /programas/{id}/publicar/`
Publica un programa en estado borrador. Requiere rol `certificadora`.

Sin payload.

**200** — Objeto programa con `estado_slug: "publicado"`.  
**403** — No es el propietario o certificadora no verificada.  
**404** — Programa no encontrado.  
**409** — El programa ya está publicado.

---

## INTERESES

> Representa que un estudiante guardó un programa como favorito (bookmark). El estudiante es redirigido a `url_inscripcion` del programa — no hay postulación directa.

Todos los endpoints requieren rol `estudiante`.

### `GET /intereses/`
Lista los programas guardados del estudiante autenticado.

**200**
```json
[
  {
    "id": 1,
    "estudiante_id": 1,
    "programa_id": 5,
    "fecha_creacion": "2025-02-01T14:30:00Z"
  }
]
```

---

### `POST /intereses/`
Guarda un programa como favorito.

**Payload**
```json
{
  "programa_id": 5
}
```

**201**
```json
{
  "id": 1,
  "estudiante_id": 1,
  "programa_id": 5,
  "fecha_creacion": "2025-02-01T14:30:00Z"
}
```
**409** — El programa ya está guardado.

---

### `GET /intereses/{programa_id}/`
Verifica si el estudiante ya guardó un programa específico.

**200**
```json
{ "guardado": true }
```

---

### `DELETE /intereses/{programa_id}/`
Quita un programa de guardados (soft delete).

**204** — Sin contenido.  
**404** — El interés no existe o ya fue eliminado.

---

## RESEÑAS

> Cualquier estudiante autenticado puede reseñar. Una reseña por estudiante por entidad. Los listados son públicos.

### `GET /resenas/programas/`
Lista las reseñas de un programa. Sin autenticación.

Query params:
| Param | Tipo | Descripción |
|---|---|---|
| `programa_id` | int | **Requerido** — ID del programa a consultar |

**200**
```json
[
  {
    "id": 1,
    "estudiante_id": 1,
    "programa_id": 5,
    "calificacion": 4,
    "comentario": "Excelente programa, muy bien estructurado.",
    "fecha_creacion": "2025-03-10T09:00:00Z"
  }
]
```
**400** — Falta el parámetro `programa_id`.

---

### `POST /resenas/programas/`
Crea una reseña de un programa. Requiere rol `estudiante`.

**Payload**
```json
{
  "programa_id": 5,
  "calificacion": 4,
  "comentario": "Excelente programa, muy bien estructurado."
}
```
> `calificacion`: entero entre 1 y 5.

**201** — Objeto reseña creado (misma estructura que un ítem del listado).  
**409** — El estudiante ya reseñó este programa.  
**422** — Calificación fuera del rango permitido (1–5).

---

### `GET /resenas/certificadoras/`
Lista las reseñas de una certificadora. Sin autenticación.

Query params:
| Param | Tipo | Descripción |
|---|---|---|
| `certificadora_id` | int | **Requerido** — ID del perfil certificadora |

**200**
```json
[
  {
    "id": 1,
    "estudiante_id": 1,
    "certificadora_id": 2,
    "calificacion": 5,
    "comentario": "Institución muy confiable.",
    "fecha_creacion": "2025-03-15T11:00:00Z"
  }
]
```
**400** — Falta el parámetro `certificadora_id`.

---

### `POST /resenas/certificadoras/`
Crea una reseña de una certificadora. Requiere rol `estudiante`.

**Payload**
```json
{
  "certificadora_id": 2,
  "calificacion": 5,
  "comentario": "Institución muy confiable."
}
```
> `calificacion`: entero entre 1 y 5.

**201** — Objeto reseña creado (misma estructura que un ítem del listado).  
**409** — El estudiante ya reseñó esta certificadora.  
**422** — Calificación fuera del rango permitido (1–5).
