from rest_framework.routers import DefaultRouter

from apps.resenas.presentation.views.resena_programa_viewset import ResenaProgramaViewSet
from apps.resenas.presentation.views.resena_certificadora_viewset import ResenaCertificadoraViewSet

router = DefaultRouter()
router.register(r'resenas/programas', ResenaProgramaViewSet, basename='resena-programa')
router.register(r'resenas/certificadoras', ResenaCertificadoraViewSet, basename='resena-certificadora')

urlpatterns = router.urls
