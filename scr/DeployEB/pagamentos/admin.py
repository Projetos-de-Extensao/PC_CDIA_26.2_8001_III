from django.contrib import admin

from .models import Categoria, ItemTransacao, Loja, Lojista, Produto, Transacao


@admin.register(Lojista)
class LojistaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_fantasia', 'cnpj', 'email', 'criado_em')
    search_fields = ('nome_fantasia', 'cnpj', 'email')


@admin.register(Loja)
class LojaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'lojista', 'cidade', 'ativo', 'criado_em')
    list_filter = ('ativo', 'cidade')
    search_fields = ('nome', 'cidade', 'lojista__nome_fantasia')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('nome', 'descricao')


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'lojista', 'preco', 'estoque', 'criado_em')
    list_filter = ('lojista', 'categorias')
    search_fields = ('nome', 'lojista__nome_fantasia', 'descricao')


@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'lojista', 'loja', 'valor', 'status', 'criado_em', 'finalizado_em')
    list_filter = ('status', 'criado_em', 'loja')
    search_fields = ('chave_pix', 'lojista__nome_fantasia')
    readonly_fields = ('status', 'criado_em', 'finalizado_em')


@admin.register(ItemTransacao)
class ItemTransacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'transacao', 'produto', 'quantidade', 'preco_unitario')
    list_filter = ('transacao', 'produto')
    search_fields = ('produto__nome', 'transacao__chave_pix')