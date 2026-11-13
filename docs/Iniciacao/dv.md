# Documento de Visão — ZuumPay

## 1. Introdução

### 1.1 Propósito
O objetivo deste projeto é oferecer uma plataforma acadêmica de pagamentos e gestão de lojistas em ambiente cloud, demonstrando uma arquitetura simples, segura e prática, baseada em Django, PostgreSQL e Docker em EC2.

### 1.2 Escopo
A solução contempla:
- API REST em Django para cadastro de lojistas, lojas, categorias, produtos e transações
- Persistência relacional em PostgreSQL
- Estrutura documental em JSON para atributos flexíveis de produtos
- Deploy em instância EC2 via Docker Compose
- Documentação de requisitos, arquitetura e implantação em MkDocs

### 1.3 Partes interessadas
- Lojistas e comerciantes
- Equipe de desenvolvimento
- Professores e avaliadores da disciplina
- Usuários finais que consomem a API e o painel administrativo

## 2. Problema e oportunidade
O problema central é a necessidade de gerir dados de pagamentos de forma organizada, segura e eficiente, sem depender de uma arquitetura monolítica pouco sustentável. A plataforma ZuumPay resolve esse cenário com uma API enxuta, estrutura modular e capacidade de crescer em etapas futuras.

## 3. Necessidades e funcionalidades

### 3.1 Necessidades
- Registrar lojistas e lojas
- Gerenciar categorias e produtos
- Consultar produtos por atributos semiestruturados
- Registrar e acompanhar transações financeiras simuladas
- Validar regras de negócio antes de confirmar a transação
- Operar a solução com variáveis de ambiente, segurança e deploy em EC2

### 3.2 Funcionalidades principais
- CRUD completo para lojistas, lojas, produtos e categorias
- Filtros de consulta em JSONField
- Ações de aprovação e cancelamento de transação
- Painel administrativo Django
- Dados de exemplo para validação local

## 4. Restrições
- O projeto é acadêmico e não processa pagamentos reais
- O banco não deve ficar exposto publicamente
- O ambiente de produção deve usar variáveis sensíveis fora do código
- A infraestrutura deve ser mantida com custo controlado e operação simples

## 5. Visão da solução
A solução é composta por um backend Django REST, banco PostgreSQL em container e deployment em EC2 com Docker Compose. A API expõe recursos para automatizar o cadastro e a consulta de dados, enquanto o app administrativo facilita manutenção e acompanhamento.

## 6. Critérios de sucesso
- API funcional e autenticada
- Persistência em PostgreSQL e volume Docker
- Transações com rollback em caso de violação de regra
- Documentação pública e consistente com a aplicação
- Deploy viável em EC2 com uso de Docker
