from rest_framework import serializers


class PerfilEstudianteSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    usuario_id = serializers.IntegerField(read_only=True)
    fecha_nacimiento = serializers.DateField(allow_null=True, required=False)
    pais_id = serializers.IntegerField(allow_null=True, required=False)
    ciudad_id = serializers.IntegerField(allow_null=True, required=False)
    biografia = serializers.CharField(allow_blank=True, required=False)
    areas_interes_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )


class PerfilCertificadoraSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    usuario_id = serializers.IntegerField(read_only=True)
    nombre_institucion = serializers.CharField(required=False)
    ruc = serializers.CharField(required=False, allow_blank=True)
    descripcion = serializers.CharField(allow_blank=True, required=False)
    sitio_web = serializers.URLField(allow_blank=True, required=False)
    pais_id = serializers.IntegerField(allow_null=True, required=False)
    ciudad_id = serializers.IntegerField(allow_null=True, required=False)
    direccion = serializers.CharField(allow_blank=True, required=False)
    estado_verificacion_slug = serializers.CharField(read_only=True)
    puede_publicar = serializers.BooleanField(read_only=True)
