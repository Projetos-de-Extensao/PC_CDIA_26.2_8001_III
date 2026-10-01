from django.contrib import admin
from .models import Lojista, Transacao

@admin.register(Lojista)
class LojistaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_fantasia', 'cnpj', 'email', 'criado_em')
    search_fields = ('nome_fantasia', 'cnpj', 'email')

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'lojista', 'valor', 'status', 'criado_em')
    list_filter = ('status', 'criado_em')
    search_fields = ('chave_pix', 'lojista__nome_fantasia')