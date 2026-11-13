# Construção e implantação

A fase de construção implementa a solução em Django, com integração ao PostgreSQL e preparação para deploy em EC2 com Docker Compose.

## Estrutura da solução
- `scr/DeployEB` contém a aplicação Django; o nome da pasta é legado e não significa que o deploy atual use Elastic Beanstalk
- `pagamentos` implementa o domínio de lojistas, lojas, produtos e transações
- `docker-compose.yml` orquestra `web` e `db`
- `.env` guarda segredos fora do versionamento

## Fluxo de validação
1. Instalar dependências e configurar `.env`
2. Rodar migrações e carga de dados de exemplo
3. Validar endpoints e regras do negócio
4. Subir os containers e confirmar persistência no volume de dados

## Checklist de deploy EC2
- Instalar Docker e Docker Compose
- Ajustar Security Group para liberar SSH e a porta da API
- Clonar o repositório e configurar `.env`
- Executar `docker compose up -d --build`
- Verificar logs e acesso à API

As etapas operacionais, estratégia escolhida e plano de rollback estão em [Transição — Atividades de deploy](../Transicao/ativ_deploy.md).
