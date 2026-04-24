from rest_framework import serializers
from apps.catalogos.infrastructure.models import (
    Pais, Ciudad, Moneda, Rol, TipoPrograma, Modalidad,
    NivelAcademico, EstadoPrograma, EstadoVerificacion,
    EstadoPostulacion, Categoria, Tag,
)


class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pais
        fields = ['id', 'nombre', 'codigo_iso']


class CiudadSerializer(serializers.ModelSerializer):
    pais_nombre = serializers.CharField(source='pais.nombre', read_only=True)

    class Meta:
        model = Ciudad
        fields = ['id', 'nombre', 'pais', 'pais_nombre']


class MonedaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moneda
        fields = ['id', 'nombre', 'codigo_iso', 'simbolo']


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'slug', 'descripcion']


class TipoProgramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPrograma
        fields = ['id', 'nombre', 'slug', 'descripcion']


class ModalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modalidad
        fields = ['id', 'nombre', 'slug', 'descripcion']


class NivelAcademicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NivelAcademico
        fields = ['id', 'nombre', 'slug', 'orden']


class EstadoProgramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoPrograma
        fields = ['id', 'nombre', 'slug']


class EstadoVerificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoVerificacion
        fields = ['id', 'nombre', 'slug']


class EstadoPostulacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoPostulacion
        fields = ['id', 'nombre', 'slug', 'descripcion']


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'slug', 'icono', 'descripcion']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'nombre', 'slug']
