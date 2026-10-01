from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status as http_status

from .models import Lojista, Transacao
from .serializers import LojistaSerializer, TransacaoSerializer


class LojistaViewSet(viewsets.ModelViewSet):
    queryset = Lojista.objects.all().order_by('id')
    serializer_class = LojistaSerializer
    permission_classes = (IsAuthenticated,)


class TransacaoViewSet(viewsets.ModelViewSet):
    queryset = Transacao.objects.select_related('lojista').all().order_by('id')
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
