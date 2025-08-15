from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
  path("", views.index, name="index"),
   # Ruta login/ para la vista LoginView para inicio de sesión, uso de plantilla y alias
  path('login/', auth_views.LoginView.as_view(template_name='security/login.html'), name='login'),

  # Ruta logout/ para la vista LogoutView para fin de sesión, redirección y alias
  path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout')
]
...
# Fallo: acceso sin autenticación
LOGIN_URL = '/login/'

# Éxito: luego de autenticación exitosa
LOGIN_REDIRECT_URL = '/'