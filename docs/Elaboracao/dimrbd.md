# Modelo Relacional do Banco de Dados — ZuumPay

## 1. Diagrama de entidades e relacionamentos

O desenho abaixo reflete os models Django. As cardinalidades representam os relacionamentos persistidos; `loja` é opcional em uma transação e pode ser definida como nula quando a loja é removida.

```mermaid
erDiagram
    LOJISTA ||--o{ LOJA : possui
    LOJISTA ||--o{ PRODUTO : cadastra
    LOJISTA ||--o{ TRANSACAO : recebe
    LOJA o|--o{ TRANSACAO : identifica
    PRODUTO }o--o{ CATEGORIA : classifica
    TRANSACAO ||--o{ ITEM_TRANSACAO : contem
    PRODUTO ||--o{ ITEM_TRANSACAO : referencia

    LOJISTA {
        int id PK
        string nome_fantasia
        string razao_social
        string cnpj UK
        string email UK
        datetime criado_em
    }
    LOJA {
        int id PK
        int lojista_id FK
        string nome
        string cidade
        boolean ativo
        datetime criado_em
    }
    CATEGORIA {
        int id PK
        string nome UK
        text descricao
    }
    PRODUTO {
        int id PK
        int lojista_id FK
        string nome
        text descricao
        decimal preco
        int estoque
        json atributos
        datetime criado_em
        datetime atualizado_em
    }
    TRANSACAO {
        int id PK
        int lojista_id FK
        int loja_id FK "opcional, SET_NULL"
        decimal valor
        string chave_pix
        string status
        text observacoes
        datetime criado_em
        datetime finalizado_em "opcional"
    }
    ITEM_TRANSACAO {
        int id PK
        int transacao_id FK
        int produto_id FK
        int quantidade
        decimal preco_unitario
    }
```

## 2. Regras e integridade

| Entidade/regra | Implementação |
|---|---|
| Lojista | CNPJ e e-mail únicos |
| Loja | FK obrigatória para lojista; remoção do lojista remove suas lojas (`CASCADE`) |
| Categoria | Nome único; relacionamento muitos-para-muitos com produtos |
| Produto | FK para lojista; `atributos` é objeto JSON; preço positivo e estoque não negativo |
| Índice de atributos | `GinIndex` em `Produto.atributos`, usado para consultas de containment no PostgreSQL |
| Transação | FK obrigatória para lojista; FK opcional de loja com `SET_NULL`; valor positivo |
| Item de transação | FKs para transação e produto; quantidade e preço unitário positivos; produto protegido contra remoção (`PROTECT`) |
| Consistência dos itens | Serializer exige que os produtos sejam do lojista da transação e, havendo itens, que a soma coincida com o valor; gravação ocorre em `transaction.atomic()` |
| Status da transação | `PENDENTE`, `PAGO` ou `CANCELADO`; apenas pendentes podem ser finalizadas pela ação correspondente |

O saldo/estoque não é debitado pelo fluxo de transação atual. O domínio representa uma simulação de pagamentos e não efetua processamento financeiro real.

## 3. Migrações e armazenamento

As entidades são definidas em `scr/DeployEB/pagamentos/models.py`; a estrutura evolui pelas migrações em `scr/DeployEB/pagamentos/migrations/`. Em PostgreSQL, o `JSONField` usa o armazenamento JSONB do backend e o índice GIN é criado pela migração correspondente. No ambiente Compose, os arquivos do banco ficam no volume nomeado `postgres_data`; remover esse volume pode apagar os dados.

## 4. Histórico e aprovação

Versão 1.0, preparada em 2026-11-13; aprovação do orientador/avaliador pendente. Consulte o [histórico consolidado](index.md#historico-de-versoes-e-aprovacoes).
