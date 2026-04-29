from rest_framework import serializers


class CreateResenaProgramaSerializer(serializers.Serializer):
    programa_id = serializers.IntegerField()
    calificacion = serializers.IntegerField(min_value=1, max_value=5)
    comentario = serializers.CharField()


class ResenaProgramaSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    estudiante_id = serializers.IntegerField(read_only=True)
    programa_id = serializers.IntegerField(read_only=True)
    calificacion = serializers.IntegerField(read_only=True)
    comentario = serializers.CharField(read_only=True)
    fecha_creacion = serializers.DateTimeField(read_only=True)
