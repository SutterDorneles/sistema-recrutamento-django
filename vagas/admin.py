# Em vagas/admin.py

from django.contrib import admin, messages
from django.db import models
# Importamos os novos modelos
from .models import (
    Vaga, Candidato, Inscricao, Pergunta, RespostaCandidato, Empresa, Funcionario,
    FuncionarioAtivo, FuncionarioDemitido, FuncionarioComObservacao, Cargo, HistoricoFuncionario, PerfilGerente
)
from .forms import ContratacaoForm, AgendamentoEntrevistaForm # Importamos o novo formulário
import csv
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.urls import path, reverse
from django.shortcuts import render, get_object_or_404
from django import forms
from django.utils.html import format_html
from django.db.models import Q
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin
from django.core.exceptions import PermissionDenied

class MyDashboardAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.dashboard_view), name='index'),
            path('pipeline/', self.admin_view(self.pipeline_view), name='pipeline'),
            path('pipeline/change_status/<int:inscricao_id>/<str:new_status>/', self.admin_view(self.change_status_view), name='pipeline_change_status'),
            # ROTA PARA A NOVA PÁGINA DE CONTRATAÇÃO
            path('inscricao/<int:inscricao_id>/contratar/', self.admin_view(self.contratar_view), name='contratar_candidato'),
            # ROTA CORRIGIDA E ADICIONADA DE AGENDAR ENTREVISTA
            path('pipeline/agendar_entrevista/<int:inscricao_id>/', self.admin_view(self.agendar_entrevista_view), name='pipeline_agendar_entrevista'),
            # NOVA ROTA PARA O AUTO-SAVE
            path('inscricao/ajax_change_status/', self.admin_view(self.ajax_change_status_view), name='ajax_change_inscricao_status'),            
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        context = self.each_context(request)
        total_vagas = Vaga.objects.count()
        total_candidatos = Candidato.objects.filter(Q(inscricao__isnull=False) & ~Q(inscricao__status='incompleto') | Q(contratado=True)).distinct().count()
        sete_dias_atras = timezone.now() - timedelta(days=7)
        novas_inscricoes = Inscricao.objects.filter(data_inscricao__gte=sete_dias_atras).exclude(status='incompleto').count()
        candidatos_em_analise = Inscricao.objects.filter(status='em_analise').count()
        candidatos_entrevista = Inscricao.objects.filter(status='entrevista').count()
        candidatos_aprovados = Inscricao.objects.filter(status='aprovado').count()
        candidatos_rejeitados = Inscricao.objects.filter(status='rejeitado').count()
        total_aguia = Candidato.objects.filter(perfil_comportamental__icontains='Águia').count()
        total_gato = Candidato.objects.filter(perfil_comportamental__icontains='Gato').count()
        total_tubarao = Candidato.objects.filter(perfil_comportamental__icontains='Tubarão').count()
        total_lobo = Candidato.objects.filter(perfil_comportamental__icontains='Lobo').count()
        
        #recent_actions = LogEntry.objects.select_related('content_type', 'user').all()[:10]     
        
        base_inscricao_url = reverse('admin:vagas_inscricao_changelist')
        context.update({
            'total_vagas': total_vagas,
            'novas_inscricoes': novas_inscricoes,
            'candidatos_em_analise': candidatos_em_analise,
            'candidatos_entrevista': candidatos_entrevista,
            'candidatos_aprovados': candidatos_aprovados,
            'candidatos_rejeitados': candidatos_rejeitados,
            'url_vagas': reverse('admin:vagas_vaga_changelist'),
            'url_em_analise': f"{base_inscricao_url}?status__exact=em_analise",
            'url_entrevista': f"{base_inscricao_url}?status__exact=entrevista",
            'url_aprovados': f"{base_inscricao_url}?status__exact=aprovado",
            'url_rejeitados': f"{base_inscricao_url}?status__exact=rejeitado",
            'total_aguia': total_aguia,
            'total_gato': total_gato,
            'total_tubarao': total_tubarao,
            'total_lobo': total_lobo,
        })
        return render(request, 'admin/index.html', context)
    
    # --- NOVA VIEW PARA O AUTO-SAVE (AJAX) ---
    def ajax_change_status_view(self, request):
        # 🔒 garante que só quem tem permissão pode salvar
        if not request.user.has_perm("vagas.change_inscricao"):
            raise PermissionDenied("Você não tem permissão para alterar inscrições.")      
         
        if request.method == 'POST':
            inscricao_id = request.POST.get('inscricao_id')
            new_status = request.POST.get('new_status')
            try:
                inscricao = Inscricao.objects.get(id=inscricao_id)
                inscricao.status = new_status
                inscricao.save()
                return JsonResponse({'success': True, 'message': 'Status atualizado com sucesso!'})
            except Inscricao.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Inscrição não encontrada.'}, status=404)
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)}, status=500)
        return JsonResponse({'success': False, 'message': 'Apenas pedidos POST são permitidos.'}, status=400)
    # --- FIM DA NOVA VIEW ---    
    
    
    # --- NOVA VIEW PARA A PÁGINA DE AGENDAMENTO ---
    def agendar_entrevista_view(self, request, inscricao_id):
        inscricao = get_object_or_404(Inscricao, id=inscricao_id)
        if request.method == 'POST':
            form = AgendamentoEntrevistaForm(request.POST)
            if form.is_valid():
                inscricao.data_entrevista = form.cleaned_data['data_entrevista']
                inscricao.status = 'entrevista'
                inscricao.save()
                messages.success(request, f"Entrevista com {inscricao.candidato.nome} agendada com sucesso!")
                redirect_url = reverse('admin:pipeline') + f'?vaga_id={inscricao.vaga.id}'
                return HttpResponseRedirect(redirect_url)
        else:
            form = AgendamentoEntrevistaForm()
        context = self.each_context(request)
        context['form'] = form
        context['inscricao'] = inscricao
        context['title'] = f"Agendar Entrevista: {inscricao.candidato.nome}"
        return render(request, 'admin/agendar_entrevista_form.html', context)


    def pipeline_view(self, request):
        context = self.each_context(request)
        context['vagas'] = Vaga.objects.all()
        selected_vaga_id = request.GET.get('vaga_id')
        if selected_vaga_id:
            selected_vaga = get_object_or_404(Vaga, id=selected_vaga_id)
            inscricoes = Inscricao.objects.filter(vaga=selected_vaga).exclude(status='incompleto').order_by('data_inscricao')
            pipeline_status = {'recebida': [], 'em_analise': [], 'entrevista': [], 'aprovado': [], 'rejeitado': []}
            for inscricao in inscricoes:
                if inscricao.status in pipeline_status:
                    pipeline_status[inscricao.status].append(inscricao)
            context['pipeline_status'] = pipeline_status
            context['selected_vaga'] = selected_vaga
        return render(request, 'admin/pipeline.html', context)
    
    def change_status_view(self, request, inscricao_id, new_status):
        inscricao = get_object_or_404(Inscricao, id=inscricao_id)
        valid_statuses = [choice[0] for choice in Inscricao.STATUS_CHOICES]
        if new_status in valid_statuses:
            inscricao.status = new_status
            inscricao.save()
            messages.success(request, f"O status de {inscricao.candidato.nome} foi alterado para '{inscricao.get_status_display()}'.")
        else:
            messages.error(request, "Status inválido.")
        redirect_url = reverse('admin:pipeline') + f'?vaga_id={inscricao.vaga.id}'
        return HttpResponseRedirect(redirect_url)

    # VIEW CENTRALIZADA PARA A PÁGINA DE CONTRATAÇÃO
    def contratar_view(self, request, inscricao_id):
        inscricao = get_object_or_404(Inscricao, id=inscricao_id)
        
        if request.method == 'POST':
            form = ContratacaoForm(request.POST)
            if form.is_valid():
                if not inscricao.candidato.contratado:
                    Funcionario.objects.create(
                        perfil_candidato=inscricao.candidato,
                        empresa=form.cleaned_data['empresa'],
                        cargo=form.cleaned_data['cargo'],
                        status='ativo',
                        remuneracao=form.cleaned_data['remuneracao'],
                        data_admissao=form.cleaned_data['data_admissao']
                    )
                    inscricao.candidato.contratado = True
                    inscricao.candidato.save()
                    messages.success(request, f"{inscricao.candidato.nome} foi contratado com sucesso!")
                    return HttpResponseRedirect(reverse('admin:vagas_funcionarioativo_changelist'))
                else:
                    messages.warning(request, f"{inscricao.candidato.nome} já consta como contratado.")
                    return HttpResponseRedirect(reverse('admin:vagas_inscricao_changelist'))
        else:
            # --- ALTERAÇÃO AQUI ---
            # Preenche o formulário com os dados da vaga original
            initial_data = {
                'empresa': inscricao.vaga.empresa,
                'cargo': inscricao.vaga.tipo_cargo, 
                'data_admissao': timezone.now().date()
            }
            # ----------------------
            form = ContratacaoForm(initial=initial_data)

        context = self.each_context(request)
        context['form'] = form
        context['inscricao'] = inscricao
        context['title'] = f"Contratar: {inscricao.candidato.nome}"
        return render(request, 'admin/contratar_form.html', context)

