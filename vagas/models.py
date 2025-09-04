# Em vagas/models.py

from django.db import models
from django.utils import timezone
from datetime import date, timedelta
import re
from django.contrib.auth.models import User

class Empresa(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Empresa")
    logotipo = models.ImageField(upload_to='logotipos/', null=True, blank=True, verbose_name="Logotipo")
    descricao = models.TextField(blank=True, null=True, verbose_name="Sobre a Empresa")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem de Exibição")
    def __str__(self): return self.nome
    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['ordem']
        
# --- NOVA TABELA PARA GERIR OS CARGOS ---
class Cargo(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome
    
    class Meta:
        ordering = ['nome']
# ----------------------------------------        

class Vaga(models.Model):
    TURNO_CHOICES = [('Diurno', 'Diurno'), ('Noturno', 'Noturno'), ('Qualquer', 'Qualquer Turno')]
    CARGO_CHOICES = [
        ('Garçom', 'Garçom'), ('Cumim', 'Cumim'), ('Caixa', 'Caixa'), ('Bartender', 'Bartender'),
        ('Montagem de lanche', 'Montagem de lanche'), ('Cozinheiro', 'Cozinheiro'), ('Chapeiro', 'Chapeiro'),
        ('Auxiliar de cozinha', 'Auxiliar de cozinha'), ('Auxiliar de limpeza', 'Auxiliar de limpeza'), ('Freelancer', 'Freelancer'), ('instrutor_funcional', 'Instrutor(a) de Treinamento Funcional'), ('estagiario', 'Estagiário'),
    ]
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="vagas", verbose_name="Empresa")
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    requisitos = models.TextField()
    turno = models.CharField(max_length=50, choices=TURNO_CHOICES, null=True, blank=True)
    tipo_cargo = models.CharField(max_length=100, choices=CARGO_CHOICES, null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    numero_vagas = models.IntegerField(default=1, verbose_name="Número de Vagas")    
    ativo = models.BooleanField(default=True, verbose_name="Vaga Ativa")    
    def __str__(self): return f"{self.titulo} ({self.empresa.nome})"
        

class Candidato(models.Model):
    nome = models.CharField(verbose_name="Nome Completo", max_length=100)
    sexo = models.CharField(max_length=20, default="Não informado")
    # --- NOVO CAMPO ADICIONADO ---
    cpf = models.CharField(max_length=14, null=True, blank=True, unique=True, verbose_name="CPF")
    # -----------------------------
    cep = models.CharField(max_length=9, blank=True, null=True)
    endereco = models.CharField(verbose_name="Endereço", max_length=255, default="Não informado")
    bairro = models.CharField(max_length=100, default="Não informado")
    cidade = models.CharField(max_length=100, default="Não informado")
    tempo_residencia = models.CharField(verbose_name="Quanto tempo reside no último endereço?", max_length=50, default="Não informado")
    contato = models.CharField(max_length=50, verbose_name="Celular (com Whatsapp e DDD)")
    idade = models.IntegerField(default=0)
    estado_civil = models.CharField(max_length=50, default="Não informado")
    tem_filhos = models.BooleanField(verbose_name="Tem filhos?", default=False)
    qtd_filhos = models.IntegerField(verbose_name="Quantos filhos?", blank=True, null=True, default=None)
    idade_filhos = models.CharField(verbose_name="Idade dos filhos?", max_length=100, blank=True, null=True, default=None)
    mora_com_filhos = models.BooleanField(verbose_name="Mora com os filhos?", default=False)
    moradia = models.CharField(max_length=50, default="Não informado")
    meio_locomocao = models.CharField(max_length=100, default="Não informado", verbose_name="Meio de locomoção")
    habitos = models.CharField(verbose_name="Hábitos", max_length=200, default="Nenhum")
    preferencia_cargo = models.CharField(verbose_name="Preferência de cargo", max_length=100, default="Não informado")
    preferencia_turno = models.CharField(verbose_name="Preferência de turno", max_length=50, default="Não informado")
    melhor_trabalho = models.TextField(verbose_name="Qual foi o trabalho que você mais gostou...", blank=True, default="")
    pontos_fortes = models.TextField(verbose_name="No que você se considera bom?", blank=True, default="")
    lazer = models.TextField(verbose_name="O que você mais gosta de fazer nas horas vagas?", blank=True, default="")
    objetivo_curto_prazo = models.TextField(verbose_name="Quais são seus objetivos pessoais a curto prazo", blank=True, default="")
    objetivo_longo_prazo = models.TextField(verbose_name="Quais são seus objetivos pessoais a longo prazo", blank=True, default="")
    email = models.EmailField() 
    curriculo = models.FileField(verbose_name="Currículo", upload_to='curriculos/', blank=True, null=True)
    total_i = models.IntegerField(default=0, verbose_name="Total 'I' (Águia)")
    total_c = models.IntegerField(default=0, verbose_name="Total 'C' (Gato)")
    total_a = models.IntegerField(default=0, verbose_name="Total 'A' (Tubarão)")
    total_o = models.IntegerField(default=0, verbose_name="Total 'O' (Lobo)")
    perfil_comportamental = models.CharField(max_length=50, blank=True, null=True, verbose_name="Perfil Comportamental")
    contratado = models.BooleanField(default=False, verbose_name="Já foi contratado?")
    def __str__(self): return self.nome
    
    # --- FUNÇÃO RESTAURADA ---
    def get_whatsapp_url(self):
        if not self.contato:
            return ""
        # Limpa o número, removendo tudo o que não for dígito
        numero_limpo = re.sub(r'\D', '', self.contato)
        # Adiciona o código do Brasil (55) se não estiver presente
        if len(numero_limpo) >= 10 and not numero_limpo.startswith('55'):
            numero_limpo = '55' + numero_limpo
        return f"https://wa.me/{numero_limpo}"
    # --------------------------

class Funcionario(models.Model):
    # --- DEFINIÇÃO DOS TIPOS DE CONTRATO ---
    CONTRATO_30_60 = '30_60'
    CONTRATO_45_90 = '45_90'
    CONTRATO_CHOICES = [
        (CONTRATO_30_60, '30 + 30 dias (60 dias)'),
        (CONTRATO_45_90, '45 + 45 dias (90 dias)'),
    ]    
    
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('demitido', 'Demitido'),
        ('observacao', 'Com Observação'),
    ]
    perfil_candidato = models.OneToOneField(Candidato, on_delete=models.CASCADE, primary_key=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True)
    cargo = models.CharField(max_length=100)
    # --- NOVO CAMPO ADICIONADO ---
    remuneracao = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # -----------------------------
    data_admissao = models.DateField() # Alterado para ser obrigatório
    data_demissao = models.DateField(null=True, blank=True)
    data_direito_ferias = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo')
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações (ex: motivo da demissão)")
    # --- NOVOS CAMPOS ---
    tipo_experiencia = models.CharField(
        max_length=5,
        choices=CONTRATO_CHOICES,
        verbose_name="Tipo de Contrato de Experiência",
        blank=True, # Permite que o campo fique em branco
        null=True
    )
    data_fim_experiencia = models.DateField(
        verbose_name="Data Final da Experiência",
        null=True,
        blank=True,
        editable=False # O usuário não pode editar este campo diretamente
    )    
    # --- NOVOS CAMPOS PARA CONTROLE DE FÉRIAS ---
    data_inicio_gozo_ferias = models.DateField(
        verbose_name="Início do Gozo de Férias",
        null=True,
        blank=True
    )
    data_fim_gozo_ferias = models.DateField(
        verbose_name="Fim do Gozo de Férias",
        null=True,
        blank=True
    )
    
    def __str__(self): return self.perfil_candidato.nome

    # --- ATUALIZAÇÃO DA LÓGICA DE COR ---
    def get_row_class(self):
        hoje = timezone.now().date()

        # Condição de experiência continua a mesma
        if self.data_fim_experiencia and hoje <= self.data_fim_experiencia:
            return "row-experiencia"

        # --- NOVA LÓGICA DE FÉRIAS VENCIDAS ---
        # Fica vermelho SE:
        # 1. A data de direito a férias já passou
        # 2. E AINDA NÃO foi registrada uma data de início do gozo de férias
        if self.data_direito_ferias and hoje > self.data_direito_ferias and not self.data_inicio_gozo_ferias:
            return "row-ferias-vencidas"

        return ""
    
    # --- NOVA FUNÇÃO PARA CALCULAR O TEMPO DE SERVIÇO ---
    def tempo_de_servico(self):
        if self.data_admissao:
            hoje = date.today()
            delta = hoje - self.data_admissao
            anos = delta.days // 365
            meses = (delta.days % 365) // 30
            if anos > 0:
                return f"{anos} ano(s) e {meses} mes(es)"
            return f"{meses} mes(es)"
        return "N/A"
    tempo_de_servico.short_description = "Tempo de Serviço"
    # ----------------------------------------------------
    
    def save(self, *args, **kwargs):
        # --- LÓGICA DO CONTRATO DE EXPERIÊNCIA ---
        if self.tipo_experiencia and self.data_admissao:
            if self.tipo_experiencia == self.CONTRATO_30_60:
                self.data_fim_experiencia = self.data_admissao + timedelta(days=59)
            elif self.tipo_experiencia == self.CONTRATO_45_90:
                self.data_fim_experiencia = self.data_admissao + timedelta(days=89)
        else:
            self.data_fim_experiencia = None

        # --- LÓGICA DO DIREITO A FÉRIAS (da sua função antiga) ---
        if self.data_admissao:
            self.data_direito_ferias = self.data_admissao + timedelta(days=365) # Ou relativedelta(years=1) se preferir
        
        # Chama o método save original para salvar tudo no banco
        super().save(*args, **kwargs)

    class Meta: verbose_name = "Funcionário"; verbose_name_plural = "Funcionários (Todos)"

class FuncionarioAtivo(Funcionario):
    class Meta:
        proxy = True
        verbose_name = "Funcionário Ativo"
        verbose_name_plural = "Funcionários Ativos"

class FuncionarioDemitido(Funcionario):
    class Meta:
        proxy = True
        verbose_name = "Funcionário Demitido"
        verbose_name_plural = "Funcionários Demitidos"

class FuncionarioComObservacao(Funcionario):
    class Meta:
        proxy = True
        verbose_name = "Funcionário com Observação"
        verbose_name_plural = "Funcionários com Observação"

class Inscricao(models.Model):
    STATUS_CHOICES = [
        ('incompleto', 'Incompleto'),        
        ('recebida', 'Recebida'), ('em_analise', 'Em Análise'), ('entrevista', 'Entrevista Agendada'),
        ('aprovado', 'Aprovado'), ('aguardando_documentacao', 'Aguardando Documentação'), ('rejeitado', 'Rejeitado'),
    ]
    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE)
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE)
    data_inscricao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='incompleto', verbose_name="Status da Candidatura")
    notas_internas = models.TextField(blank=True, null=True, verbose_name="Notas Internas do Recrutador")
    
    # --- Correção do plural no menu lateral ---
    class Meta:
        verbose_name = "Inscrição"
        verbose_name_plural = "Inscrições"    
    
    # --- NOVOS CAMPOS PARA A AGENDA ---
    data_entrevista = models.DateTimeField(null=True, blank=True, verbose_name="Data e Hora da Entrevista")
    # ----------------------------------    
    
    def __str__(self): return f'{self.candidato.nome} - {self.vaga.titulo}'

