from django.db import models

class Lojista(models.Model):
    nome_fantasia = models.CharField(max_length=150, verbose_name="Nome Fantasia")
    razao_social = models.CharField(max_length=150, verbose_name="Razão Social")
    cnpj = models.CharField(max_length=14, unique=True, verbose_name="CNPJ")
    email = models.EmailField(unique=True, verbose_name="E-mail de Contato")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")

    def __str__(self):
        return f"{self.nome_fantasia} ({self.cnpj})"

    class Meta:
        verbose_name = "Lojista"
        verbose_name_plural = "Lojistas"


class Transacao(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago / Aprovado'),
        ('CANCELADO', 'Cancelado'),
    ]

    lojista = models.ForeignKey(Lojista, on_delete=models.CASCADE, related_name='transacoes', verbose_name="Lojista")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor (R$)")
    chave_pix = models.CharField(max_length=255, verbose_name="Chave Pix de Destino")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE', verbose_name="Status da Transação")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora")

    def __str__(self):
        return f"Transação R$ {self.valor} - {self.status} ({self.lojista.nome_fantasia})"

    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"