admin_site = MyDashboardAdminSite(name='myadmin')

class InscricaoInline(admin.TabularInline):
    model = Inscricao
    extra = 0
    fields = ('candidato', 'status', 'notas_internas', 'data_inscricao')
    readonly_fields = ('candidato', 'data_inscricao')
    can_delete = False
    formfield_overrides = {
        models.TextField: {'widget': admin.widgets.AdminTextareaWidget(attrs={'rows': 3, 'cols': 40})},
    }
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(candidato__contratado=False)

class VagaAdmin(admin.ModelAdmin):
    # ... (código do VagaAdmin continua o mesmo)
    list_display = ('titulo', 'empresa', 'tipo_cargo', 'turno', 'data_criacao')
    search_fields = ('titulo', 'descricao', 'empresa__nome')
    list_filter = ('empresa', 'tipo_cargo', 'turno', 'data_criacao',)
    inlines = [InscricaoInline]

class CandidatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'perfil_comportamental', 'ultima_empresa_inscrita', 'ultima_vaga_inscrita', 'whatsapp_link', 'contratado')
    search_fields = ('nome', 'email', 'cidade')
    list_filter = ('inscricao__vaga','contratado', 'perfil_comportamental', 'cidade', 'preferencia_turno')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # --- NOVA LÓGICA DE ACESSO TOTAL ---
        grupos_com_acesso_total = ['RH', 'Recrutamento_RH']

        if request.user.is_superuser or request.user.groups.filter(name__in=grupos_com_acesso_total).exists():
            # A sua lógica original para superusuários agora se aplica a todos com acesso total
            complete_candidates_ids = set(
                Inscricao.objects.exclude(status='incompleto')
                .values_list('candidato_id', flat=True)
            )
            qs = qs.filter(
                Q(id__in=complete_candidates_ids) | Q(contratado=True)
            )
            if 'contratado__exact' in request.GET:
                return qs
            return qs.filter(contratado=False)

        # --- Lógica para Gerentes (continua a mesma) ---
        if request.user.groups.filter(name='Gerentes').exists():
            try:
                empresa_gerente = request.user.perfil_gerente.empresa
                return qs.filter(
                    inscricao__status='aprovado',
                    inscricao__vaga__empresa=empresa_gerente,
                    contratado=False
                ).distinct()
            except PerfilGerente.DoesNotExist:
                return qs.none()
        
        return qs.none()
    # ----------------------
    # --- CORREÇÃO: Reintroduzida a organização em abas (fieldsets) ---
    fieldsets = (
        ('Informações Principais', {'fields': ('nome', 'email', 'cpf', 'contato', 'idade', 'sexo', 'estado_civil', 'contratado')}),
        ('Endereço e Moradia', {'fields': ('cep', 'endereco', 'bairro', 'cidade', 'tempo_residencia', 'moradia', 'meio_locomocao')}),
        ('Perfil Profissional e Pessoal', {'classes': ('collapse',), 'fields': ('preferencia_cargo', 'preferencia_turno', 'melhor_trabalho', 'pontos_fortes', 'objetivo_curto_prazo', 'objetivo_longo_prazo', 'lazer', 'habitos', 'curriculo')}),
        # Esta secção é agora preenchida pelo nosso template
        ('Resultado do Teste de Perfil', {'fields': ()}),
    )    
        
    readonly_fields = ('perfil_comportamental', 'total_i', 'total_c', 'total_a', 'total_o', 'contratado')
    
    # Esta linha é a chave para trazer o gráfico de volta
    change_form_template = 'admin/vagas/candidato/change_form.html'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        candidato = self.get_object(request, object_id)
        if candidato:
            total_respostas = candidato.total_i + candidato.total_c + candidato.total_a + candidato.total_o
            def calcular_percentual(valor, total):
                if total == 0: return 0
                return round((valor / total) * 100)
            extra_context['chart_data'] = {
                'aguia': calcular_percentual(candidato.total_i, total_respostas),
                'gato': calcular_percentual(candidato.total_c, total_respostas),
                'tubarao': calcular_percentual(candidato.total_a, total_respostas),
                'lobo': calcular_percentual(candidato.total_o, total_respostas),
                'perfil_principal': candidato.perfil_comportamental,
            }
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    
    def ultima_empresa_inscrita(self, obj):
        ultima_inscricao = obj.inscricao_set.order_by('-data_inscricao').first()
        if ultima_inscricao: return ultima_inscricao.vaga.empresa.nome
        return "Nenhuma inscrição"
    ultima_empresa_inscrita.short_description = "Última Empresa"

    def ultima_vaga_inscrita(self, obj):
        ultima_inscricao = obj.inscricao_set.order_by('-data_inscricao').first()
        if ultima_inscricao: return ultima_inscricao.vaga.titulo
        return "Nenhuma inscrição"
    ultima_vaga_inscrita.short_description = "Última Vaga"

    def whatsapp_link(self, obj):
        url = obj.get_whatsapp_url()
        if not url: return "—"
        return format_html('<a href="{}" target="_blank"><i class="fab fa-whatsapp"></i> Enviar Mensagem</a>', url)
    whatsapp_link.short_description = "WhatsApp"
    
