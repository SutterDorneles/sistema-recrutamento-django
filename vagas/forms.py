from django import forms
from .models import Candidato, Vaga

class CandidaturaForm(forms.ModelForm):
    class Meta:
        model = Candidato
        fields = [
            'nome', 'sexo', 'cep', 'endereco', 'bairro', 'cidade', 'tempo_residencia',
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
            'cep': forms.TextInput(attrs={'id': 'cep'}),
            'endereco': forms.TextInput(attrs={'id': 'rua'}),
            'bairro': forms.TextInput(attrs={'id': 'bairro'}),
            'cidade': forms.TextInput(attrs={'id': 'cidade'}),
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

class ContratacaoForm(forms.Form):
    """
    Formulário para finalizar a contratação de um candidato,
    permitindo ajustar o cargo e definir a remuneração e data de admissão.
    """
    # Usamos um ModelChoiceField para que o cargo seja uma lista de opções
    cargo = forms.ChoiceField(
        choices=Vaga.CARGO_CHOICES,
        label="Cargo de Contratação",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    remuneracao = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Remuneração (Salário)",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    data_admissao = forms.DateField(
        label="Data de Admissão",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

# --- NOVO FORMULÁRIO PARA AGENDAR ENTREVISTAS ---
class AgendamentoEntrevistaForm(forms.Form):
    data_entrevista = forms.DateTimeField(
        label="Data e Hora da Entrevista",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
# ---------------------------------------------