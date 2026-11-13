# Sequência de Comunicação — ZuumPay

## 1. Criar uma transação com itens

Fluxo baseado em `TransacaoViewSet`, `TransacaoSerializer.create()` e `ItemTransacao`. Quando a validação de domínio falha após a criação provisória, a transação atômica desfaz a transação e os itens.

```mermaid
sequenceDiagram
    actor Cliente
    participant API as Django REST / ViewSet
    participant Serializer as TransacaoSerializer
    participant DB as PostgreSQL

    Cliente->>API: POST /api/transacoes/ (credenciais + JSON)
    API->>API: Verifica autenticação
    API->>Serializer: Valida payload
    Serializer->>DB: BEGIN (transaction.atomic)
    Serializer->>DB: INSERT Transacao (status PENDENTE)
    loop para cada item informado
        Serializer->>DB: Confere produto e lojista
        Serializer->>DB: INSERT ItemTransacao com preço atual
    end
    Serializer->>Serializer: Confere soma dos itens = valor
    alt payload válido
        Serializer->>DB: COMMIT
        API-->>Cliente: 201 Created + transação
    else divergência ou regra inválida
        Serializer->>DB: ROLLBACK
        API-->>Cliente: 400 Bad Request
    end
```

Sem itens, a transação pode ser criada apenas com os dados do lojista/valor; nesse caso, a comparação com a soma dos itens não é aplicada.

## 2. Aprovar ou cancelar

O endpoint de ação realiza atualização condicional no banco: somente uma linha ainda pendente pode mudar de estado. Isso evita que uma segunda requisição finalize novamente a mesma transação.

```mermaid
sequenceDiagram
    actor Operador as Usuário autenticado
    participant API as TransacaoViewSet
    participant DB as PostgreSQL

    Operador->>API: POST /api/transacoes/{id}/aprovar/ ou /cancelar/
    API->>API: Verifica autenticação e localiza transação
    API->>DB: UPDATE ... WHERE id = ? AND status = PENDENTE
    alt uma linha atualizada
        DB-->>API: Atualizada
        API->>DB: Lê status e finalizado_em
        API-->>Operador: 200 OK + transação finalizada
    else nenhuma linha atualizada
        DB-->>API: Nenhuma linha elegível
        API-->>Operador: 409 Conflict
    end
```

## 3. Histórico e aprovação

Versão 1.0, preparada em 2026-11-13; aprovação do orientador/avaliador pendente. Consulte o [histórico consolidado](index.md#historico-de-versoes-e-aprovacoes).
