from django.urls import path
from django.http import JsonResponse

# Uma vista simples de teste para a API
def api_root(request):
    return JsonResponse({
        "status": "sucesso",
        "mensagem": "Bem-vindo à API do ZuumPay!",
        "endpoints": {
            "admin": "/admin/",
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
]