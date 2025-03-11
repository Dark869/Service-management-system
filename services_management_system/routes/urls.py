#Agregar aqui todos los archivos de rutas creados

from django.urls import path
from ..views import index

urlpatterns = [
    path('', index.index, name='index'),
]