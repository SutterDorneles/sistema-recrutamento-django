# Em vagas/admin.py

from django.contrib import admin, messages
from django.db import models
# Importamos os novos modelos
from .models import (
    Vaga, Candidato, Inscricao, Pergunta, RespostaCandidato, Empresa, Funcionario,
    FuncionarioAtivo, FuncionarioDemitido, FuncionarioComObservacao
)
import csv
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from datetime import timedelta
from django.urls import path, reverse
from django.shortcuts import render, get_object_or_404
from django import forms
from django.utils.html import format_html

class MyDashboardAdminSite(admin.AdminSite):
    # ... (código do dashboard continua o mesmo)
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.dashboard_view), name='index'),
            path('pipeline/', self.admin_view(self.pipeline_view), name='pipeline'),
            path('pipeline/change_status/<int:inscricao_id>/<str:new_status>/', self.admin_view(self.change_status_view), name='pipeline_change_status'),
            path('pipeline/contratar/<int:inscricao_id>/', self.admin_view(self.pipeline_contratar_view), name='pipeline_contratar'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        context = self.each_context(request)
        total_vagas = Vaga.objects.count()
        total_candidatos = Candidato.objects.count()
        sete_dias_atras = timezone.now() - timedelta(days=7)
        novas_inscricoes = Inscricao.objects.filter(data_inscricao__gte=sete_dias_atras).count()
        candidatos_em_analise = Inscricao.objects.filter(status='em_analise').count()
        candidatos_entrevista = Inscricao.objects.filter(status='entrevista').count()
        candidatos_aprovados = Inscricao.objects.filter(status='aprovado').count()
        candidatos_rejeitados = Inscricao.objects.filter(status='rejeitado').count()
        total_aguia = Candidato.objects.filter(perfil_comportamental__icontains='Águia').count()
        total_gato = Candidato.objects.filter(perfil_comportamental__icontains='Gato').count()
        total_tubarao = Candidato.objects.filter(perfil_comportamental__icontains='Tubarão').count()
        total_lobo = Candidato.objects.filter(perfil_comportamental__icontains='Lobo').count()
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

    def pipeline_view(self, request):
        context = self.each_context(request)
        context['vagas'] = Vaga.objects.all()
        selected_vaga_id = request.GET.get('vaga_id')
        if selected_vaga_id:
            selected_vaga = get_object_or_404(Vaga, id=selected_vaga_id)
            inscricoes = Inscricao.objects.filter(vaga=selected_vaga).order_by('data_inscricao')
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

    def pipeline_contratar_view(self, request, inscricao_id):
        inscricao = get_object_or_404(Inscricao, id=inscricao_id)
        if inscricao.status == 'aprovado':
            if not inscricao.candidato.contratado:
                Funcionario.objects.create(
                    perfil_candidato=inscricao.candidato,
                    empresa=inscricao.vaga.empresa,
                    cargo=inscricao.vaga.tipo_cargo or 'Não especificado',
                    status='ativo',
                    remuneracao=0, # Valor padrão, pode ser editado depois
                    data_admissao=timezone.now().date()
                )
                inscricao.candidato.contratado = True
                inscricao.candidato.save()
                messages.success(request, f"{inscricao.candidato.nome} foi contratado com sucesso!")
            else:
                messages.warning(request, f"{inscricao.candidato.nome} já consta como contratado.")
        else:
            messages.error(request, "O candidato precisa de estar com o status 'Aprovado' para ser contratado.")
        
        redirect_url = reverse('admin:pipeline') + f'?vaga_id={inscricao.vaga.id}'
        return HttpResponseRedirect(redirect_url)

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
    
    # --- ALTERAÇÃO AQUI ---
    # Oculta as inscrições de candidatos já contratados
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(candidato__contratado=False)
    # ----------------------    

class VagaAdminForm(forms.ModelForm):
    replicar_para_empresas = forms.ModelMultipleChoiceField(
        queryset=Empresa.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple('Outras empresas', is_stacked=False),
        required=False,
        label='Replicar esta vaga para outras empresas',
        help_text='Selecione empresas adicionais onde esta vaga também deve ser criada. A empresa principal deve ser selecionada no campo "Empresa" acima.'
    )
    class Meta:
        model = Vaga
        fields = '__all__'

class VagaAdmin(admin.ModelAdmin):
    form = VagaAdminForm
    list_display = ('titulo', 'empresa', 'tipo_cargo', 'turno', 'data_criacao')
    search_fields = ('titulo', 'descricao', 'empresa__nome')
    list_filter = ('empresa', 'tipo_cargo', 'turno', 'data_criacao',)
    inlines = [InscricaoInline]
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        empresas_adicionais = form.cleaned_data.get('replicar_para_empresas')
        if empresas_adicionais:
            for empresa in empresas_adicionais:
                if empresa != obj.empresa:
                    obj.pk = None
                    obj.empresa = empresa
                    obj.save()

class CandidatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'contato', 'whatsapp_link', 'perfil_comportamental', 'ultima_empresa_inscrita', 'ultima_vaga_inscrita', 'contratado')
    search_fields = ('nome', 'email', 'cidade')
    list_filter = ('contratado', 'perfil_comportamental', 'cidade', 'preferencia_turno')
    fieldsets = (
        ('Informações Principais', {'fields': ('nome', 'email', 'cpf', 'contato', 'idade', 'sexo', 'estado_civil', 'contratado')}),
        ('Endereço e Moradia', {'fields': ('cep', 'endereco', 'bairro', 'cidade', 'tempo_residencia', 'moradia', 'meio_locomocao')}),
        ('Informações Familiares', {'classes': ('collapse',), 'fields': ('tem_filhos', 'qtd_filhos', 'idade_filhos', 'mora_com_filhos')}),
        ('Perfil Profissional e Pessoal', {'fields': ('preferencia_cargo', 'preferencia_turno', 'melhor_trabalho', 'pontos_fortes', 'objetivo_curto_prazo', 'objetivo_longo_prazo', 'lazer', 'habitos', 'curriculo')}),
        ('Resultado do Teste de Perfil', {'fields': ()}),
    )
    readonly_fields = ('perfil_comportamental', 'total_i', 'total_c', 'total_a', 'total_o', 'contratado')
    change_form_template = 'admin/vagas/candidato/change_form.html'
 
    def ultima_empresa_inscrita(self, obj):
        ultima_inscricao = obj.inscricao_set.order_by('-data_inscricao').first()
        if ultima_inscricao:
            return ultima_inscricao.vaga.empresa.nome
        return "Nenhuma inscrição"
    ultima_empresa_inscrita.short_description = "Última Empresa"

    def ultima_vaga_inscrita(self, obj):
        ultima_inscricao = obj.inscricao_set.order_by('-data_inscricao').first()
        if ultima_inscricao:
            return ultima_inscricao.vaga.titulo
        return "Nenhuma inscrição"
    ultima_vaga_inscrita.short_description = "Última Vaga"   
    
    
    def whatsapp_link(self, obj):
        url = obj.get_whatsapp_url()
        if not url:
            return "—"
        return format_html('<a href="{}" target="_blank"><i class="fab fa-whatsapp"></i> Enviar Mensagem</a>', url)
    whatsapp_link.short_description = "WhatsApp"
    
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

