from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from .models import Categoria, ItemTransacao, Loja, Lojista, Produto, Transacao
from .services import TransacaoService


class LojistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lojista
        fields = (
            'id',
            'nome_fantasia',
            'razao_social',
            'cnpj',
            'email',
            'status_conta',
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
        if 'estoque' in value and (
            type(value['estoque']) is not int or value['estoque'] < 0
        ):
            raise serializers.ValidationError(
                'O atributo estoque deve ser um número inteiro maior ou igual a zero.'
            )
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

        lojista = attrs.get('lojista') or getattr(self.instance, 'lojista', None)
        loja = attrs.get('loja') or getattr(self.instance, 'loja', None)
        if lojista and loja and loja.lojista_id != lojista.id:
            raise serializers.ValidationError({'loja': 'A loja deve pertencer ao lojista informado.'})

        if lojista is not None:
            try:
                TransacaoService.validar_lojista_ativo(lojista)
            except Exception as exc:
                raise serializers.ValidationError({'lojista': str(exc)})

        if loja is not None:
            try:
                TransacaoService.validar_loja_ativa(loja)
            except Exception as exc:
                raise serializers.ValidationError({'loja': str(exc)})

        itens = attrs.get('itens')
        if self.instance is None and 'itens' in self.initial_data and not itens:
            raise serializers.ValidationError({
                'itens': 'Informe ao menos um item na transação.'
            })
        if itens is not None:
            produtos = [item['produto'].pk for item in itens]
            if len(produtos) != len(set(produtos)):
                raise serializers.ValidationError({
                    'itens': 'Não repita produtos; consolide a quantidade em um único item.'
                })
            for item in itens:
                produto = item['produto']
                if produto.lojista_id != lojista.id:
                    raise serializers.ValidationError({
                        'itens': f'O produto {produto.nome} não pertence ao lojista da transação.'
                    })

        return attrs

    def validate_valor(self, value):
        if value <= 0:
            raise serializers.ValidationError('O valor da transação deve ser maior que zero.')
        return value

    def create(self, validated_data):
        itens_data = validated_data.pop('itens', [])
        with transaction.atomic():
            lojista = validated_data['lojista']
            lojista = Lojista.objects.select_for_update().get(pk=lojista.pk)
            TransacaoService.validar_lojista_ativo(lojista)

            produtos = Produto.objects.select_for_update().filter(
                pk__in={item['produto'].pk for item in itens_data}
            ).order_by('pk')
            produtos_por_id = {produto.pk: produto for produto in produtos}

            for item_data in itens_data:
                produto_id = item_data['produto'].pk
                produto = produtos_por_id.get(produto_id)
                if produto is None:
                    raise serializers.ValidationError({
                        'itens': 'Um ou mais produtos não estão disponíveis.'
                    })
                if produto.lojista_id != lojista.id:
                    raise serializers.ValidationError({
                        'itens': 'Cada produto deve pertencer ao lojista da transação.'
                    })
                item_data['produto'] = produto

            TransacaoService.validar_valor_transacao(itens_data, validated_data['valor'])

            for item_data in itens_data:
                TransacaoService.debitar_estoque(item_data['produto'], item_data['quantidade'])

            transacao = Transacao.objects.create(**validated_data)
            for item_data in itens_data:
                produto = item_data['produto']
                quantidade = item_data['quantidade']
                ItemTransacao.objects.create(
                    transacao=transacao,
                    produto=produto,
                    quantidade=quantidade,
                    preco_unitario=produto.preco,
                )
            return transacao

    def update(self, instance, validated_data):
        with transaction.atomic():
            transacao = Transacao.objects.select_for_update().get(pk=instance.pk)
            return super().update(transacao, validated_data)

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
