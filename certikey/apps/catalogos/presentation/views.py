from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from apps.catalogos.infrastructure.models import (
    Pais, Ciudad, Moneda, Rol, TipoPrograma, Modalidad,
    NivelAcademico, Categoria, Tag,
)
from apps.catalogos.presentation.serializers import (
    PaisSerializer, CiudadSerializer, MonedaSerializer, RolSerializer,
    TipoProgramaSerializer, ModalidadSerializer, NivelAcademicoSerializer,
    CategoriaSerializer, TagSerializer,
)


class PaisViewSet(ReadOnlyModelViewSet):
    queryset = Pais.objects.all()
    serializer_class = PaisSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    search_fields = ['nombre']


class CiudadViewSet(ReadOnlyModelViewSet):
    queryset = Ciudad.objects.select_related('pais').all()
    serializer_class = CiudadSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['pais']


class MonedaViewSet(ReadOnlyModelViewSet):
    queryset = Moneda.objects.all()
    serializer_class = MonedaSerializer
    permission_classes = [AllowAny]


class RolViewSet(ReadOnlyModelViewSet):
    queryset = Rol.objects.filter(es_publico=True)
    serializer_class = RolSerializer
    permission_classes = [AllowAny]


class TipoProgramaViewSet(ReadOnlyModelViewSet):
    queryset = TipoPrograma.objects.filter(activo=True)
    serializer_class = TipoProgramaSerializer
    permission_classes = [AllowAny]


class ModalidadViewSet(ReadOnlyModelViewSet):
    queryset = Modalidad.objects.all()
    serializer_class = ModalidadSerializer
    permission_classes = [AllowAny]


class NivelAcademicoViewSet(ReadOnlyModelViewSet):
    queryset = NivelAcademico.objects.all()
    serializer_class = NivelAcademicoSerializer
    permission_classes = [AllowAny]


class CategoriaViewSet(ReadOnlyModelViewSet):
    queryset = Categoria.objects.filter(activa=True)
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]
    search_fields = ['nombre']


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    search_fields = ['nombre']
