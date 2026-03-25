from django.db import models
from django.contrib.auth.models import User

class Dizimista(models.Model):
    ESTADO_CIVIL_CHOICES = [
        ('Solteiro', 'Solteiro'),
        ('Casado', 'Casado'),
    ]

    numero_dizimista = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nº Dizimista")
    nome = models.CharField(max_length=200)
    endereco = models.CharField(max_length=255)
    bairro = models.CharField(max_length=100)
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES)
    nome_conjuge = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nome do Cônjuge")
    valor_primeira_contribuicao = models.DecimalField(max_digits=10, decimal_places=2)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class Pagamento(models.Model):
    FORMA_PAGAMENTO_CHOICES = [
        ('Dinheiro', 'Dinheiro'),
        ('PIX', 'PIX'),
        ('Cartão de Débito', 'Cartão de Débito'),
        ('Cartão de Crédito', 'Cartão de Crédito'),
    ]

    dizimista = models.ForeignKey(Dizimista, on_delete=models.CASCADE, related_name='pagamentos')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_pagamento = models.DateField()
    forma_pagamento = models.CharField(max_length=50, choices=FORMA_PAGAMENTO_CHOICES)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='pagamentos_registrados')
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dizimista.nome} - R$ {self.valor} em {self.data_pagamento}"
