from rest_framework import serializers


class ProgramaSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    titulo = serializers.CharField(max_length=255)
    slug = serializers.SlugField()
    descripcion_corta = serializers.CharField(max_length=300)
    descripcion = serializers.CharField()
    certificadora_id = serializers.IntegerField(read_only=True)
    categorias_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list,
        max_length=5,
    )
    tipo_id = serializers.IntegerField()
    modalidad_id = serializers.IntegerField()
    nivel_id = serializers.IntegerField(allow_null=True, required=False)
    estado_slug = serializers.CharField(read_only=True)
    es_gratuito = serializers.BooleanField(default=False)
    precio = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    moneda_id = serializers.IntegerField(allow_null=True, required=False)
    duracion_horas = serializers.IntegerField(allow_null=True, required=False)
    duracion_semanas = serializers.IntegerField(allow_null=True, required=False)
    otorga_certificado = serializers.BooleanField(default=True)
    descripcion_certificado = serializers.CharField(allow_blank=True, required=False)
    fecha_inicio = serializers.DateField(allow_null=True, required=False)
    fecha_fin = serializers.DateField(allow_null=True, required=False)
    inscripciones_abiertas = serializers.BooleanField(default=True)
    url_inscripcion = serializers.URLField(allow_blank=True, required=False)
    tags_ids = serializers.ListField(child=serializers.IntegerField(), required=False, default=list)
    fecha_creacion = serializers.DateTimeField(read_only=True)


class ProgramaUpdateSerializer(serializers.Serializer):
    titulo = serializers.CharField(max_length=255, required=False)
    descripcion_corta = serializers.CharField(max_length=300, required=False)
    descripcion = serializers.CharField(required=False)
    categorias_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        max_length=5,
    )
    nivel_id = serializers.IntegerField(allow_null=True, required=False)
    es_gratuito = serializers.BooleanField(required=False)
    precio = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    moneda_id = serializers.IntegerField(allow_null=True, required=False)
    duracion_horas = serializers.IntegerField(allow_null=True, required=False)
    duracion_semanas = serializers.IntegerField(allow_null=True, required=False)
    fecha_inicio = serializers.DateField(allow_null=True, required=False)
    fecha_fin = serializers.DateField(allow_null=True, required=False)
    inscripciones_abiertas = serializers.BooleanField(required=False)
    url_inscripcion = serializers.URLField(allow_blank=True, required=False)
    tags_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