class InscricaoAdmin(admin.ModelAdmin):
    list_display = ('get_nome_candidato', 'get_empresa_nome', 'get_vaga_titulo', 'whatsapp_do_candidato', 'status', 'data_inscricao')
    list_filter = ('vaga__empresa__nome', 'status', 'data_inscricao')
    search_fields = ('candidato__nome', 'candidato__email', 'vaga__titulo')
    list_editable = ('status',)
    actions = [
        'marcar_como_em_analise', 'marcar_como_entrevista', 
        'marcar_como_aprovado', 'marcar_como_rejeitado', 
        'contratar_candidato', 'exportar_para_csv'
    ]
    
    # --- ALTERAÇÃO AQUI ---
    # Oculta as inscrições de candidatos já contratados
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(candidato__contratado=False)
    # ----------------------    
    
    def whatsapp_do_candidato(self, obj):
        url = obj.candidato.get_whatsapp_url()
        if not url:
            return "—"
        return format_html('<a href="{}" target="_blank"><i class="fab fa-whatsapp"></i> Contatar</a>', url)
    whatsapp_do_candidato.short_description = "WhatsApp"    
    
    # --- NOVA AÇÃO PARA CONTRATAR ---
    def contratar_candidato(self, request, queryset):
        contratados = 0
        ja_contratados = 0
        nao_aprovados = 0

        for inscricao in queryset:
            if inscricao.status == 'aprovado':
                if not inscricao.candidato.contratado:
                    # Cria o funcionário
                    Funcionario.objects.create(
                        perfil_candidato=inscricao.candidato,
                        empresa=inscricao.vaga.empresa,
                        cargo=inscricao.vaga.tipo_cargo or 'Não especificado',
                        status='ativo',
                        remuneracao=0, # Valor padrão, pode ser editado depois
                        data_admissao=timezone.now().date()
                    )
                    # Marca o candidato como contratado
                    inscricao.candidato.contratado = True
                    inscricao.candidato.save()
                    contratados += 1
                else:
                    ja_contratados += 1
            else:
                nao_aprovados += 1
        
        if contratados > 0:
            self.message_user(request, f"{contratados} candidato(s) foram contratados e movidos para a lista de funcionários.", messages.SUCCESS)
        if ja_contratados > 0:
            self.message_user(request, f"{ja_contratados} candidato(s) já constavam como contratados.", messages.WARNING)
        if nao_aprovados > 0:
            self.message_user(request, f"{nao_aprovados} candidato(s) não puderam ser contratados pois o seu status não é 'Aprovado'.", messages.ERROR)
            
    contratar_candidato.short_description = "Contratar candidato(s) selecionado(s)"
    # --- FIM DA NOVA AÇÃO ---    
    
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
    email = forms.EmailField(label="Email", required=True)
    cpf = forms.CharField(label="CPF", max_length=14, required=False)

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

