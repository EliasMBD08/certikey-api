from rest_framework.routers import DefaultRouter
from apps.programas.presentation.views.programa_viewset import ProgramaViewSet

router = DefaultRouter()
router.register(r'programas', ProgramaViewSet, basename='programa')

urlpatterns = router.urls
