# Entidades — Certikey API

> **Base compartida (`ModeloBase`):** `fecha_creacion`, `fecha_actualizacion`, `activo` (soft delete).
> Las entidades que no lo indican heredan de `models.Model` (catálogos de referencia).

---

## App: `catalogos`

Datos de referencia del sistema. Solo lectura desde la API pública.

### Pais
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| nombre | CharField(100) | unique |
| codigo_iso | CharField(3) | unique |

### Ciudad
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| pais | FK → Pais | CASCADE |
| nombre | CharField(100) | unique_together con pais |

### Moneda
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| nombre | CharField(50) | |
| codigo_iso | CharField(5) | unique |
| simbolo | CharField(5) | |

### Rol
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| nombre | CharField(50) | unique |
| slug | SlugField | unique |
| descripcion | CharField(255) | |
| es_publico | Boolean | default True |

> Slugs del sistema: `admin`, `certificadora`, `estudiante`

### TipoPrograma
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| nombre | CharField(100) | unique |
| slug | SlugField | unique |
| descripcion | TextField | |
| activo | Boolean | default True |

### Modalidad
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| nombre | CharField(100) | unique |
| slug | SlugField | unique |
| descripcion | CharField(255) | |

### NivelAcademico
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| nombre | CharField(100) | unique |
| slug | SlugField | unique |
| orden | PositiveSmallIntegerField | para ordenar |

### EstadoPrograma
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| nombre | CharField(50) | unique |
| slug | SlugField | unique |
| descripcion | CharField(255) | |
| es_visible_publico | Boolean | controla visibilidad en listado |

> Slugs del sistema: `borrador`, `publicado`, `pausado`, `archivado`

### EstadoVerificacion
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| nombre | CharField(50) | unique |
| slug | SlugField | unique |
| permite_publicar | Boolean | habilita crear programas |

> Slugs del sistema: `pendiente`, `verificada`, `suspendida`

### Categoria
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| nombre | CharField(100) | unique |
| slug | SlugField | unique |
| icono | CharField(50) | nombre del ícono (ej. FontAwesome) |
| descripcion | TextField | |
| activa | Boolean | default True |

> Usada para el **match**: `PerfilEstudiante.areas_interes ∩ Programa.categorias`

### Tag
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| nombre | CharField(50) | unique |
| slug | SlugField | unique |

---

## App: `usuarios`

### Usuario *(extiende AbstractUser)*
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| username | CharField | heredado |
| email | EmailField | heredado |
| first_name | CharField | heredado |
| last_name | CharField | heredado |
| is_active | Boolean | heredado |
| date_joined | DateTimeField | heredado |
| rol | FK → Rol | PROTECT, nullable |
| telefono | CharField(20) | |
| foto_perfil | ImageField | upload: `perfiles/` |
| fecha_actualizacion | DateTimeField | auto_now |

**Métodos:** `es_admin()`, `es_certificadora()`, `es_estudiante()`

### PerfilEstudiante *(ModeloBase)*
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| usuario | OneToOne → Usuario | CASCADE |
| fecha_nacimiento | DateField | nullable |
| pais | FK → Pais | SET_NULL, nullable |
| ciudad | FK → Ciudad | SET_NULL, nullable |
| biografia | TextField | |
| **areas_interes** | M2M → Categoria | base del match con programas |
| fecha_creacion | DateTime | heredado |
| fecha_actualizacion | DateTime | heredado |
| activo | Boolean | heredado |

### PerfilCertificadora *(ModeloBase)*
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| usuario | OneToOne → Usuario | CASCADE |
| nombre_institucion | CharField(255) | |
| ruc | CharField(20) | unique |
| descripcion | TextField | |
| logo | ImageField | upload: `logos/` |
| sitio_web | URLField | |
| pais | FK → Pais | SET_NULL, nullable |
| ciudad | FK → Ciudad | SET_NULL, nullable |
| direccion | CharField(255) | |
| estado_verificacion | FK → EstadoVerificacion | PROTECT, nullable |
| fecha_verificacion | DateTimeField | nullable |
| fecha_creacion | DateTime | heredado |
| fecha_actualizacion | DateTime | heredado |
| activo | Boolean | heredado |

**Método:** `puede_publicar()` — depende de `estado_verificacion.permite_publicar`

---

## App: `programas`

