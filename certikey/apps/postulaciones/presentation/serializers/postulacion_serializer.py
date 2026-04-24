from rest_framework import serializers


class CreatePostulacionSerializer(serializers.Serializer):
    programa_id = serializers.IntegerField()
    mensaje = serializers.CharField(allow_blank=True, required=False, default='')


class PostulacionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    estudiante_id = serializers.IntegerField(read_only=True)
    programa_id = serializers.IntegerField(read_only=True)
    estado_slug = serializers.CharField(read_only=True)
    mensaje = serializers.CharField(read_only=True)
    fecha_postulacion = serializers.DateTimeField(read_only=True)
