# Em vagas/admin.py

from django.contrib import admin
from django.db import models
# Importamos o novo modelo Empresa
from .models import Vaga, Candidato, Inscricao, Pergunta, RespostaCandidato, Empresa 
import csv
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from django.urls import path
from django.shortcuts import render

class MyDashboardAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.dashboard_view), name='index'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        context = self.each_context(request)
        total_vagas = Vaga.objects.count()
        total_candidatos = Candidato.objects.count()
        sete_dias_atras = timezone.now() - timedelta(days=7)
        novas_inscricoes = Inscricao.objects.filter(data_inscricao__gte=sete_dias_atras).count()
        candidatos_em_analise = Inscricao.objects.filter(status='em_analise').count()
        total_aguia = Candidato.objects.filter(perfil_comportamental__icontains='Águia').count()
        total_gato = Candidato.objects.filter(perfil_comportamental__icontains='Gato').count()
        total_tubarao = Candidato.objects.filter(perfil_comportamental__icontains='Tubarão').count()
        total_lobo = Candidato.objects.filter(perfil_comportamental__icontains='Lobo').count()
        context.update({
            'total_vagas': total_vagas,
            'total_candidatos': total_candidatos,
            'novas_inscricoes': novas_inscricoes,
            'candidatos_em_analise': candidatos_em_analise,
            'total_aguia': total_aguia,
            'total_gato': total_gato,
            'total_tubarao': total_tubarao,
            'total_lobo': total_lobo,
        })
        return render(request, 'admin/index.html', context)

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

class VagaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'empresa', 'tipo_cargo', 'turno', 'data_criacao')
    search_fields = ('titulo', 'descricao', 'empresa__nome')
    list_filter = ('empresa', 'tipo_cargo', 'turno', 'data_criacao',)
    inlines = [InscricaoInline]

class CandidatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'perfil_comportamental', 'cidade')
    search_fields = ('nome', 'email', 'cidade')
    list_filter = ('perfil_comportamental', 'cidade', 'preferencia_turno')
    fieldsets = (
        ('Informações Pessoais', {'fields': ('nome', 'email', 'contato', 'sexo', 'idade', 'cidade', 'endereco')}),
        ('Resultado do Teste de Perfil', {'fields': ('perfil_comportamental', 'total_i', 'total_c', 'total_a', 'total_o')}),
        ('Informações Adicionais', {'classes': ('collapse',), 'fields': ('preferencia_cargo', 'preferencia_turno', 'curriculo', 'pontos_fortes', 'lazer')}),
    )
    readonly_fields = ('perfil_comportamental', 'total_i', 'total_c', 'total_a', 'total_o')

class InscricaoAdmin(admin.ModelAdmin):
    list_display = ('get_nome_candidato', 'get_vaga_titulo', 'status', 'data_inscricao')
    list_filter = ('status', 'vaga__titulo', 'data_inscricao')
    search_fields = ('candidato__nome', 'candidato__email')
    list_editable = ('status',)
    actions = ['marcar_como_em_analise', 'marcar_como_entrevista', 'marcar_como_aprovado', 'marcar_como_rejeitado', 'exportar_para_csv']
    
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
                inscricao.candidato.nome,
                inscricao.candidato.email,
                inscricao.candidato.contato,
                inscricao.vaga.titulo,
                inscricao.get_status_display(),
                inscricao.notas_internas
            ])
        return response
    exportar_para_csv.short_description = "Exportar selecionadas para CSV"

    def get_nome_candidato(self, obj):
        return obj.candidato.nome
    get_nome_candidato.short_description = 'Nome do Candidato'

    def get_vaga_titulo(self, obj):
        return obj.vaga.titulo
    get_vaga_titulo.short_description = 'Vaga'

class PerguntaAdmin(admin.ModelAdmin):
    list_display = ('texto', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('texto',)

class RespostaCandidatoAdmin(admin.ModelAdmin):
    # ALTERAÇÃO: Trocamos 'pergunta' por um método mais claro
    list_display = ('candidato', 'get_texto_pergunta', 'perfil_escolhido')
    list_filter = ('perfil_escolhido', 'candidato')
    autocomplete_fields = ['candidato', 'pergunta']
    # Adicionamos uma barra de pesquisa
    search_fields = ('candidato__nome', 'pergunta__texto')

    # Nova função para buscar o texto da pergunta
    def get_texto_pergunta(self, obj):
        return obj.pergunta.texto
    # Define o nome que aparecerá no cabeçalho da coluna
    get_texto_pergunta.short_description = 'Texto da Pergunta'

# --- REGISTO DO NOVO MODELO EMPRESA ---
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)
# ---------------------------------------

# Registamos os modelos no nosso admin personalizado
admin_site.register(Empresa, EmpresaAdmin) # <-- Linha adicionada
admin_site.register(Vaga, VagaAdmin)
admin_site.register(Candidato, CandidatoAdmin)
admin_site.register(Inscricao, InscricaoAdmin)
admin_site.register(Pergunta, PerguntaAdmin)
admin_site.register(RespostaCandidato, RespostaCandidatoAdmin)
