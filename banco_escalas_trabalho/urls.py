from django.contrib import admin
from django.urls import include, path
from .views import *


urlpatterns = [
    path('', home_view, name='template_home'), 
    path('cadastrar_departamento', cadastrar_departamento_view, name='cadastrar_departamento'),
    path('cadastrar_cargo', cadastrar_cargo_view, name='cadastrar_cargo'), 
    path('visualizar_funcionario/<int:id>/', visualizar_funcionario_view, name='visualizar_funcionario'), 
    path('cadastrar_funcionario', cadastrar_funcionario_view, name='cadastrar_funcionario'), 
    path('visualizar_adicionar_semanas', visualizar_adicionar_semanas_view, name='visualizar_adicionar_semanas'),
    path('cadastrar_escala', cadastrar_escala_view, name='cadastrar_escala'),
    path('excluir_escala', excluir_escala_view, name='excluir_escala'),
    #path('visualizar_adicionar_semanas', visualizar_adicionar_semanas_view, name='visualizar_adicionar_semanas'),
]