# --- NOVA SECÇÃO PARA GERIR OS CARGOS ---
class CargoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)
# ----------------------------------------    

class InscricaoAdmin(admin.ModelAdmin):
    list_display = ('get_nome_candidato', 'get_empresa_nome', 'get_vaga_titulo', 'whatsapp_do_candidato', 'status', 'acoes_contratacao', 'data_inscricao')
    list_filter = ('vaga__tipo_cargo','vaga__empresa__nome', 'status', 'data_inscricao')
    search_fields = ('candidato__nome', 'candidato__email', 'vaga__titulo')
    list_editable = ('status',)

    # Diz ao admin para usar o nosso novo "molde" para esta página
    change_list_template = "admin/vagas/inscricao/change_list.html"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # --- NOVA LÓGICA DE ACESSO TOTAL ---
        grupos_com_acesso_total = ['RH', 'Recrutamento_RH']

        if request.user.is_superuser or request.user.groups.filter(name__in=grupos_com_acesso_total).exists():
            # Superusuários e RH veem todas as inscrições relevantes
            return qs.exclude(status='incompleto').filter(candidato__contratado=False)

        # --- Lógica para Gerentes (continua a mesma) ---
        if request.user.groups.filter(name='Gerentes').exists():
            try:
                empresa_gerente = request.user.perfil_gerente.empresa
                return qs.filter(
                    vaga__empresa=empresa_gerente,
                    status='aprovado'
                )
            except PerfilGerente.DoesNotExist:
                return qs.none()
        
        return qs.none()
    
    # CORREÇÃO: As duas regras de filtro foram combinadas numa única função
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Exclui tanto as inscrições incompletas como as de candidatos já contratados
        return qs.exclude(status='incompleto').filter(candidato__contratado=False)

    def whatsapp_do_candidato(self, obj):
        url = obj.candidato.get_whatsapp_url()
        if not url: return "—"
        return format_html('<a href="{}" target="_blank"><i class="fab fa-whatsapp"></i> Contatar</a>', url)
    whatsapp_do_candidato.short_description = "WhatsApp"

    def acoes_contratacao(self, obj):
        if obj.status == 'aprovado' and not obj.candidato.contratado:
            url = reverse('admin:contratar_candidato', args=[obj.id])
            return format_html('<a href="{}" class="button">Contratar</a>', url)
        return "—"
    acoes_contratacao.short_description = 'Ações'
    
    def marcar_como_em_analise(self, request, queryset):
        queryset.update(status='em_analise')
        self.message_user(request, f"{queryset.count()} inscrições foram marcadas como 'Em Análise'.")
    marcar_como_em_analise.short_description = "Marcar selecionadas como 'Em Análise'"
    def marcar_como_entrevista(self, request, queryset):
        queryset.update(status='entrevista')
        self.message_user(request, f"{queryset.count()} inscrições foram marcadas para 'Entrevista'.")
    marcar_como_entrevista.short_description = "Marcar selecionadas para 'Entrevista'"
    def marcar_como_aprovado(self, request, queryset):
        queryset.update(status='aprovado')
        self.message_user(request, f"{queryset.count()} inscrições foram marcadas como 'Aprovado'.")
    marcar_como_aprovado.short_description = "Marcar selecionadas como 'Aprovado'"
    def marcar_como_rejeitado(self, request, queryset):
        queryset.update(status='rejeitado')
        self.message_user(request, f"{queryset.count()} inscrições foram marcadas como 'Rejeitado'.")
    marcar_como_rejeitado.short_description = "Marcar selecionadas como 'Rejeitado'"
    def exportar_para_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="candidatos.csv"'
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Nome do Candidato', 'Email', 'Telefone', 'Vaga', 'Status da Inscrição', 'Notas Internas'])
        for inscricao in queryset:
            writer.writerow([
                inscricao.candidato.nome, inscricao.candidato.email, inscricao.candidato.contato,
                inscricao.vaga.titulo, inscricao.get_status_display(), inscricao.notas_internas
            ])
        return response
    exportar_para_csv.short_description = "Exportar selecionadas para CSV"
    def get_nome_candidato(self, obj): return obj.candidato.nome
    get_nome_candidato.short_description = 'Nome do Candidato'
    def get_vaga_titulo(self, obj): return obj.vaga.titulo
    get_vaga_titulo.short_description = 'Vaga'
    def get_empresa_nome(self, obj): return obj.vaga.empresa.nome
    get_empresa_nome.short_description = 'Empresa'

