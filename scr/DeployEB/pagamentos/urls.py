from django.http import JsonResponse
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import LojistaViewSet, TransacaoViewSet

app_name = 'pagamentos'


def api_root(_request):
    return JsonResponse({
        'status': 'sucesso',
        'mensagem': 'Bem-vindo à API do ZuumPay!',
        'endpoints': {
            'lojistas': '/api/lojistas/',
            'transacoes': '/api/transacoes/',
            'aprovar_transacao': '/api/transacoes/<id>/aprovar/',
            'cancelar_transacao': '/api/transacoes/<id>/cancelar/',
            'admin': '/admin/',
        },
    })


router = DefaultRouter()
router.register('lojistas', LojistaViewSet, basename='lojista')
router.register('transacoes', TransacaoViewSet, basename='transacao')

urlpatterns = [
    path('', api_root, name='api-root'),
    *router.urls,
]
