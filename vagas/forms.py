from django import forms
from .models import Candidato, Vaga, Cargo, Empresa, Inscricao
from django.core.exceptions import ValidationError

class CandidaturaForm(forms.ModelForm):

    class Meta:
        model = Candidato
        fields = [
            'nome', 'sexo', 'cep', 'endereco', 'bairro', 'cidade', 'tempo_residencia',
            'contato', 'idade', 'estado_civil', 'tem_filhos', 'qtd_filhos',
            'idade_filhos', 'mora_com_filhos', 'moradia', 'meio_locomocao',
            'habitos', 'preferencia_turno', 'melhor_trabalho',
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
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        candidato_existente = Candidato.objects.filter(email__iexact=email).first()
        
        if candidato_existente and candidato_existente.contratado:
            raise ValidationError(
                'Este e-mail já está associado a um funcionário ativo. Por favor, utilize um e-mail diferente.'
            )
        
        return email

class ContratacaoForm(forms.Form):
    # --- NOVO CAMPO ADICIONADO ---
    empresa = forms.ModelChoiceField(
        queryset=Empresa.objects.all(),
        label="Empresa de Contratação",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # -----------------------------
    cargo = forms.ModelChoiceField(
        queryset=Cargo.objects.all(),
        label="Cargo de Contratação",
        empty_label="--------",
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