# --- GESTÃO DE FUNCIONÁRIOS ATUALIZADA ---
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('perfil_candidato', 'empresa', 'cargo', 'status', 'data_admissao', 'tempo_de_servico')
    list_filter = ('status', 'empresa', 'cargo')
    search_fields = ('perfil_candidato__nome', 'perfil_candidato__email', 'cargo')
    list_editable = ('status',)
    
    # Usa o formulário personalizado apenas ao adicionar um novo funcionário
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return FuncionarioAdminForm
        return super().get_form(request, obj, **kwargs)

    # Define fieldsets diferentes para adicionar e editar
    def get_fieldsets(self, request, obj=None):
        if obj is None: # Formulário de Adicionar
            return (
                ('Dados do Novo Funcionário', {'fields': ('nome', 'email', 'cpf')}),
                ('Detalhes do Contrato', {'fields': ('empresa', 'cargo', 'remuneracao', 'data_admissao', 'status', 'observacoes')}),
            )
        else: # Formulário de Editar
            return (
                ('Informações do Funcionário', {'fields': ('perfil_candidato', 'empresa', 'cargo', 'remuneracao', 'status', 'observacoes')}),
                ('Datas Importantes', {'fields': ('data_admissao', 'data_demissao', 'tempo_de_servico')}),
            )

    # Define campos de apenas leitura apenas ao editar
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('perfil_candidato', 'empresa', 'data_admissao', 'tempo_de_servico')
        return ()

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
            if not obj.status:
                obj.status = 'ativo'

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
