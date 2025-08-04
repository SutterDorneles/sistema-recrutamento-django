from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_vagas, name='lista_vagas'),
    path('vaga/<int:vaga_id>/', views.detalhes_vaga, name='detalhes_vaga'),
    path('vaga/<int:vaga_id>/candidatar/', views.candidatar, name='candidatar'),
    
    # **NOVA ROTA ADICIONADA**
    # Rota para a página de confirmação após a candidatura.
    path('vaga/<int:vaga_id>/confirmacao/', views.confirmacao, name='confirmacao'),
    path('candidato/<int:candidato_id>/teste/', views.realizar_teste, name='realizar_teste'),
]
