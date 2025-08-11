# Em vagas/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import (
    Vaga, Candidato, Inscricao, Pergunta, RespostaCandidato, Empresa
)
from .forms import CandidaturaForm
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, Count
from django.urls import reverse

def lista_empresas(request):
    empresas = Empresa.objects.all()
    contexto = {
        'empresas': empresas,
        'titulo_pagina': 'Escolha uma Empresa'
    }
    return render(request, 'vagas/lista_empresas.html', contexto)

def lista_vagas(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    query = request.GET.get('q')
    vagas = Vaga.objects.filter(empresa=empresa).order_by('-data_criacao')
    if query:
        vagas = vagas.filter(
            Q(titulo__icontains=query) |
            Q(descricao__icontains=query) |
            Q(requisitos__icontains=query)
        )
    contexto = {
        'vagas': vagas,
        'empresa': empresa,
        'titulo_pagina': f'Vagas em {empresa.nome}'
    }
    return render(request, 'vagas/lista_vagas.html', contexto)

def detalhes_vaga(request, vaga_id):
    vaga = get_object_or_404(Vaga, id=vaga_id)
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
                inscricao = Inscricao.objects.create(vaga=vaga, candidato=candidato)
                
                # --- LÓGICA DE ENVIO DE E-MAIL DUPLO ---
                try:
                    # 1. E-mail de confirmação para o candidato
                    assunto_candidato = f"Confirmação de Candidatura: {vaga.titulo}"
                    mensagem_candidato = (
                        f"Olá, {candidato.nome}!\n\n"
                        f"Recebemos a sua candidatura para a vaga de '{vaga.titulo}' na empresa {vaga.empresa.nome}.\n\n"
                        "O seu perfil será analisado e entraremos em contacto caso seja selecionado para as próximas etapas.\n\n"
                        "Agradecemos o seu interesse!\n"
                        "Atenciosamente,\nEquipe de Recrutamento"
                    )
                    send_mail(
                        assunto_candidato,
                        mensagem_candidato,
                        settings.DEFAULT_FROM_EMAIL,
                        [candidato.email] # E-mail do candidato
                    )

                    # 2. E-mail de notificação para o recrutador
                    link_inscricao = request.build_absolute_uri(
                        reverse('admin:vagas_inscricao_change', args=[inscricao.id])
                    )
                    assunto_recrutador = f"Nova candidatura para '{vaga.titulo}': {candidato.nome}"
                    mensagem_recrutador = (
                        f"Uma nova candidatura foi recebida de '{candidato.nome}' para a vaga '{vaga.titulo}'.\n\n"
                        f"Para ver os detalhes da inscrição, aceda ao link:\n{link_inscricao}"
                    )
                    # IMPORTANTE: Substitua pelo e-mail real do recrutador
                    email_do_recrutador = ['sutterdorns@gmail.com']
                    send_mail(
                        assunto_recrutador,
                        mensagem_recrutador,
                        settings.DEFAULT_FROM_EMAIL,
                        email_do_recrutador
                    )
                except Exception as e:
                    print(f"Ocorreu um erro ao tentar enviar os e-mails: {e}")
                # --- FIM DA LÓGICA ---
            
            return redirect('realizar_teste', candidato_id=candidato.id)
    else:
        form = CandidaturaForm()
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
    # CORREÇÃO: Removido o 'vagas/' do caminho
    return render(request, 'teste_personalidade.html', contexto)

def calcular_e_salvar_perfil(candidato):
    contagem_perfis = RespostaCandidato.objects.filter(candidato=candidato).values('perfil_escolhido').annotate(total=Count('perfil_escolhido'))
    perfil = {'I': 0, 'C': 0, 'A': 0, 'O': 0}
    for item in contagem_perfis:
        if item['perfil_escolhido'] in perfil:
            perfil[item['perfil_escolhido']] = item['total']
    candidato.total_i = perfil['I']
    candidato.total_c = perfil['C']
    candidato.total_a = perfil['A']
    candidato.total_o = perfil['O']
    total_respostas = sum(perfil.values())
    def calcular_percentual(valor, total):
        if total == 0: return 0
        return round((valor / total) * 100)
    mapa_perfis = {
        'I': f"Águia ({calcular_percentual(perfil['I'], total_respostas)}%)",
        'C': f"Gato ({calcular_percentual(perfil['C'], total_respostas)}%)",
        'A': f"Tubarão ({calcular_percentual(perfil['A'], total_respostas)}%)",
        'O': f"Lobo ({calcular_percentual(perfil['O'], total_respostas)}%)",
    }
    if perfil and any(perfil.values()):
        perfil_max = max(perfil, key=perfil.get)
        candidato.perfil_comportamental = mapa_perfis[perfil_max]
    else:
        candidato.perfil_comportamental = "Indefinido"
    candidato.save()

def confirmacao(request, vaga_id):
    vaga = get_object_or_404(Vaga, id=vaga_id)
    return render(request, 'vagas/confirmacao.html', {'vaga': vaga})
