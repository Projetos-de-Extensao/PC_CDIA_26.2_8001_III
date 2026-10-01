from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Lojista, Transacao


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
                'status': 'PENDENTE',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        transacao = Transacao.objects.get()
        self.assertEqual(transacao.lojista, self.lojista)
        self.assertEqual(transacao.valor, Decimal('25.50'))

        detail_url = reverse(
            'pagamentos:transacao-detail',
            kwargs={'pk': transacao.pk},
        )
        self.assertEqual(self.client.get(detail_url).status_code, 200)
        update_response = self.client.patch(
            detail_url,
            {'status': 'PAGO'},
            format='json',
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(
            Transacao.objects.get(pk=transacao.pk).status,
            'PAGO',
        )
        self.assertEqual(self.client.delete(detail_url).status_code, 204)
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
