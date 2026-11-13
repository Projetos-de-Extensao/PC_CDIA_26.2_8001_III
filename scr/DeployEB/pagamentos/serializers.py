from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from .models import Categoria, ItemTransacao, Loja, Lojista, Produto, Transacao


class LojistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lojista
        fields = (
            'id',
            'nome_fantasia',
            'razao_social',
            'cnpj',
            'email',
            'criado_em',
        )
        read_only_fields = ('id', 'criado_em')


class LojaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loja
        fields = ('id', 'lojista', 'nome', 'cidade', 'ativo', 'criado_em')
        read_only_fields = ('id', 'criado_em')


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ('id', 'nome', 'descricao')
        read_only_fields = ('id',)


class ProdutoSerializer(serializers.ModelSerializer):
    categorias = serializers.PrimaryKeyRelatedField(many=True, queryset=Categoria.objects.all(), required=False)

    class Meta:
        model = Produto
        fields = (
            'id',
            'lojista',
            'nome',
            'descricao',
            'preco',
            'estoque',
            'atributos',
            'categorias',
            'criado_em',
            'atualizado_em',
        )
        read_only_fields = ('id', 'criado_em', 'atualizado_em')

    def validate_preco(self, value):
        if value <= 0:
            raise serializers.ValidationError('O preço do produto deve ser maior que zero.')
        return value

    def validate_atributos(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError('Os atributos devem ser um objeto JSON válido.')
        return value


class ItemTransacaoSerializer(serializers.ModelSerializer):
    produto = serializers.PrimaryKeyRelatedField(queryset=Produto.objects.all())

    class Meta:
        model = ItemTransacao
        fields = ('id', 'produto', 'quantidade', 'preco_unitario')
        read_only_fields = ('id', 'preco_unitario')

    def validate_quantidade(self, value):
        if value <= 0:
            raise serializers.ValidationError('A quantidade deve ser maior que zero.')
        return value


class TransacaoSerializer(serializers.ModelSerializer):
    loja = serializers.PrimaryKeyRelatedField(queryset=Loja.objects.all(), required=False, allow_null=True)
    itens = ItemTransacaoSerializer(many=True, required=False)

    def validate(self, attrs):
        if 'status' in self.initial_data:
            raise serializers.ValidationError({
                'status': 'Use as ações aprovar ou cancelar para alterar o status.'
            })

        lojista = attrs.get('lojista')
        loja = attrs.get('loja')
        if lojista and loja and loja.lojista_id != lojista.id:
            raise serializers.ValidationError({'loja': 'A loja deve pertencer ao lojista informado.'})

        return attrs

    def validate_valor(self, value):
        if value <= 0:
            raise serializers.ValidationError('O valor da transação deve ser maior que zero.')
        return value

    def create(self, validated_data):
        itens_data = validated_data.pop('itens', [])
        with transaction.atomic():
            transacao = Transacao.objects.create(**validated_data)
            total_itens = Decimal('0.00')
            for item_data in itens_data:
                produto = item_data['produto']
                if produto.lojista_id != transacao.lojista_id:
                    raise serializers.ValidationError({
                        'itens': 'Cada item da transação deve pertencer ao lojista do pedido.'
                    })
                quantidade = item_data['quantidade']
                item = ItemTransacao.objects.create(
                    transacao=transacao,
                    produto=produto,
                    quantidade=quantidade,
                    preco_unitario=produto.preco,
                )
                total_itens += item.total

            if itens_data and transacao.valor != total_itens:
                raise serializers.ValidationError({
                    'valor': 'O valor da transação deve coincidir com a soma dos itens.'
                })
            return transacao

    class Meta:
        model = Transacao
        fields = (
            'id',
            'lojista',
            'loja',
            'valor',
            'chave_pix',
            'status',
            'observacoes',
            'itens',
            'criado_em',
            'finalizado_em',
        )
        read_only_fields = ('id', 'status', 'criado_em', 'finalizado_em')