class PerguntaAdmin(admin.ModelAdmin):
    list_display = ('texto', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('texto',)

class RespostaCandidatoAdmin(admin.ModelAdmin):
    list_display = ('candidato', 'get_texto_pergunta', 'perfil_escolhido')
    list_filter = ('perfil_escolhido', 'candidato')
    autocomplete_fields = ['candidato', 'pergunta']
    search_fields = ('candidato__nome', 'pergunta__texto')
    def get_texto_pergunta(self, obj): return obj.pergunta.texto
    get_texto_pergunta.short_description = 'Texto da Pergunta'

class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem')
    list_editable = ('ordem',)
    search_fields = ('nome',)

# --- FORMULÁRIO PERSONALIZADO PARA ADICIONAR FUNCIONÁRIOS MANUALMENTE ---
class FuncionarioAdminForm(forms.ModelForm):
    nome = forms.CharField(label="Nome Completo", max_length=100, required=True)
    email = forms.EmailField(label="Email", required=False)
    cpf = forms.CharField(label="CPF", max_length=14, required=True)

    class Meta:
        model = Funcionario
        fields = ['nome', 'email', 'cpf', 'empresa', 'cargo', 'remuneracao', 'data_admissao', 'status', 'observacoes']
        # --- ALTERAÇÃO AQUI ---
        # Força o uso do widget de calendário para a data de admissão
        widgets = {
            'data_admissao': admin.widgets.AdminDateWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se estamos a editar um funcionário existente, não mostramos os campos do candidato
        if self.instance.pk:
            del self.fields['nome']
            del self.fields['email']
            del self.fields['cpf']
            
# ------------------------
# Filtros personalizados
# ------------------------
class ExperienciaVencidaFilter(admin.SimpleListFilter):
    title = "Período de Experiência"
    parameter_name = "experiencia"

    def lookups(self, request, model_admin):
        return [
            ("vencida", "Experiência vencida"),
            ("em_andamento", "Experiência em andamento"),
        ]

    def queryset(self, request, queryset):
        hoje = timezone.now().date()
        
        if self.value() == "vencida":
            # MUDANÇA AQUI 👇: usa o novo campo
            return queryset.filter(data_fim_experiencia__lt=hoje)
            
        if self.value() == "em_andamento":
            # MUDANÇA AQUI 👇: usa o novo campo
            return queryset.filter(data_fim_experiencia__gte=hoje)
            
        return queryset


class FeriasFilter(admin.SimpleListFilter):
    title = "Direito a Férias"
    parameter_name = "ferias"

    def lookups(self, request, model_admin):
        return [
            ("tem_direito", "Já tem direito a férias"),
            ("nao_tem", "Ainda não tem direito"),
        ]

    def queryset(self, request, queryset):
        hoje = timezone.now().date()
        if self.value() == "tem_direito":
            return queryset.filter(data_direito_ferias__lte=hoje)
        if self.value() == "nao_tem":
            return queryset.filter(data_direito_ferias__gt=hoje)
        return queryset   
    
class HistoricoFuncionarioAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'data_ocorrencia', 'tipo', 'criado_por', 'descricao')
    list_filter = ('tipo', 'funcionario')

    def save_model(self, request, obj, form, change):
        # Lógica para preencher 'criado_por' ao salvar
        if not obj.pk: # Se for um novo objeto
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)

