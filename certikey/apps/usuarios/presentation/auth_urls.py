from django.urls import path
from apps.usuarios.presentation.views.register_view import RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
]
