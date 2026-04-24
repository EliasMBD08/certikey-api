from django.urls import path
from apps.usuarios.presentation.views.profile_view import ProfileView

urlpatterns = [
    path('me/', ProfileView.as_view(), name='usuario-me'),
]