class Pergunta(models.Model):
    texto = models.CharField(max_length=255, verbose_name="Texto da Pergunta")
    alternativa_i = models.CharField(max_length=255, verbose_name="Alternativa (I - Águia)")
    alternativa_c = models.CharField(max_length=255, verbose_name="Alternativa (C - Gato)")
    alternativa_a = models.CharField(max_length=255, verbose_name="Alternativa (A - Tubarão)")
    alternativa_o = models.CharField(max_length=255, verbose_name="Alternativa (O - Lobo)")
    ativo = models.BooleanField(default=True)
    def __str__(self): return self.texto

class RespostaCandidato(models.Model):
    PERFIL_CHOICES = [('I', 'I'), ('C', 'C'), ('A', 'A'), ('O', 'O')]
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE)
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE)
    perfil_escolhido = models.CharField(max_length=1, choices=PERFIL_CHOICES, verbose_name="Perfil Escolhido")
    class Meta: unique_together = ('candidato', 'pergunta')
    def __str__(self): return f"Resposta de {self.candidato.nome} para '{self.pergunta.texto}' foi '{self.perfil_escolhido}'"

# HISTÓRICO DO FUNCIONÁRIO
class HistoricoFuncionario(models.Model):
    TIPO_CHOICES = [
        # Positivas / Desenvolvimento
        ('ELOGIO',              'Elogio / Reconhecimento'),
        ('FEEDBACK',            'Feedback / Alinhamento'),
        ('TREINAMENTO',         'Treinamento / Capacitação'),
        
        # Administrativas / Contratuais
        ('PROMOCAO',            'Promoção / Aumento'),
        ('ALTERACAO_CONTRATUAL','Alteração Contratual'),      
        ('ATESTADO',            'Apresentação de Atestado'),
        
        # Corretivas / Ocorrências
        ('ADVERTENCIA',         'Advertência (Verbal ou Escrita)'),
        ('FALTA_ATRASO',        'Falta / Atraso'),
        ('OCORRENCIA_OP',       'Ocorrência Operacional'),   
        ('RECLAMACAO_CLIENTE',  'Reclamação de Cliente'),   
        
        # Neutra
        ('OBSERVACAO',          'Observação Geral'),
    ]

    funcionario = models.ForeignKey(
        Funcionario, # Ou FuncionarioAtivo
        on_delete=models.CASCADE,
        related_name='historico' # Importante para relacionar
    )
    data_ocorrencia = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='OBSERVACAO')
    descricao = models.TextField(verbose_name="Descrição do Evento")
    criado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Registro de Histórico"
        verbose_name_plural = "Registros de Histórico"
        ordering = ['-data_ocorrencia'] # Mostra os mais recentes primeiro

    def __str__(self):
        return f"{self.get_tipo_display()} para {self.funcionario} em {self.data_ocorrencia.strftime('%d/%m/%Y')}"    

class PerfilGerente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_gerente')
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, verbose_name="Loja que Gerencia")

    class Meta:
        verbose_name = "Perfil de Gerente"
        verbose_name_plural = "Perfis de Gerente"

    def __str__(self):
        return f"Gerente {self.usuario.username} da loja {self.empresa.nome}"