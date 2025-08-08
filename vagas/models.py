# Em vagas/models.py

from django.db import models
from django.utils import timezone

class Empresa(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Empresa")
    logotipo = models.ImageField(upload_to='logotipos/', null=True, blank=True, verbose_name="Logotipo")
    descricao = models.TextField(blank=True, null=True, verbose_name="Sobre a Empresa")
    def __str__(self): return self.nome
    class Meta: verbose_name = "Empresa"; verbose_name_plural = "Empresas"

class Vaga(models.Model):
    TURNO_CHOICES = [('Diurno', 'Diurno'), ('Noturno', 'Noturno'), ('Qualquer', 'Qualquer Turno')]
    CARGO_CHOICES = [
        ('Garçom', 'Garçom'), ('Cumim', 'Cumim'), ('Caixa', 'Caixa'), ('Bartender', 'Bartender'),
        ('Montagem de lanche', 'Montagem de lanche'), ('Cozinheiro', 'Cozinheiro'), ('Chapeiro', 'Chapeiro'),
        ('Auxiliar de cozinha', 'Auxiliar de cozinha'), ('Auxiliar de limpeza', 'Auxiliar de limpeza'),
        ('Serviços gerais', 'Serviços gerais'), ('Freelancer', 'Freelancer'),
    ]
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="vagas", verbose_name="Empresa")
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    requisitos = models.TextField()
    turno = models.CharField(max_length=50, choices=TURNO_CHOICES, null=True, blank=True)
    tipo_cargo = models.CharField(max_length=100, choices=CARGO_CHOICES, null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.titulo} ({self.empresa.nome})"

class Candidato(models.Model):
    nome = models.CharField(verbose_name="Nome Completo", max_length=100, default="Não informado")
    sexo = models.CharField(max_length=20, default="Não informado")
    cep = models.CharField(max_length=9, blank=True, null=True)
    endereco = models.CharField(verbose_name="Endereço", max_length=255, default="Não informado")
    bairro = models.CharField(max_length=100, default="Não informado")
    cidade = models.CharField(max_length=100, default="Não informado")
    tempo_residencia = models.CharField(verbose_name="Quanto tempo reside no último endereço?", max_length=50, default="Não informado")
    contato = models.CharField(max_length=50, default="Não informado")
    idade = models.IntegerField(default=0)
    estado_civil = models.CharField(max_length=50, default="Não informado")
    tem_filhos = models.BooleanField(verbose_name="Tem filhos?", default=False)
    qtd_filhos = models.IntegerField(verbose_name="Quantos filhos?", blank=True, null=True, default=None)
    idade_filhos = models.CharField(verbose_name="Idade dos filhos?", max_length=100, blank=True, null=True, default=None)
    mora_com_filhos = models.BooleanField(verbose_name="Mora com os filhos?", default=False)
    moradia = models.CharField(max_length=50, default="Não informado")
    meio_locomocao = models.CharField(max_length=100, default="Não informado")
    habitos = models.CharField(verbose_name="Hábitos", max_length=200, default="Nenhum")
    preferencia_cargo = models.CharField(verbose_name="Preferência de cargo", max_length=100, default="Não informado")
    preferencia_turno = models.CharField(verbose_name="Preferência de turno", max_length=50, default="Não informado")
    melhor_trabalho = models.TextField(verbose_name="Qual foi o trabalho que você mais gostou, teve o melhor desempenho e mais se destacou?", blank=True, default="")
    pontos_fortes = models.TextField(verbose_name="No que você se considera bom?", blank=True, default="")
    lazer = models.TextField(verbose_name="O que você mais gosta de fazer nas horas vagas?", blank=True, default="")
    objetivo_curto_prazo = models.TextField(verbose_name="Quais são seus objetivos pessoais a curto prazo", blank=True, default="")
    objetivo_longo_prazo = models.TextField(verbose_name="Quais são seus objetivos pessoais a longo prazo", blank=True, default="")
    email = models.EmailField(default="nao.informado@exemplo.com")
    curriculo = models.FileField(verbose_name="Currículo", upload_to='curriculos/', blank=True, null=True)
    total_i = models.IntegerField(default=0, verbose_name="Total 'I' (Águia)")
    total_c = models.IntegerField(default=0, verbose_name="Total 'C' (Gato)")
    total_a = models.IntegerField(default=0, verbose_name="Total 'A' (Tubarão)")
    total_o = models.IntegerField(default=0, verbose_name="Total 'O' (Lobo)")
    perfil_comportamental = models.CharField(max_length=50, blank=True, null=True, verbose_name="Perfil Comportamental")
    contratado = models.BooleanField(default=False, verbose_name="Já foi contratado?")
    def __str__(self): return self.nome

class Funcionario(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('demitido', 'Demitido'),
        ('lista_negra', 'Lista Negra'),
    ]
    perfil_candidato = models.OneToOneField(Candidato, on_delete=models.CASCADE, primary_key=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True)
    cargo = models.CharField(max_length=100)
    data_admissao = models.DateField(auto_now_add=True)
    data_demissao = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo')
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações (ex: motivo da demissão)")
    def __str__(self): return self.perfil_candidato.nome
    class Meta: verbose_name = "Funcionário"; verbose_name_plural = "Funcionários"

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

class FuncionarioListaNegra(Funcionario):
    class Meta:
        proxy = True
        verbose_name = "Funcionário em Lista Negra"
        verbose_name_plural = "Funcionários em Lista Negra"

class Inscricao(models.Model):
    STATUS_CHOICES = [
        ('recebida', 'Recebida'), ('em_analise', 'Em Análise'), ('entrevista', 'Entrevista Agendada'),
        ('aprovado', 'Aprovado'), ('rejeitado', 'Rejeitado'),
    ]
    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE)
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE)
    data_inscricao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recebida', verbose_name="Status da Candidatura")
    notas_internas = models.TextField(blank=True, null=True, verbose_name="Notas Internas do Recrutador")
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
