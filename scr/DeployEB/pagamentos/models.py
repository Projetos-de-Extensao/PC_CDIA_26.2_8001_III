from decimal import Decimal

from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Lojista(models.Model):
    STATUS_ATIVO = 'ATIVO'
    STATUS_PENDENTE_APROVACAO = 'PENDENTE_APROVACAO'
    STATUS_SUSPENSO = 'SUSPENSO'

    STATUS_CHOICES = [
        (STATUS_ATIVO, 'Ativo'),
        (STATUS_PENDENTE_APROVACAO, 'Pendente de aprovação'),
        (STATUS_SUSPENSO, 'Suspenso'),
    ]

    nome_fantasia = models.CharField(max_length=150, verbose_name="Nome Fantasia")
    razao_social = models.CharField(max_length=150, verbose_name="Razão Social")
    cnpj = models.CharField(max_length=14, unique=True, verbose_name="CNPJ")
    email = models.EmailField(unique=True, verbose_name="E-mail de Contato")
    status_conta = models.CharField(
        max_length=24,
        choices=STATUS_CHOICES,
        default=STATUS_ATIVO,
        verbose_name="Status da conta",
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")

    @property
    def ativo(self):
        return self.status_conta == self.STATUS_ATIVO

    def __str__(self):
        return f"{self.nome_fantasia} ({self.cnpj})"

    class Meta:
        verbose_name = "Lojista"
        verbose_name_plural = "Lojistas"


class Loja(models.Model):
    lojista = models.ForeignKey(
        Lojista,
        on_delete=models.CASCADE,
        related_name='lojas',
        verbose_name="Lojista",
    )
    nome = models.CharField(max_length=150, verbose_name="Nome da Loja")
    cidade = models.CharField(max_length=100, default='São Paulo', verbose_name="Cidade")
    ativo = models.BooleanField(default=True, verbose_name="Loja ativa")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")

    def __str__(self):
        return f"{self.nome} ({self.lojista.nome_fantasia})"

    class Meta:
        verbose_name = "Loja"
        verbose_name_plural = "Lojas"
        ordering = ['nome']


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Categoria")
    descricao = models.TextField(blank=True, default='', verbose_name="Descrição")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nome']


class Produto(models.Model):
    lojista = models.ForeignKey(
        Lojista,
        on_delete=models.CASCADE,
        related_name='produtos',
        verbose_name="Lojista",
    )
    nome = models.CharField(max_length=150, verbose_name="Nome do Produto")
    descricao = models.TextField(blank=True, default='', verbose_name="Descrição")
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço")
    estoque = models.PositiveIntegerField(default=0, verbose_name="Estoque")
    atributos = models.JSONField(default=dict, blank=True, verbose_name="Atributos do produto")
    categorias = models.ManyToManyField(Categoria, blank=True, related_name='produtos')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    def __str__(self):
        return f"{self.nome} - {self.lojista.nome_fantasia}"

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['-criado_em']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(preco__gt=0),
                name='produto_preco_positivo',
            ),
            models.CheckConstraint(
                condition=models.Q(estoque__gte=0),
                name='produto_estoque_nao_negativo',
            ),
        ]
        indexes = [
            GinIndex(fields=['atributos'], name='produto_atributos_gin'),
        ]


class ItemCatalogo(Produto):
    class Meta:
        proxy = True
        verbose_name = "Item do Catálogo"
        verbose_name_plural = "Itens do Catálogo"
        ordering = ['-criado_em']


