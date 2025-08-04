# Em vagas/models.py

from django.db import models

class Vaga(models.Model):
    # ... (seu modelo Vaga continua o mesmo)
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    requisitos = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class Candidato(models.Model):
    # ... (seus campos existentes continuam aqui)
    nome = models.CharField(max_length=100, default="Não informado")
    sexo = models.CharField(max_length=20, default="Não informado")
    endereco = models.CharField(max_length=255, default="Não informado")
    bairro = models.CharField(max_length=100, default="Não informado")
    cidade = models.CharField(max_length=100, default="Não informado")
    tempo_residencia = models.CharField(max_length=50, default="Não informado")
    contato = models.CharField(max_length=50, default="Não informado")
    idade = models.IntegerField(default=0)
    estado_civil = models.CharField(max_length=50, default="Não informado")
    tem_filhos = models.BooleanField(default=False)
    qtd_filhos = models.IntegerField(blank=True, null=True, default=None)
    idade_filhos = models.CharField(max_length=100, blank=True, null=True, default=None)
    mora_com_filhos = models.BooleanField(default=False)
    moradia = models.CharField(max_length=50, default="Não informado")
    meio_locomocao = models.CharField(max_length=100, default="Não informado")
    habitos = models.CharField(max_length=200, default="Nenhum")
    preferencia_cargo = models.CharField(max_length=100, default="Não informado")
    preferencia_turno = models.CharField(max_length=50, default="Não informado")
    melhor_trabalho = models.TextField(blank=True, default="")
    pontos_fortes = models.TextField(blank=True, default="")
    lazer = models.TextField(blank=True, default="")
    objetivo_curto_prazo = models.TextField(blank=True, default="")
    objetivo_longo_prazo = models.TextField(blank=True, default="")
    email = models.EmailField(default="nao.informado@exemplo.com")
    curriculo = models.FileField(upload_to='curriculos/', blank=True, null=True)

    # --- CAMPOS DO TESTE ATUALIZADOS ---
    total_i = models.IntegerField(default=0, verbose_name="Total 'I' (Águia)")
    total_c = models.IntegerField(default=0, verbose_name="Total 'C' (Gato)")
    total_a = models.IntegerField(default=0, verbose_name="Total 'A' (Tubarão)")
    total_o = models.IntegerField(default=0, verbose_name="Total 'O' (Lobo)")
    perfil_comportamental = models.CharField(max_length=50, blank=True, null=True, verbose_name="Perfil Comportamental")
    # ------------------------------------

    def __str__(self):
        return self.nome

class Inscricao(models.Model):
    # ... (seu modelo Inscricao continua o mesmo)
    STATUS_CHOICES = [
        ('recebida', 'Recebida'),
        ('em_analise', 'Em Análise'),
        ('entrevista', 'Entrevista Agendada'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    ]
    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE)
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE)
    data_inscricao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recebida', verbose_name="Status da Candidatura")
    notas_internas = models.TextField(blank=True, null=True, verbose_name="Notas Internas do Recrutador")

    def __str__(self):
        return f'{self.candidato.nome} - {self.vaga.titulo}'

# --- MODELO DE PERGUNTA ATUALIZADO ---
class Pergunta(models.Model):
    texto = models.CharField(max_length=255, verbose_name="Texto da Pergunta")
    alternativa_i = models.CharField(max_length=255, verbose_name="Alternativa (I - Águia)")
    alternativa_c = models.CharField(max_length=255, verbose_name="Alternativa (C - Gato)")
    alternativa_a = models.CharField(max_length=255, verbose_name="Alternativa (A - Tubarão)")
    alternativa_o = models.CharField(max_length=255, verbose_name="Alternativa (O - Lobo)")
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.texto

# --- MODELO DE RESPOSTA ATUALIZADO ---
class RespostaCandidato(models.Model):
    PERFIL_CHOICES = [('I', 'I'), ('C', 'C'), ('A', 'A'), ('O', 'O')]
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE)
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE)
    perfil_escolhido = models.CharField(max_length=1, choices=PERFIL_CHOICES, verbose_name="Perfil Escolhido")

    class Meta:
        unique_together = ('candidato', 'pergunta')

    def __str__(self):
        return f"Resposta de {self.candidato.nome} para '{self.pergunta.texto}' foi '{self.perfil_escolhido}'"

