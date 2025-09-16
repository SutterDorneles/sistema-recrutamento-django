# Em vagas/management/commands/auditar_candidatos.py

from django.core.management.base import BaseCommand
from vagas.models import Funcionario, Candidato
from django.db.models import Count, Q

class Command(BaseCommand):
    help = 'Audita a base de dados de candidatos em busca de perfis corrompidos por bugs antigos.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- INICIANDO AUDITORIA DE PERFIS DE CANDIDATOS ---"))
        self.stdout.write("Procurando por perfis corrompidos...")

        # ======================================================================
        # CHECAGEM 1: Funcionários com novas inscrições (Alerta Grave)
        # ======================================================================
        funcionarios_ativos = Funcionario.objects.filter(status='ativo')
        self.stdout.write(self.style.WARNING(f"\n[CHECAGEM 1] Verificando {funcionarios_ativos.count()} funcionários ativos..."))

        problema_grave_encontrado = False
        for func in funcionarios_ativos:
            candidato_associado = func.perfil_candidato
            
            inscricoes_suspeitas = candidato_associado.inscricao_set.filter(
                Q(status='incompleto') | Q(status='recebida')
            ).exclude(
                data_inscricao__date__lt=func.data_admissao
            )

            if inscricoes_suspeitas.exists():
                self.stdout.write(self.style.ERROR(
                    f"  [ALERTA GRAVE] O perfil do funcionário '{func}' (Candidato ID: {candidato_associado.id}) "
                    f"foi usado para novas candidaturas APÓS a contratação."
                ))
                problema_grave_encontrado = True

        if not problema_grave_encontrado:
            self.stdout.write(self.style.SUCCESS("  => Nenhuma anomalia grave encontrada em perfis de funcionários."))

        # ======================================================================
        # CHECAGEM 2: Candidatos com múltiplas vagas distintas (Alerta Moderado)
        # ======================================================================
        candidatos_para_checar = Candidato.objects.filter(contratado=False).annotate(
            num_inscricoes=Count('inscricao'),
            tipos_de_cargo_distintos=Count('inscricao__vaga__tipo_cargo', distinct=True)
        ).filter(tipos_de_cargo_distintos__gte=3)

        self.stdout.write(self.style.WARNING("\n[CHECAGEM 2] Verificando candidatos com perfis de vaga muito diversos..."))

        if not candidatos_para_checar.exists():
            self.stdout.write(self.style.SUCCESS("  => Nenhuma anomalia moderada encontrada."))
        else:
            for candidato in candidatos_para_checar:
                self.stdout.write(
                    f"  [ALERTA MODERADO] O candidato '{candidato.nome}' (ID: {candidato.id}) "
                    f"se inscreveu para {candidato.tipos_de_cargo_distintos} tipos de cargo diferentes. "
                    "Recomenda-se verificação manual."
                )

        self.stdout.write(self.style.SUCCESS("\n--- AUDITORIA CONCLUÍDA ---"))