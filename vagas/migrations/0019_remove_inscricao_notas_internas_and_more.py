# Seu arquivo de migração - 00XX_auto_....py

from django.db import migrations, models


# Esta função irá mover os dados
def move_notas_internas(apps, schema_editor):
    Inscricao = apps.get_model("vagas", "Inscricao")
    Candidato = apps.get_model("vagas", "Candidato")
    
    # Itera sobre todas as inscrições que têm notas internas
    for inscricao in Inscricao.objects.exclude(notas_internas=None):
        if inscricao.candidato:
            # Move o conteúdo do campo antigo para o novo
            candidato = inscricao.candidato
            candidato.notas_internas = inscricao.notas_internas
            
            # Salva o objeto candidato
            candidato.save()

class Migration(migrations.Migration):

    dependencies = [
        ("vagas", "0018_alter_vaga_tipo_cargo"),
    ]

    operations = [
        # 1. Adiciona o novo campo na tabela de Candidato
        migrations.AddField(
            model_name="candidato",
            name="notas_internas",
            field=models.TextField(
                blank=True,
                verbose_name="Notas Internas do Recrutador",
            ),
        ),
        
        # 2. Executa a função que move os dados
        migrations.RunPython(move_notas_internas),

        # 3. Remove o campo antigo da tabela de Inscrição
        migrations.RemoveField(
            model_name="inscricao",
            name="notas_internas",
        ),
    ]