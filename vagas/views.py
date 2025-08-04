# Em vagas/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import (
    Vaga, Candidato, Inscricao, Pergunta, RespostaCandidato, Empresa
)
from .forms import CandidaturaForm
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, Count


# --- NOVA VIEW PARA A PÁGINA INICIAL ---
def lista_empresas(request):
    """
    Esta é a nova página inicial. Ela busca todas as empresas
    e as exibe.
    """
    empresas = Empresa.objects.all()
    contexto = {
        'empresas': empresas,
        'titulo_pagina': 'Escolha uma Empresa'
    }
    return render(request, 'vagas/lista_empresas.html', contexto)
# -----------------------------------------

# --- VIEW DE VAGAS ATUALIZADA ---
def lista_vagas(request, empresa_id):
    """
    Esta view agora mostra apenas as vagas de uma empresa específica.
    """
    empresa = get_object_or_404(Empresa, id=empresa_id)
    query = request.GET.get('q')
    
    # Filtramos as vagas para pertencerem apenas à empresa selecionada
    vagas = Vaga.objects.filter(empresa=empresa).order_by('-data_criacao')
    
    if query:
        vagas = vagas.filter(
            Q(titulo__icontains=query) |
            Q(descricao__icontains=query) |
            Q(requisitos__icontains=query)
        )
        
    contexto = {
        'vagas': vagas,
        'empresa': empresa, # Enviamos a empresa para o template
        'titulo_pagina': f'Vagas em {empresa.nome}'
    }
    return render(request, 'vagas/lista_vagas.html', contexto)

def calcular_e_salvar_perfil(candidato):
    """
    Calcula o perfil comportamental do candidato com base nas suas respostas.
    """
    contagem_perfis = RespostaCandidato.objects.filter(
        candidato=candidato
    ).values(
        'perfil_escolhido'
    ).annotate(
        total=Count('perfil_escolhido')
    )
    perfil = {'I': 0, 'C': 0, 'A': 0, 'O': 0}
    for item in contagem_perfis:
        if item['perfil_escolhido'] in perfil:
            perfil[item['perfil_escolhido']] = item['total']

    candidato.total_i = perfil['I']
    candidato.total_c = perfil['C']
    candidato.total_a = perfil['A']
    candidato.total_o = perfil['O']

    # --- CÁLCULO DINÂMICO DA PERCENTAGEM ---
    total_respostas = sum(perfil.values())

    def calcular_percentual(valor, total):
        if total == 0:
            return 0
        return round((valor / total) * 100)

    mapa_perfis = {
        'I': f"Águia ({calcular_percentual(perfil['I'], total_respostas)}%)",
        'C': f"Gato ({calcular_percentual(perfil['C'], total_respostas)}%)",
        'A': f"Tubarão ({calcular_percentual(perfil['A'], total_respostas)}%)",
        'O': f"Lobo ({calcular_percentual(perfil['O'], total_respostas)}%)",
    }
    # --- FIM DA ALTERAÇÃO ---

    if perfil and any(perfil.values()):
        perfil_max = max(perfil, key=perfil.get)
        candidato.perfil_comportamental = mapa_perfis[perfil_max]
    else:
        candidato.perfil_comportamental = "Indefinido"

    candidato.save()

def detalhes_vaga(request, vaga_id):
    vaga = get_object_or_404(Vaga, id=vaga_id)
    # CORREÇÃO: Adicionado o caminho 'vagas/'
    return render(request, 'vagas/detalhes_vaga.html', {'vaga': vaga})

def candidatar(request, vaga_id):
    vaga = get_object_or_404(Vaga, id=vaga_id)
    if request.method == 'POST':
        form = CandidaturaForm(request.POST, request.FILES)
        if form.is_valid():
            email_candidato = form.cleaned_data['email']
            candidato, created = Candidato.objects.get_or_create(
                email=email_candidato,
                defaults=form.cleaned_data
            )
            if not Inscricao.objects.filter(vaga=vaga, candidato=candidato).exists():
                Inscricao.objects.create(vaga=vaga, candidato=candidato)
            return redirect('realizar_teste', candidato_id=candidato.id)
    else:
        form = CandidaturaForm()
    # CORREÇÃO: Adicionado o caminho 'vagas/'
    return render(request, 'vagas/formulario_candidatura.html', {'vaga': vaga, 'form': form})

def realizar_teste(request, candidato_id):
    candidato = get_object_or_404(Candidato, id=candidato_id)
    perguntas = Pergunta.objects.filter(ativo=True)

    if request.method == 'POST':
        for pergunta in perguntas:
            perfil_escolhido = request.POST.get(f'pergunta_{pergunta.id}')
            if perfil_escolhido:
                RespostaCandidato.objects.update_or_create(
                    candidato=candidato,
                    pergunta=pergunta,
                    defaults={'perfil_escolhido': perfil_escolhido}
                )
        
        calcular_e_salvar_perfil(candidato)

        ultima_inscricao = Inscricao.objects.filter(candidato=candidato).latest('data_inscricao')
        return redirect('confirmacao', vaga_id=ultima_inscricao.vaga.id)

    contexto = {
        'candidato': candidato,
        'perguntas': perguntas,
        'titulo_pagina': 'Teste de Perfil Comportamental'
    }
    # CORREÇÃO: Adicionado o caminho 'vagas/'
    return render(request, 'teste_personalidade.html', contexto)

def confirmacao(request, vaga_id):
    vaga = get_object_or_404(Vaga, id=vaga_id)
    # CORREÇÃO: Adicionado o caminho 'vagas/'
    return render(request, 'vagas/confirmacao.html', {'vaga': vaga})
