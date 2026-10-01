from rest_framework import serializers

from .models import Lojista, Transacao


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


class TransacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transacao
        fields = (
            'id',
            'lojista',
            'valor',
            'chave_pix',
            'status',
            'criado_em',
        )
        read_only_fields = ('id', 'criado_em')
