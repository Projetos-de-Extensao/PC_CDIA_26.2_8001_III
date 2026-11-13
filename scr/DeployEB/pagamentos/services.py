from decimal import Decimal

from rest_framework.exceptions import ValidationError


class TransacaoService:
    @staticmethod
    def validar_lojista_ativo(lojista):
        if lojista is None:
            return
        if lojista.status_conta != lojista.STATUS_ATIVO:
            raise ValidationError('Só é possível criar transações para lojistas com conta ativa.')

    @staticmethod
    def validar_loja_ativa(loja):
        if loja is not None and not loja.ativo:
            raise ValidationError('A loja informada está inativa.')

    @staticmethod
    def obter_estoque_disponivel(produto):
        estoque_modelo = int(produto.estoque)
        atributos = produto.atributos if isinstance(produto.atributos, dict) else {}
        estoque_json = atributos.get('estoque')
        if isinstance(estoque_json, int):
            return min(estoque_modelo, estoque_json)
        return estoque_modelo

    @staticmethod
    def debitar_estoque(produto, quantidade):
        estoque_disponivel = TransacaoService.obter_estoque_disponivel(produto)
        if estoque_disponivel < quantidade:
            raise ValidationError(f'Estoque insuficiente para o produto {produto.nome}.')

        produto.estoque = max(0, produto.estoque - quantidade)
        atributos = produto.atributos if isinstance(produto.atributos, dict) else {}
        if 'estoque' in atributos:
            estoque_json = atributos['estoque']
            if type(estoque_json) is not int or estoque_json < 0:
                raise ValidationError(f'O estoque do produto {produto.nome} está em formato inválido.')
            atributos['estoque'] = max(0, estoque_json - quantidade)
            produto.atributos = atributos

        produto.save(update_fields=('estoque', 'atributos', 'atualizado_em'))

    @staticmethod
    def repor_estoque(produto, quantidade):
        produto.estoque += quantidade
        atributos = produto.atributos if isinstance(produto.atributos, dict) else {}
        if 'estoque' in atributos:
            estoque_json = atributos['estoque']
            if type(estoque_json) is not int or estoque_json < 0:
                raise ValidationError(f'O estoque do produto {produto.nome} está inválido.')
            atributos['estoque'] = estoque_json + quantidade
            produto.atributos = atributos
        produto.save(update_fields=('estoque', 'atributos', 'atualizado_em'))

    @staticmethod
    def validar_valor_transacao(itens_data, valor_transacao):
        if not itens_data:
            return

        total_itens = Decimal('0.00')
        for item in itens_data:
            total_itens += Decimal(item['quantidade']) * item['produto'].preco
        if valor_transacao != total_itens:
            raise ValidationError('O valor da transação deve coincidir com a soma dos itens.')
