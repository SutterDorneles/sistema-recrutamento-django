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
        
    # ✅ Este é o código mais importante. Ele verifica a validação no formulário.
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Tenta encontrar um candidato com o email fornecido
        candidato_existente = Candidato.objects.filter(email=email).first()
        
        if candidato_existente:
            # Se o candidato já existe, verifica se a última inscrição dele é incompleta.
            ultima_inscricao = Inscricao.objects.filter(candidato=candidato_existente).order_by('-data_inscricao').first()
            
            # Se a última inscrição existe e não é incompleta, levanta um erro.
            if ultima_inscricao and ultima_inscricao.status != 'incompleto':
                raise ValidationError(
                    'Este e-mail já foi usado para uma candidatura completa. '
                    'Para se candidatar a outra vaga, por favor, use um e-mail diferente ou entre em contato para ajuda.'
                )
            # Se a inscrição for incompleta ou não existir, o formulário passa.
            # A view irá lidar com a lógica de reaproveitar o perfil do candidato.
            
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