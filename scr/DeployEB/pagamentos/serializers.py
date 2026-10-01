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
    def validate(self, attrs):
        if 'status' in self.initial_data:
            raise serializers.ValidationError({
                'status': 'Use as ações aprovar ou cancelar para alterar o status.'
            })
        return attrs

    def validate_valor(self, value):
        if value <= 0:
            raise serializers.ValidationError('O valor da transação deve ser maior que zero.')
        return value

    class Meta:
        model = Transacao
        fields = (
            'id',
            'lojista',
            'valor',
            'chave_pix',
            'status',
            'criado_em',
            'finalizado_em',
        )
        read_only_fields = ('id', 'status', 'criado_em', 'finalizado_em')
