# Construção e deploy

Esta etapa reúne a implementação do MVP ZuumPay e as instruções para executar e publicar a aplicação.

## Aplicação

O [projeto Django está em `scr/DeployEB`](https://github.com/Projetos-de-Extensao/PC_CDIA_26.2_8001_III/tree/main/scr/DeployEB). O app `pagamentos` contém os modelos `Lojista` e `Transacao`; cada transação está relacionada a um lojista. A API REST autenticada oferece operações de consulta, criação, atualização e remoção:

- `/api/lojistas/` e `/api/lojistas/<id>/`
- `/api/transacoes/` e `/api/transacoes/<id>/`

O Django Admin está disponível em `/admin/`. A API é acadêmica e simulada: não processa pagamentos reais nem deve receber dados de cartão.

## Execução e publicação

O [README do repositório](https://github.com/Projetos-de-Extensao/PC_CDIA_26.2_8001_III/blob/main/README.md) contém os requisitos, os comandos para criar o ambiente virtual, instalar dependências, executar migrações, criar um superusuário e iniciar o servidor local. Também documenta a preparação do pacote `app.zip` e as etapas de publicação no AWS Elastic Beanstalk.

O pacote é criado por `python package_eb.py` a partir de `scr/DeployEB`; as instruções indicam como configurar o ambiente AWS, definir variáveis sensíveis, publicar a aplicação e verificar o health check. A URL pública deve ser registrada no README após o deploy confirmado.

## Escopo e limitações

O app usa SQLite por padrão e o Elastic Beanstalk ainda precisa ser configurado com um banco gerenciado antes de qualquer uso que exija persistência confiável ou escala horizontal. A API usa autenticação Django e requer um superusuário para acesso administrativo. Verifique o README para as opções de produção e HTTPS.