# --- GESTÃO DE FUNCIONÁRIOS ATUALIZADA ---
class FuncionarioAdmin(admin.ModelAdmin):
    change_list_template = "admin/vagas/funcionario/change_list.html"  # 👈 novo
        
    list_display = ('perfil_candidato', 'empresa', 'cargo', 'status', 'data_admissao', 'tempo_de_servico', 'data_fim_experiencia','data_direito_ferias', 'cor_da_linha')
    list_filter = ('status', 'empresa', 'cargo', ExperienciaVencidaFilter, FeriasFilter)
    search_fields = ('perfil_candidato__nome', 'perfil_candidato__email', 'cargo')
    list_editable = ('status',)
    readonly_fields = [
        'tempo_de_servico','data_fim_experiencia','data_direito_ferias', 'mostrar_historico'
    ]    

    change_form_template = 'admin/vagas/funcionario/change_form.html'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # --- NOVA LÓGICA DE ACESSO TOTAL ---
        # Define quais grupos têm visão completa
        grupos_com_acesso_total = ['RH', 'Recrutamento_RH'] 

        # Se o usuário for superuser OU pertencer a um dos grupos de acesso total
        if request.user.is_superuser or request.user.groups.filter(name__in=grupos_com_acesso_total).exists():
            return qs # Vê tudo

        # --- Lógica para Gerentes (continua a mesma) ---
        if request.user.groups.filter(name='Gerentes').exists():
            try:
                return qs.filter(empresa=request.user.perfil_gerente.empresa)
            except PerfilGerente.DoesNotExist:
                return qs.none()
        
        # Outros usuários não veem nada
        return qs.none()
    
    @admin.display(description='Status Cor')
    def cor_da_linha(self, obj): # <-- O erro provavelmente estava aqui (faltava o 'obj')
        # Esta função PRECISA chamar o método do seu modelo E RETORNAR O VALOR
        return obj.get_row_class()
    
    def mostrar_historico(self, obj):
        if not obj.pk:
            return "Salve o funcionário primeiro para adicionar um histórico."

        # Botão para adicionar um novo registro de histórico
        add_url = reverse('myadmin:vagas_historicofuncionario_add') + f'?funcionario={obj.pk}'
        
        html = f'<a href="{add_url}" class="button">Adicionar Novo Histórico</a>'
        html += '<ul>'
        
        # Pega os 5 históricos mais recentes
        historicos = obj.historico.all().order_by('-data_ocorrencia')[:5]
        
        for hist in historicos:
            criado_por_nome = hist.criado_por.username if hist.criado_por else 'Sistema'
            html += (
                f"<li><strong>{hist.data_ocorrencia.strftime('%d/%m/%Y às %H:%M')} - "
                f"({criado_por_nome}) - {hist.get_tipo_display()}:</strong> "
                f"{hist.descricao}</li>"
            )
            
        html += '</ul>'
        
        if obj.historico.count() > 5:
            # Link para ver todos os históricos
            all_url = reverse('myadmin:vagas_historicofuncionario_changelist') + f'?funcionario__id__exact={obj.pk}'
            html += f'<a href="{all_url}">Ver todos os {obj.historico.count()} registros...</a>'
            
        return format_html(html)

    mostrar_historico.short_description = ""    

    # --- LÓGICA RESTAURADA ---
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return FuncionarioAdminForm
        return super().get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        if obj is None: # Formulário de Adicionar
            return (
                ('Dados do Novo Funcionário', {'fields': ('nome', 'email', 'cpf')}),
                ('Detalhes do Contrato', {'fields': ('empresa', 'cargo', 'remuneracao', 'data_admissao', 'status', 'observacoes')}),
            )
        else: # Formulário de Editar
            return (
                ('Detalhes do Contrato', {
                    'fields': ('empresa', 'cargo', 'remuneracao', 'status', 'observacoes', 'data_demissao')
                }),
                ('Datas Importantes', {
                    'fields': ('data_admissao', 'data_demissao', 'tipo_experiencia', 'tempo_de_servico', 'data_direito_ferias')
                }),
                ('Controle de Férias', {
                    'fields': ('data_direito_ferias', 'data_inicio_gozo_ferias', 'data_fim_gozo_ferias')
                }),                
                ('Dados Pessoais (do Perfil Original)', {
                    'classes': ('collapse',),
                    'fields': ('get_nome', 'get_email', 'get_cpf', 'get_contato', 'get_idade', 'get_sexo', 'get_estado_civil', 'get_endereco_completo')
                }),
                ('Resultado do Teste de Perfil', { 'fields': () }),
                # --- ADICIONE ESTA SEÇÃO INTEIRA AQUI NO FINAL ---
                ('Histórico do Funcionário', {
                    'fields': ('mostrar_historico',)
                }),         
            )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [
                'get_nome', 'get_email', 'get_cpf', 'get_contato', 'get_idade', 'get_sexo',
                'get_estado_civil', 'get_endereco_completo',
                'tempo_de_servico', 'mostrar_historico',
            ]
        return ()
    
    # --- FIM DA LÓGICA RESTAURADA ---
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        funcionario = self.get_object(request, object_id)
        if funcionario:
            candidato = funcionario.perfil_candidato
            total_respostas = candidato.total_i + candidato.total_c + candidato.total_a + candidato.total_o
            def calcular_percentual(valor, total):
                if total == 0: return 0
                return round((valor / total) * 100)
            extra_context['chart_data'] = {
                'aguia': calcular_percentual(candidato.total_i, total_respostas),
                'gato': calcular_percentual(candidato.total_c, total_respostas),
                'tubarao': calcular_percentual(candidato.total_a, total_respostas),
                'lobo': calcular_percentual(candidato.total_o, total_respostas),
                'perfil_principal': candidato.perfil_comportamental,
            }
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    # Funções para buscar os dados do candidato relacionado
    def get_nome(self, obj): return obj.perfil_candidato.nome
    get_nome.short_description = "Nome Completo"
    
    def get_email(self, obj): return obj.perfil_candidato.email
    get_email.short_description = "Email"

    def get_cpf(self, obj): return obj.perfil_candidato.cpf
    get_cpf.short_description = "CPF"

    def get_contato(self, obj): return obj.perfil_candidato.contato
    get_contato.short_description = "Contato"
    
    def get_idade(self, obj): return obj.perfil_candidato.idade
    get_idade.short_description = "Idade"

    def get_sexo(self, obj): return obj.perfil_candidato.sexo
    get_sexo.short_description = "Sexo"

    def get_estado_civil(self, obj): return obj.perfil_candidato.estado_civil
    get_estado_civil.short_description = "Estado Civil"

    def get_endereco_completo(self, obj):
        c = obj.perfil_candidato
        return f"{c.endereco}, {c.bairro} - {c.cidade}"
    get_endereco_completo.short_description = "Endereço"

    # Lógica personalizada para guardar
    def save_model(self, request, obj, form, change):
        if not change: # Se for um novo funcionário
            candidato, created = Candidato.objects.get_or_create(
                email=form.cleaned_data['email'],
                defaults={
                    'nome': form.cleaned_data['nome'],
                    'cpf': form.cleaned_data.get('cpf'),
                    'contratado': True
                }
            )
            if not created:
                candidato.nome = form.cleaned_data['nome']
                candidato.contratado = True
                candidato.save()
            
            obj.perfil_candidato = candidato
            if not obj.status: obj.status = 'ativo'

        if change and 'status' in form.changed_data and obj.status == 'demitido' and not obj.data_demissao:
            obj.data_demissao = timezone.now().date()
        
        super().save_model(request, obj, form, change)

