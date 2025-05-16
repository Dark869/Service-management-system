#Agregar aqui todos los archivos de rutas creados

from django.urls import path
from services_management_system.views import index, login

urlpatterns = [
    path('', index.index, name='index'),
    path('login/', login.login, name='login'),
]