class Transacao(models.Model):
    STATUS_PENDENTE = 'PENDENTE'
    STATUS_EM_ANALISE = 'EM_ANALISE'
    STATUS_PAGO = 'PAGO'
    STATUS_CANCELADO = 'CANCELADO'
    STATUS_ESTORNADO = 'ESTORNADO'
    STATUS_FALHADO = 'FALHADO'

    STATUS_CHOICES = [
        (STATUS_PENDENTE, 'Pendente'),
        (STATUS_EM_ANALISE, 'Em análise'),
        (STATUS_PAGO, 'Pago / Aprovado'),
        (STATUS_CANCELADO, 'Cancelado'),
        (STATUS_ESTORNADO, 'Estornado'),
        (STATUS_FALHADO, 'Falhado'),
    ]

    lojista = models.ForeignKey(
        Lojista,
        on_delete=models.CASCADE,
        related_name='transacoes',
        verbose_name="Lojista",
    )
    loja = models.ForeignKey(
        Loja,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transacoes',
        verbose_name="Loja",
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor (R$)")
    chave_pix = models.CharField(max_length=255, verbose_name="Chave Pix de Destino")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDENTE,
        verbose_name="Status da Transação",
    )
    observacoes = models.TextField(blank=True, default='', verbose_name="Observações")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora")
    finalizado_em = models.DateTimeField(null=True, blank=True, verbose_name="Data/Hora de Finalização")

    def validar_transicao(self, novo_status):
        transicoes_validas = {
            self.STATUS_PENDENTE: {self.STATUS_EM_ANALISE, self.STATUS_PAGO, self.STATUS_CANCELADO, self.STATUS_FALHADO},
            self.STATUS_EM_ANALISE: {self.STATUS_PAGO, self.STATUS_CANCELADO, self.STATUS_FALHADO},
            self.STATUS_PAGO: {self.STATUS_ESTORNADO},
            self.STATUS_CANCELADO: set(),
            self.STATUS_ESTORNADO: set(),
            self.STATUS_FALHADO: set(),
        }

        if novo_status not in transicoes_validas.get(self.status, set()):
            raise ValidationError(
                f"Transição inválida de status: {self.status} -> {novo_status}."
            )

    def registrar_status(self, novo_status, motivo=''):
        status_anterior = self.status
        self.validar_transicao(novo_status)
        self.status = novo_status
        if novo_status in {self.STATUS_CANCELADO, self.STATUS_ESTORNADO, self.STATUS_FALHADO, self.STATUS_PAGO}:
            self.finalizado_em = timezone.now()
        self.save(update_fields=('status', 'finalizado_em'))
        TransacaoStatusHistorico.objects.create(
            transacao=self,
            status_anterior=status_anterior,
            status_novo=novo_status,
            motivo=motivo,
        )

    def __str__(self):
        return f"Transação R$ {self.valor} - {self.status} ({self.lojista.nome_fantasia})"

    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(valor__gt=0),
                name='transacao_valor_positivo',
            ),
        ]


class TransacaoStatusHistorico(models.Model):
    transacao = models.ForeignKey(
        Transacao,
        on_delete=models.CASCADE,
        related_name='historico_status',
        verbose_name='Transação',
    )
    status_anterior = models.CharField(
        max_length=20,
        choices=Transacao.STATUS_CHOICES,
        verbose_name='Status anterior',
    )
    status_novo = models.CharField(
        max_length=20,
        choices=Transacao.STATUS_CHOICES,
        verbose_name='Status novo',
    )
    motivo = models.CharField(max_length=255, blank=True, default='', verbose_name='Motivo')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Data/Hora do evento')

    def __str__(self):
        return f'{self.transacao_id}: {self.status_anterior} -> {self.status_novo}'

    class Meta:
        verbose_name = 'Histórico de status da transação'
        verbose_name_plural = 'Históricos de status da transação'
        ordering = ['-criado_em']


class ItemTransacao(models.Model):
    transacao = models.ForeignKey(
        Transacao,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name="Transação",
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='itens_transacao',
        verbose_name="Produto",
    )
    quantidade = models.PositiveIntegerField(default=1, verbose_name="Quantidade")
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário")

    @property
    def total(self):
        return Decimal(str(self.quantidade)) * self.preco_unitario

    def __str__(self):
        return f"{self.produto.nome} x {self.quantidade}"

    class Meta:
        verbose_name = "Item da Transação"
        verbose_name_plural = "Itens da Transação"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantidade__gt=0),
                name='item_quantidade_positiva',
            ),
            models.CheckConstraint(
                condition=models.Q(preco_unitario__gt=0),
                name='item_preco_unitario_positivo',
            ),
        ]