class FuncionarioAtivoAdmin(FuncionarioAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status='ativo')    

class FuncionarioDemitidoAdmin(FuncionarioAdmin):
    list_display = ('perfil_candidato', 'empresa', 'cargo', 'status', 'data_demissao', 'tempo_de_servico')
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status='demitido')

class FuncionarioComObservacaoAdmin(FuncionarioAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status='observacao')
    
# --- CÓDIGO PARA ADICIONAR O PERFIL DE GERENTE AO ADMIN DE USUÁRIO ---

# 1. Crie o Inline para o perfil
class PerfilGerenteInline(admin.StackedInline):
    model = PerfilGerente
    can_delete = False
    verbose_name_plural = 'Perfil de Gerente (Vincular a uma Loja)'

# 2. Crie sua própria classe UserAdmin que usa o inline
class UserAdmin(BaseUserAdmin):
    inlines = (PerfilGerenteInline,)    
    
admin_site.register(Vaga, VagaAdmin)
admin_site.register(Candidato, CandidatoAdmin)
admin_site.register(Inscricao, InscricaoAdmin)
admin_site.register(Pergunta, PerguntaAdmin)
admin_site.register(RespostaCandidato, RespostaCandidatoAdmin)
admin_site.register(Empresa, EmpresaAdmin)
admin_site.register(Funcionario, FuncionarioAdmin)
admin_site.register(FuncionarioAtivo, FuncionarioAtivoAdmin)
admin_site.register(FuncionarioDemitido, FuncionarioDemitidoAdmin)
admin_site.register(FuncionarioComObservacao, FuncionarioComObservacaoAdmin)
admin_site.register(Cargo, CargoAdmin)
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(HistoricoFuncionario, HistoricoFuncionarioAdmin)