# Requisitos Suplementares — ZuumPay

## 1. Objetivo
Este documento detalha requisitos de desempenho, disponibilidade, segurança, operação e custos da solução ZuumPay.

## 2. Decisão de arquitetura
A solução utiliza EC2 + Docker + PostgreSQL por ser uma opção prática para demonstração acadêmica de deploy em nuvem, com baixa complexidade operacional e boa aderência ao requisito de uso de containers e banco relacional. O PostgreSQL fica em container dedicado e os segredos são lidos via variáveis de ambiente em `.env`.

## 3. Requisitos de desempenho
- API em Django com resposta consistente em cenários locais e de teste
- Consultas de produtos por atributos em JSONField devem manter bom desempenho em coleções moderadas
- Uso de PostgreSQL e volume nomeado para persistência eficiente dos dados

## 4. Requisitos de disponibilidade
- A aplicação deve subir com `docker compose up -d --build`
- O banco deve ficar acessível ao serviço web apenas pela rede interna do Compose
- A API deve responder em HTTP 200 em endpoints principais e manter os dados após reinício dos containers

## 5. Requisitos de segurança
- Segredos em `.env`, fora do Git
- `DJANGO_SECRET_KEY` e senha do banco não versionados
- `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` configurados por ambiente
- Acesso administrativo protegido por autenticação do Django
- Comunicação somente por portas mínimas e, em produção, com acesso controlado pela EC2

## 6. Requisitos de operação e custo
- O ambiente acadêmico precisa operar com infraestrutura enxuta
- O custo de EC2 + Docker + Postgres em container é inferior ao de arquiteturas mais complexas
- O monitoramento se dá por logs do Docker e verificações manuais da API

## 7. Riscos
- Configuração incorreta de `.env`
- Falta de volume persistente para PostgreSQL
- Exposição indevida de portas do Security Group
- Dependência de banco local em desenvolvimento sem a configuração adequada

## 8. Critérios de aceitação
- Serviço web e banco subindo corretamente com Docker Compose
- API acessível via IP público da EC2 ou localhost
- Persistência confirmada após reinicialização do ambiente
- Documentação e configuração consistentes com a aplicação implementada

## 9. Identificação dos requisitos

Os identificadores abaixo são usados na [matriz de rastreamento](../Elaboracao/maps.md). Requisitos de segurança descrevem a configuração implementada e não substituem uma auditoria ou certificação.

| ID | Requisito verificável | Tipo |
|---|---|---|
| RF-01 | Endpoints de recursos exigem usuário autenticado. | Funcional |
| RF-02 | A API permite operações CRUD para lojistas, lojas, categorias, produtos, transações e itens de transação. | Funcional |
| RF-03 | Produtos aceitam atributos como objeto JSON e podem ser filtrados por chave/valor; PostgreSQL dispõe de índice GIN no campo. | Funcional / desempenho |
| RF-04 | A criação de transação com itens valida lojista, quantidades e soma dos itens, com rollback se a operação falhar. | Funcional / integridade |
| RF-05 | Só transações com status `PENDENTE` podem ser finalizadas: a aprovação altera o status para `PAGO` e o cancelamento para `CANCELADO`; uma finalização concorrente ou repetida retorna HTTP 409. | Funcional |
| RF-06 | O painel `/admin/` permite manutenção administrativa autenticada dos modelos registrados. | Funcional |
| RF-07 | A raiz da API e o endpoint `/` fornecem respostas de verificação/descoberta documentadas. | Funcional / operação |
| RNF-01 | O Compose inicia PostgreSQL e web, aguarda a saúde do banco, aplica migrações e mantém os dados em volume nomeado. | Confiabilidade |
| RNF-02 | O serviço web e o banco comunicam-se pela rede do Compose; o banco não publica porta no host. | Segurança |
| RNF-03 | Segredos e parâmetros por ambiente são fornecidos por variáveis e arquivo `.env`, que não deve ser versionado. | Segurança |
| RNF-04 | O objetivo acadêmico proposto é disponibilidade mensal de 95% para a API, excluídas janelas de manutenção anunciadas. É uma meta, não uma garantia contratual. | Serviço |
| RNF-05 | A solução deve ter uma estimativa mensal transparente, com premissas, itens incluídos e exclusões explícitas. | Custo |
| RNF-06 | A documentação deve construir em modo estrito e ser publicada pelo fluxo de GitHub Pages configurado. | Manutenibilidade |

## 10. Objetivos de serviço (SLA/SLO)

O ZuumPay é uma demonstração acadêmica, não um serviço de pagamentos comercial; portanto, **não há SLA contratual nem disponibilidade garantida**. Para validação do projeto, fica proposto o seguinte SLO, sujeito à aprovação do orientador:

- **Disponibilidade alvo:** 95% por mês-calendário para `GET /api/`, medida por verificações periódicas HTTP; manutenção anunciada fica fora do cálculo.
- **Tratamento de incidentes:** best effort, com diagnóstico por `docker compose ps` e `docker compose logs`; não existe plantão ou resposta garantida.
- **Recuperação:** não há RTO/RPO formal aprovado nem backup automatizado demonstrado no repositório. A disponibilidade do volume protege contra recriação simples dos containers, mas não contra perda do host/volume. Não se deve interpretar isso como backup ou recuperação de desastre.
- **Segurança de transporte:** HTTPS não está configurado no Compose/repositório; para tráfego público real, deve ser colocado proxy/TLS antes da aplicação.

O SLO só poderá ser tratado como compromisso após aprovação, monitoramento contínuo e procedimento de backup/restauração testado.

## 11. Estimativa de custo mensal

Estimativa de referência para **uma instância Linux EC2 t3.small em us-east-2, ligada 730 horas/mês**, com 20 GB de volume EBS gp3 e um endereço IPv4 público. Os valores são aproximados, em USD, e não representam uma fatura observada nem cotação vinculante.

| Item | Premissa | Estimativa mensal |
|---|---|---:|
| EC2 t3.small | US$ 0,0208/h × 730 h | US$ 15,18 |
| EBS gp3 | 20 GB × US$ 0,08/GB-mês | US$ 1,60 |
| IPv4 público | US$ 0,005/h × 730 h | US$ 3,65 |
| **Subtotal estimado** | Antes de impostos e itens excluídos | **US$ 20,43/mês** |

O cálculo supõe cobrança sob demanda, sem créditos/free tier. Não inclui transferência de dados para internet, snapshots/backup, métricas/monitoramento pagos, DNS, balanceador, impostos ou variação de preço/região. Docker e PostgreSQL em container não têm tarifa de licença nesta estimativa; seus recursos estão incluídos na EC2. Confirmar os preços e o tamanho real da instância na [AWS Pricing Calculator](https://calculator.aws/) antes de contratar. A instância usada na demonstração não foi identificada no código versionado, portanto esta tabela é apenas um cenário de orçamento.
