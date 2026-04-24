from rest_framework.routers import DefaultRouter
from apps.postulaciones.presentation.views.postulacion_viewset import PostulacionViewSet

router = DefaultRouter()
router.register(r'postulaciones', PostulacionViewSet, basename='postulacion')

urlpatterns = router.urls
