import json

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import connection, transaction
from django.utils import timezone
from rest_framework import status as http_status
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Categoria, ItemTransacao, Loja, Lojista, Produto, Transacao
from .serializers import (
    CategoriaSerializer,
    ItemTransacaoSerializer,
    LojaSerializer,
    LojistaSerializer,
    ProdutoSerializer,
    TransacaoSerializer,
)


class LojistaViewSet(viewsets.ModelViewSet):
    queryset = Lojista.objects.all().order_by('id')
    serializer_class = LojistaSerializer
    permission_classes = (IsAuthenticated,)


class LojaViewSet(viewsets.ModelViewSet):
    queryset = Loja.objects.select_related('lojista').all().order_by('id')
    serializer_class = LojaSerializer
    permission_classes = (IsAuthenticated,)


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all().order_by('id')
    serializer_class = CategoriaSerializer
    permission_classes = (IsAuthenticated,)


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.select_related('lojista').prefetch_related('categorias').all().order_by('id')
    serializer_class = ProdutoSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        chave = self.request.query_params.get('atributos__chave')
        valor = self.request.query_params.get('atributos__valor')

        if 'lojista' in self.request.query_params:
            queryset = queryset.filter(lojista_id=self.request.query_params['lojista'])

        if not chave:
            return queryset

        if valor is None:
            if connection.vendor == 'postgresql':
                return queryset.filter(atributos__has_key=chave)
            return queryset.filter(**{f'atributos__{chave}__isnull': False})

        try:
            valor_json = json.loads(valor)
        except json.JSONDecodeError:
            valor_json = valor

        if connection.vendor == 'postgresql':
            return queryset.filter(atributos__contains={chave: valor_json})

        return queryset.filter(**{f'atributos__{chave}': valor_json})


class ItemTransacaoViewSet(viewsets.ModelViewSet):
    queryset = ItemTransacao.objects.select_related('transacao', 'produto').all().order_by('id')
    serializer_class = ItemTransacaoSerializer
    permission_classes = (IsAuthenticated,)


class TransacaoViewSet(viewsets.ModelViewSet):
    queryset = Transacao.objects.select_related('lojista', 'loja').all().order_by('id')
    serializer_class = TransacaoSerializer
    permission_classes = (IsAuthenticated,)

    def _finalizar_transacao(self, status_final):
        transacao_id = self.get_object().pk
        with transaction.atomic():
            transacao = Transacao.objects.select_for_update().get(pk=transacao_id)
            try:
                transacao.validar_transicao(status_final)
            except (DjangoValidationError, ValidationError) as exc:
                return Response({'detail': str(exc)}, status=http_status.HTTP_409_CONFLICT)

            if status_final in {Transacao.STATUS_CANCELADO, Transacao.STATUS_ESTORNADO}:
                quantidades = {}
                for item in transacao.itens.select_related('produto').all():
                    quantidades[item.produto_id] = (
                        quantidades.get(item.produto_id, 0) + item.quantidade
                    )

                produtos = Produto.objects.select_for_update().filter(pk__in=quantidades).order_by('pk')
                for produto in produtos:
                    produto.estoque += quantidades[produto.pk]
                    if isinstance(produto.atributos, dict) and 'estoque' in produto.atributos:
                        estoque = produto.atributos['estoque']
                        if type(estoque) is not int or estoque < 0:
                            raise ValidationError({
                                'itens': f'O estoque do produto {produto.nome} está inválido.'
                            })
                        produto.atributos['estoque'] = estoque + quantidades[produto.pk]
                    produto.save(update_fields=('estoque', 'atributos', 'atualizado_em'))

            transacao.status = status_final
            transacao.finalizado_em = timezone.now()
            transacao.save(update_fields=('status', 'finalizado_em'))

        return Response(self.get_serializer(transacao).data)

    @action(detail=True, methods=('post',))
    def aprovar(self, request, pk=None):
        return self._finalizar_transacao(Transacao.STATUS_PAGO)

    @action(detail=True, methods=('post',))
    def cancelar(self, request, pk=None):
        return self._finalizar_transacao(Transacao.STATUS_CANCELADO)

    @action(detail=True, methods=('post',))
    def estornar(self, request, pk=None):
        return self._finalizar_transacao(Transacao.STATUS_ESTORNADO)

    @action(detail=True, methods=('post',))
    def falhar(self, request, pk=None):
        return self._finalizar_transacao(Transacao.STATUS_FALHADO)
