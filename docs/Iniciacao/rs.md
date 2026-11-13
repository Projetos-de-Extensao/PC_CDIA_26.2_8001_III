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
