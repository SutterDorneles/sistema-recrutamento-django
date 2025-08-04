from django import forms
from .models import Candidato

class CandidaturaForm(forms.ModelForm):
    class Meta:
        model = Candidato
        fields = [
            'nome', 'sexo', 'endereco', 'bairro', 'cidade', 'tempo_residencia',
            'contato', 'idade', 'estado_civil', 'tem_filhos', 'qtd_filhos',
            'idade_filhos', 'mora_com_filhos', 'moradia', 'meio_locomocao',
            'habitos', 'preferencia_cargo', 'preferencia_turno', 'melhor_trabalho',
            'pontos_fortes', 'lazer', 'objetivo_curto_prazo', 'objetivo_longo_prazo',
            'email', 'curriculo'
        ]
        widgets = {
            'tem_filhos': forms.RadioSelect(choices=[(True, 'Sim'), (False, 'Não')]),
            'mora_com_filhos': forms.RadioSelect(choices=[(True, 'Sim'), (False, 'Não')]),
            'sexo': forms.Select(choices=[('Masculino', 'Masculino'), ('Feminino', 'Feminino'), ('Outro', 'Outro')]),
            'estado_civil': forms.Select(choices=[('Solteiro', 'Solteiro'), ('Casado', 'Casado'), ('Divorciado', 'Divorciado'), ('Viúvo', 'Viúvo')]),
            'moradia': forms.Select(choices=[('Aluguel', 'Moro de aluguel'), ('Propria', 'Tenho casa própria')]),
            'preferencia_cargo': forms.Select(choices=[
                ('Garçom', 'Garçom'), ('Cozinha', 'Cozinha'), ('Copa', 'Copa'),
                ('Caixa', 'Caixa'), ('Serviços gerais', 'Serviços gerais'), ('Freelancer', 'Freelancer'),
            ]),
            'preferencia_turno': forms.Select(choices=[
                ('Diurno', 'Diurno (09:00 - 16:30)'),
                ('Noturno', 'Noturno (16:30 - 23:30)'),
                ('Qualquer', 'Qualquer turno'),
            ]),
            'habitos': forms.CheckboxSelectMultiple(choices=[
                ('Alcool', 'Ingere bebida alcoólica'),
                ('Fuma', 'Fuma'),
                ('Nenhum', 'Nenhum'),
                ('Outros', 'Outros...'),
            ]),
            'melhor_trabalho': forms.Textarea(attrs={'rows': 3}),
            'pontos_fortes': forms.Textarea(attrs={'rows': 3}),
            'lazer': forms.Textarea(attrs={'rows': 3}),
            'objetivo_curto_prazo': forms.Textarea(attrs={'rows': 2}),
            'objetivo_longo_prazo': forms.Textarea(attrs={'rows': 2}),
        }
