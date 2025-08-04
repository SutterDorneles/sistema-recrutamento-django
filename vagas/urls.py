from django.urls import path
from . import views

urlpatterns = [
    # A página inicial agora aponta para a lista de empresas
    path('', views.lista_empresas, name='lista_empresas'),
    
    # A URL da lista de vagas agora inclui o ID da empresa
    path('empresa/<int:empresa_id>/vagas/', views.lista_vagas, name='lista_vagas'),
    
    # As outras URLs continuam as mesmas
    path('vaga/<int:vaga_id>/', views.detalhes_vaga, name='detalhes_vaga'),
    path('vaga/<int:vaga_id>/candidatar/', views.candidatar, name='candidatar'),
    path('candidato/<int:candidato_id>/teste/', views.realizar_teste, name='realizar_teste'),
    path('vaga/<int:vaga_id>/confirmacao/', views.confirmacao, name='confirmacao'),
]
