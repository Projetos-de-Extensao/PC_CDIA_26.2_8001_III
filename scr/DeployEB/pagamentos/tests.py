from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APIRequestFactory

from .models import Categoria, ItemTransacao, Loja, Lojista, Produto, Transacao
from .views import ProdutoViewSet


class PagamentosApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            username='api-test-user',
            email='admin@example.com',
            password='local-test-password',
        )
        self.lojista = Lojista.objects.create(
            nome_fantasia='Loja de Teste',
            razao_social='Loja de Teste LTDA',
            cnpj='12345678000199',
            email='loja@example.com',
        )

    def test_api_requires_authentication(self):
        response = self.client.get(reverse('pagamentos:lojista-list'))

        self.assertEqual(response.status_code, 401)

    def test_api_root_lists_available_endpoints(self):
        response = self.client.get(reverse('pagamentos:api-root'))
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'sucesso')
        self.assertIn('lojistas', data['endpoints'])
        self.assertIn('transacoes', data['endpoints'])
        self.assertIn('catalogo', data['endpoints'])
        self.assertIn('aprovar_transacao', data['endpoints'])
        self.assertIn('cancelar_transacao', data['endpoints'])

    def test_authenticated_user_can_list_and_create_lojistas(self):
        self.client.force_authenticate(user=self.user)

        list_response = self.client.get(reverse('pagamentos:lojista-list'))
        create_response = self.client.post(
            reverse('pagamentos:lojista-list'),
            {
                'nome_fantasia': 'Nova Loja',
                'razao_social': 'Nova Loja LTDA',
                'cnpj': '98765432000199',
                'email': 'nova@example.com',
            },
            format='json',
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data['count'], 1)
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(Lojista.objects.count(), 2)

    def test_superuser_can_access_admin(self):
        self.assertTrue(
            self.client.login(
                username='api-test-user',
                password='local-test-password',
            )
        )

        response = self.client.get(reverse('admin:index'))

        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_can_read_update_and_delete_lojista(self):
        self.client.force_authenticate(user=self.user)
        detail_url = reverse(
            'pagamentos:lojista-detail',
            kwargs={'pk': self.lojista.pk},
        )

        read_response = self.client.get(detail_url)
        update_response = self.client.patch(
            detail_url,
            {'nome_fantasia': 'Loja Atualizada'},
            format='json',
        )
        delete_response = self.client.delete(detail_url)

        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(Lojista.objects.filter(pk=self.lojista.pk).exists())

    def test_authenticated_user_can_create_transacao_for_lojista(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('pagamentos:transacao-list'),
            {
                'lojista': self.lojista.pk,
                'valor': '25.50',
                'chave_pix': 'pix-teste@example.com',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        transacao = Transacao.objects.get()
        self.assertEqual(transacao.lojista, self.lojista)
        self.assertEqual(transacao.valor, Decimal('25.50'))
        self.assertEqual(transacao.status, Transacao.STATUS_PENDENTE)
        self.assertIsNone(transacao.finalizado_em)

        detail_url = reverse(
            'pagamentos:transacao-detail',
            kwargs={'pk': transacao.pk},
        )
        self.assertEqual(self.client.get(detail_url).status_code, 200)
        update_response = self.client.patch(
            detail_url,
            {'valor': '30.00'},
            format='json',
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(
            Transacao.objects.get(pk=transacao.pk).status,
            Transacao.STATUS_PENDENTE,
        )
        self.assertEqual(self.client.delete(detail_url).status_code, 204)
        self.assertFalse(Transacao.objects.exists())

    def test_transacao_status_changes_only_through_approval_or_cancellation(self):
        self.client.force_authenticate(user=self.user)
        transacao = Transacao.objects.create(
            lojista=self.lojista,
            valor=Decimal('25.50'),
            chave_pix='pix-teste@example.com',
        )
        detail_url = reverse(
            'pagamentos:transacao-detail',
            kwargs={'pk': transacao.pk},
        )

        direct_update = self.client.patch(
            detail_url,
            {'status': Transacao.STATUS_PAGO},
            format='json',
        )
        approval = self.client.post(f'{detail_url}aprovar/')
        second_action = self.client.post(f'{detail_url}cancelar/')

        self.assertEqual(direct_update.status_code, 400)
        self.assertEqual(approval.status_code, 200)
        self.assertEqual(approval.data['status'], Transacao.STATUS_PAGO)
        self.assertIsNotNone(approval.data['finalizado_em'])
        self.assertEqual(second_action.status_code, 409)
        transacao.refresh_from_db()
        self.assertEqual(transacao.status, Transacao.STATUS_PAGO)

    def test_pending_transacao_can_be_cancelled(self):
        self.client.force_authenticate(user=self.user)
        transacao = Transacao.objects.create(
            lojista=self.lojista,
            valor=Decimal('25.50'),
            chave_pix='pix-teste@example.com',
        )
        detail_url = reverse(
            'pagamentos:transacao-detail',
            kwargs={'pk': transacao.pk},
        )

        response = self.client.post(f'{detail_url}cancelar/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], Transacao.STATUS_CANCELADO)
        self.assertIsNotNone(response.data['finalizado_em'])

    def test_cancelled_transacao_cannot_be_approved(self):
        self.client.force_authenticate(user=self.user)
        transacao = Transacao.objects.create(
            lojista=self.lojista,
            valor=Decimal('25.50'),
            chave_pix='pix-teste@example.com',
            status=Transacao.STATUS_CANCELADO,
        )

        response = self.client.post(
            reverse('pagamentos:transacao-aprovar', kwargs={'pk': transacao.pk})
        )

        self.assertEqual(response.status_code, 409)
        transacao.refresh_from_db()
        self.assertEqual(transacao.status, Transacao.STATUS_CANCELADO)

    def test_transacao_rejects_non_positive_values(self):
        self.client.force_authenticate(user=self.user)

        for value in ('0', '-1.00'):
            with self.subTest(value=value):
                response = self.client.post(
                    reverse('pagamentos:transacao-list'),
                    {
                        'lojista': self.lojista.pk,
                        'valor': value,
                        'chave_pix': 'pix-teste@example.com',
                    },
                    format='json',
                )
                self.assertEqual(response.status_code, 400)

        self.assertFalse(Transacao.objects.exists())

    def test_transacao_rejects_unknown_lojista(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('pagamentos:transacao-list'),
            {
                'lojista': 9999,
                'valor': '25.50',
                'chave_pix': 'pix-teste@example.com',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Transacao.objects.exists())

    def test_product_json_attribute_filter_works(self):
        self.client.force_authenticate(user=self.user)
        categoria = Categoria.objects.create(nome='Smart Home', descricao='Casa inteligente')
        produto = Produto.objects.create(
            lojista=self.lojista,
            nome='Sensor de Presença',
            descricao='Sensor inteligente',
            preco=Decimal('60.00'),
            estoque=7,
            atributos={'cor': 'branco', 'tipo': 'sensor', 'wifi': True},
        )
        produto.categorias.add(categoria)

        response = self.client.get(
            reverse('pagamentos:produto-list'),
            {'atributos__chave': 'tipo', 'atributos__valor': 'sensor'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], produto.id)

    def test_catalogo_endpoint_lists_products(self):
        self.client.force_authenticate(user=self.user)
        produto = Produto.objects.create(
            lojista=self.lojista,
            nome='Produto de Catálogo',
            preco=Decimal('12.50'),
            atributos={'tipo': 'demo'},
        )

        response = self.client.get(reverse('pagamentos:catalogo-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], produto.id)

    def test_postgres_json_filter_uses_indexable_containment_query(self):
        view = ProdutoViewSet()
        request = APIRequestFactory().get(
            '/api/produtos/',
            {'atributos__chave': 'tipo', 'atributos__valor': 'sensor'},
        )
        view.action_map = {'get': 'list'}
        view.request = view.initialize_request(request)

        with patch('pagamentos.views.connection.vendor', 'postgresql'):
            queryset = view.get_queryset()

        self.assertIsInstance(queryset, QuerySet)
        lookup = queryset.query.where.children[-1]
        self.assertEqual(lookup.lookup_name, 'contains')
        self.assertEqual(lookup.rhs, {'tipo': 'sensor'})

    def test_transaction_atomic_rollback_on_invalid_items(self):
        self.client.force_authenticate(user=self.user)
        categoria = Categoria.objects.create(nome='Tecnologia', descricao='Eletrônicos')
        produto = Produto.objects.create(
            lojista=self.lojista,
            nome='Câmera',
            descricao='Câmera de segurança',
            preco=Decimal('250.00'),
            estoque=5,
            atributos={'marca': 'Zuum'},
        )
        produto.categorias.add(categoria)

        response = self.client.post(
            reverse('pagamentos:transacao-list'),
            {
                'lojista': self.lojista.pk,
                'valor': '300.00',
                'chave_pix': 'pix-demo@example.com',
                'itens': [
                    {'produto': produto.pk, 'quantidade': 1},
                ],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Transacao.objects.exists())

    def test_transaction_rejects_products_from_another_lojista(self):
        self.client.force_authenticate(user=self.user)
        outro_lojista = Lojista.objects.create(
            nome_fantasia='Outro Lojista',
            razao_social='Outro Lojista LTDA',
            cnpj='11111111000199',
            email='outro@example.com',
        )
        produto = Produto.objects.create(
            lojista=outro_lojista,
            nome='Produto externo',
            preco=Decimal('10.00'),
            estoque=1,
        )

        response = self.client.post(
            reverse('pagamentos:transacao-list'),
            {
                'lojista': self.lojista.pk,
                'valor': '10.00',
                'chave_pix': 'pix-teste@example.com',
                'itens': [{'produto': produto.pk, 'quantidade': 1}],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Transacao.objects.exists())

    def test_transaction_rejects_duplicate_and_explicitly_empty_items(self):
        self.client.force_authenticate(user=self.user)
        produto = Produto.objects.create(
            lojista=self.lojista,
            nome='Produto de teste',
            preco=Decimal('10.00'),
            estoque=3,
        )
        base_payload = {
            'lojista': self.lojista.pk,
            'valor': '20.00',
            'chave_pix': 'pix-teste@example.com',
        }

        for itens in (
            [
                {'produto': produto.pk, 'quantidade': 1},
                {'produto': produto.pk, 'quantidade': 1},
            ],
            [],
        ):
            with self.subTest(itens=itens):
                response = self.client.post(
                    reverse('pagamentos:transacao-list'),
                    {**base_payload, 'itens': itens},
                    format='json',
                )
                self.assertEqual(response.status_code, 400)

        self.assertFalse(Transacao.objects.exists())
        self.assertFalse(ItemTransacao.objects.exists())

    def test_transaction_decrements_and_restores_optional_attribute_stock(self):
        self.client.force_authenticate(user=self.user)
        produto = Produto.objects.create(
            lojista=self.lojista,
            nome='Produto com estoque JSON',
            preco=Decimal('10.00'),
            estoque=99,
            atributos={'estoque': 4},
        )
        payload = {
            'lojista': self.lojista.pk,
            'valor': '20.00',
            'chave_pix': 'pix-teste@example.com',
            'itens': [{
                'produto': produto.pk,
                'quantidade': 2,
                'preco_unitario': '0.01',
            }],
        }

        created = self.client.post(
            reverse('pagamentos:transacao-list'), payload, format='json'
        )

        self.assertEqual(created.status_code, 201)
        item = ItemTransacao.objects.get(transacao_id=created.data['id'])
        self.assertEqual(item.preco_unitario, Decimal('10.00'))
        produto.refresh_from_db()
        self.assertEqual(produto.atributos['estoque'], 2)

        cancelled = self.client.post(
            reverse(
                'pagamentos:transacao-cancelar',
                kwargs={'pk': created.data['id']},
            )
        )

        self.assertEqual(cancelled.status_code, 200)
        produto.refresh_from_db()
        self.assertEqual(produto.atributos['estoque'], 4)

    def test_transaction_rejects_insufficient_attribute_stock_atomically(self):
        self.client.force_authenticate(user=self.user)
        produto = Produto.objects.create(
            lojista=self.lojista,
            nome='Produto sem saldo',
            preco=Decimal('10.00'),
            estoque=99,
            atributos={'estoque': 1},
        )

        response = self.client.post(
            reverse('pagamentos:transacao-list'),
            {
                'lojista': self.lojista.pk,
                'valor': '20.00',
                'chave_pix': 'pix-teste@example.com',
                'itens': [{'produto': produto.pk, 'quantidade': 2}],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Transacao.objects.exists())
        produto.refresh_from_db()
        self.assertEqual(produto.atributos['estoque'], 1)

    def test_product_attributes_require_object_and_nonnegative_integer_stock(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            'lojista': self.lojista.pk,
            'nome': 'Produto JSON inválido',
            'preco': '10.00',
        }

        for atributos in (['lista'], 'texto', {'estoque': -1}, {'estoque': 1.5}):
            with self.subTest(atributos=atributos):
                response = self.client.post(
                    reverse('pagamentos:produto-list'),
                    {**payload, 'atributos': atributos},
                    format='json',
                )
                self.assertEqual(response.status_code, 400)
