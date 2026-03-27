from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Dizimista, Pagamento

class AgenteCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'is_superuser')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class DizimistaForm(forms.ModelForm):
    class Meta:
        model = Dizimista
        fields = ['numero_dizimista', 'nome', 'endereco', 'bairro', 'estado_civil', 'nome_conjuge', 'valor_primeira_contribuicao']
        widgets = {
            'numero_dizimista': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'estado_civil': forms.Select(attrs={'class': 'form-select', 'id': 'id_estado_civil'}),
            'nome_conjuge': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_nome_conjuge'}),
            'valor_primeira_contribuicao': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = ['dizimista', 'valor', 'forma_pagamento']
        widgets = {
            'dizimista': forms.Select(attrs={'class': 'form-select'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-select'}),
        }