### Programa *(ModeloBase)*
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| certificadora | FK → PerfilCertificadora | CASCADE |
| **categorias** | M2M → Categoria | máx 5, base del match |
| tags | M2M → Tag | |
| tipo | FK → TipoPrograma | PROTECT |
| modalidad | FK → Modalidad | PROTECT |
| nivel | FK → NivelAcademico | SET_NULL, nullable |
| estado | FK → EstadoPrograma | PROTECT |
| moneda | FK → Moneda | SET_NULL, nullable |
| titulo | CharField(255) | |
| slug | SlugField | unique |
| descripcion_corta | CharField(300) | |
| descripcion | TextField | |
| imagen_portada | ImageField | upload: `programas/` |
| duracion_horas | PositiveIntegerField | nullable |
| duracion_semanas | PositiveIntegerField | nullable |
| precio | DecimalField(10,2) | nullable |
| es_gratuito | Boolean | default False |
| otorga_certificado | Boolean | default True |
| descripcion_certificado | CharField(255) | |
| fecha_inicio | DateField | nullable |
| fecha_fin | DateField | nullable |
| inscripciones_abiertas | Boolean | default True |
| **url_inscripcion** | URLField | enlace externo — modelo nexo |
| fecha_creacion | DateTime | heredado |
| fecha_actualizacion | DateTime | heredado |
| activo | Boolean | heredado |

---

## App: `intereses`

> Representa que un estudiante guardó un programa como favorito. Es el corazón del modelo **nexo**: no hay aplicación directa, el estudiante es redirigido a `url_inscripcion`.

### Interes *(ModeloBase)*
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| estudiante | FK → PerfilEstudiante | CASCADE |
| programa | FK → Programa | CASCADE |
| fecha_creacion | DateTime | heredado |
| fecha_actualizacion | DateTime | heredado |
| activo | Boolean | soft delete = "quitar bookmark" |

**Constraint:** `unique_together(estudiante, programa)`

**Soft delete:** quitar el bookmark desactiva el registro; volver a guardarlo lo reactiva sin crear duplicados.

---

## App: `resenas`

> Reseñas públicas. Cualquier estudiante autenticado puede reseñar. Una reseña por estudiante por entidad.

### ResenaPrograma *(ModeloBase)*
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| estudiante | FK → PerfilEstudiante | CASCADE |
| programa | FK → Programa | CASCADE |
| calificacion | PositiveSmallIntegerField | 1–5 |
| comentario | TextField | |
| fecha_creacion | DateTime | heredado |
| fecha_actualizacion | DateTime | heredado |
| activo | Boolean | heredado |

**Constraint:** `unique_together(estudiante, programa)`

### ResenaCertificadora *(ModeloBase)*
| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| estudiante | FK → PerfilEstudiante | CASCADE |
| certificadora | FK → PerfilCertificadora | CASCADE |
| calificacion | PositiveSmallIntegerField | 1–5 |
| comentario | TextField | |
| fecha_creacion | DateTime | heredado |
| fecha_actualizacion | DateTime | heredado |
| activo | Boolean | heredado |

**Constraint:** `unique_together(estudiante, certificadora)`

---

## Resumen de relaciones

| Desde | Campo | Hacia | Tipo | Cardinalidad |
|---|---|---|---|---|
| Ciudad | pais | Pais | FK | N:1 |
| Usuario | rol | Rol | FK | N:1 |
| PerfilEstudiante | usuario | Usuario | OneToOne | 1:1 |
| PerfilEstudiante | pais | Pais | FK | N:1 |
| PerfilEstudiante | ciudad | Ciudad | FK | N:1 |
| PerfilEstudiante | areas_interes | Categoria | M2M | N:N |
| PerfilCertificadora | usuario | Usuario | OneToOne | 1:1 |
| PerfilCertificadora | pais | Pais | FK | N:1 |
| PerfilCertificadora | ciudad | Ciudad | FK | N:1 |
| PerfilCertificadora | estado_verificacion | EstadoVerificacion | FK | N:1 |
| Programa | certificadora | PerfilCertificadora | FK | N:1 |
| Programa | categorias | Categoria | M2M | N:N (máx 5) |
| Programa | tags | Tag | M2M | N:N |
| Programa | tipo | TipoPrograma | FK | N:1 |
| Programa | modalidad | Modalidad | FK | N:1 |
| Programa | nivel | NivelAcademico | FK | N:1 |
| Programa | estado | EstadoPrograma | FK | N:1 |
| Programa | moneda | Moneda | FK | N:1 |
| Interes | estudiante | PerfilEstudiante | FK | N:1 |
| Interes | programa | Programa | FK | N:1 |
| ResenaPrograma | estudiante | PerfilEstudiante | FK | N:1 |
| ResenaPrograma | programa | Programa | FK | N:1 |
| ResenaCertificadora | estudiante | PerfilEstudiante | FK | N:1 |
| ResenaCertificadora | certificadora | PerfilCertificadora | FK | N:1 |

---

## Lógica de match

```python
# Programas sugeridos a un estudiante según sus áreas de interés
Programa.objects.filter(
    categorias__in=estudiante.perfil_estudiante.areas_interes.all()
).distinct()
```
