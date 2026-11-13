import json

from django.db import connection
from django.utils import timezone
from rest_framework import status as http_status
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
        transacao = self.get_object()
        atualizada = Transacao.objects.filter(
            pk=transacao.pk,
            status=Transacao.STATUS_PENDENTE,
        ).update(status=status_final, finalizado_em=timezone.now())

        if not atualizada:
            return Response(
                {'detail': 'Somente transações pendentes podem ser finalizadas.'},
                status=http_status.HTTP_409_CONFLICT,
            )

        transacao.refresh_from_db(fields=('status', 'finalizado_em'))
        return Response(self.get_serializer(transacao).data)

    @action(detail=True, methods=('post',))
    def aprovar(self, request, pk=None):
        return self._finalizar_transacao(Transacao.STATUS_PAGO)

    @action(detail=True, methods=('post',))
    def cancelar(self, request, pk=None):
        return self._finalizar_transacao(Transacao.STATUS_CANCELADO)
