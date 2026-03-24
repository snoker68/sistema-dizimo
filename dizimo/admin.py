from django.contrib import admin
from .models import Dizimista, Pagamento

@admin.register(Dizimista)
class DizimistaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'bairro', 'estado_civil', 'valor_primeira_contribuicao')
    search_fields = ('nome', 'bairro')

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('dizimista', 'valor', 'data_pagamento', 'forma_pagamento', 'registrado_por')
    list_filter = ('data_pagamento', 'forma_pagamento')
    search_fields = ('dizimista__nome',)
