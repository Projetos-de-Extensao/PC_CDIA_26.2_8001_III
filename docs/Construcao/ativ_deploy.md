# Atividades de deploy e transição

## Objetivo
Registrar a sequência operacional de implantação da solução em ambiente de produção acadêmica.

## Etapas
1. Preparar a instância EC2 com Docker e Git
2. Configurar `.env` com `DJANGO_SECRET_KEY`, `POSTGRES_*` e hosts permitidos
3. Fazer deploy do código por `git pull`
4. Subir o ambiente com `docker compose up -d --build`
5. Rodar migrates e criações de superusuário
6. Validar `/api/` e `/admin/`
7. Confirmar persistência após reinício dos containers

## Evidências esperadas
- `docker compose ps` com serviços em execução
- `docker compose logs` sem erros de banco
- acesso à API via IP da EC2
- dados preservados após reinicialização
