from decimal import Decimal

from django.core.management.base import BaseCommand

from pagamentos.models import Categoria, ItemTransacao, Loja, Lojista, Produto, Transacao


class Command(BaseCommand):
    help = 'Carrega dados de exemplo para a API ZuumPay.'

    def handle(self, *args, **options):
        lojista, _ = Lojista.objects.get_or_create(
            cnpj='12345678000199',
            defaults={
                'nome_fantasia': 'ZuumPay Market',
                'razao_social': 'ZuumPay Market Ltda',
                'email': 'contato@zuumpay.example',
            },
        )

        loja, _ = Loja.objects.get_or_create(
            lojista=lojista,
            nome='Loja Central',
            defaults={'cidade': 'São Paulo', 'ativo': True},
        )

        categorias = []
        for nome, descricao in [
            ('Eletrônicos', 'Produtos de tecnologia e acessórios.'),
            ('Casa', 'Itens para uso doméstico.'),
            ('Acessórios', 'Complementos e periféricos.'),
        ]:
            categoria, _ = Categoria.objects.get_or_create(nome=nome, defaults={'descricao': descricao})
            categorias.append(categoria)

        produto, _ = Produto.objects.get_or_create(
            lojista=lojista,
            nome='Kit de Monitoramento',
            defaults={
                'descricao': 'Kit com câmera, sensor e sincronização via app.',
                'preco': Decimal('899.90'),
                'estoque': 12,
                'atributos': {'cor': 'preto', 'material': 'alumínio', 'garantia': '12 meses'},
            },
        )
        produto.categorias.set(categorias)

        transacao, _ = Transacao.objects.get_or_create(
            lojista=lojista,
            loja=loja,
            valor=Decimal('899.90'),
            chave_pix='pix@zuumpay.example',
            defaults={'status': Transacao.STATUS_PENDENTE, 'observacoes': 'Pedido de demonstração'},
        )

        ItemTransacao.objects.get_or_create(
            transacao=transacao,
            produto=produto,
            defaults={'quantidade': 1, 'preco_unitario': produto.preco},
        )

        self.stdout.write(self.style.SUCCESS('Dados de exemplo carregados com sucesso.'))
