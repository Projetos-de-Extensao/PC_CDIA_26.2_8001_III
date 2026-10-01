from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

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
