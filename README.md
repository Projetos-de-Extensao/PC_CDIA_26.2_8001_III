# Zuumpay — API de pagamentos

Aplicação Django/ Django REST Framework para cadastro de lojistas e transações. O projeto pode ser executado localmente e empacotado para publicação no AWS Elastic Beanstalk.

Projeto acadêmico da disciplina de Big Data e Cloud Computing.

## URL pública

**Aplicação no AWS:** [health check](http://zuumpay0.us-east-2.elasticbeanstalk.com/).

**API oficial:** [abrir a raiz da API](http://zuumpay0.us-east-2.elasticbeanstalk.com/api/).

**Console AWS:** [abrir o Elastic Beanstalk na região `us-east-2`](https://us-east-2.console.aws.amazon.com/elasticbeanstalk/home?region=us-east-2#/applications?applicationName=zuumpay-api).

**API local:** [abrir a raiz da API](http://127.0.0.1:8000/api/) após iniciar o servidor local.

O endpoint `/` responde com `{"status": "ok"}` e funciona como health check. A raiz `/api/` lista as coleções disponíveis.

**Documentação MkDocs:** [abrir site publicado](https://projetos-de-extensao.github.io/PC_CDIA_26.2_8001_III/). Build e deploy confirmados pelo GitHub Actions.

> A API exige autenticação. Use credenciais de um usuário Django; não exponha credenciais administrativas em clientes públicos.

### Endpoints da API

As coleções permitem `GET` (lista) e `POST` (criação). Lojistas têm operações de leitura, atualização e exclusão no detalhe. Transações começam como pendentes; o status só muda pelas ações de fluxo abaixo:

| Recurso | Coleção | Detalhe |
|---|---|---|
| Lojistas | `/api/lojistas/` | `/api/lojistas/<id>/` |
| Transações simuladas | `/api/transacoes/` | `/api/transacoes/<id>/` |

### Usar a API publicada

As coleções exigem autenticação. Para listar os lojistas no ambiente AWS, use as credenciais de um usuário Django:

```powershell
curl.exe -u seu-usuario:sua-senha http://zuumpay0.us-east-2.elasticbeanstalk.com/api/lojistas/
```

Sem autenticação, `/api/lojistas/` e `/api/transacoes/` devem responder HTTP 401. A raiz `/api/` e o health check `/` podem ser usados para verificar se o serviço está disponível.

### Fluxo de transações simuladas

1. Crie a transação com um lojista existente, valor maior que zero e chave Pix fictícia. O status inicial é `PENDENTE`; datas e status são controlados pelo servidor.
2. Finalize uma transação pendente enviando `POST` para `/api/transacoes/<id>/aprovar/` ou `/api/transacoes/<id>/cancelar/`.
3. A resposta inclui o status final (`PAGO` ou `CANCELADO`) e `finalizado_em`. Uma transação já finalizada não pode ser finalizada de novo; a API responde HTTP 409.

Exemplo local com autenticação básica:

```powershell
curl.exe -u seu-usuario:sua-senha -X POST http://127.0.0.1:8000/api/transacoes/1/aprovar/
```

Esse fluxo é apenas uma simulação acadêmica: não movimenta dinheiro, não valida a chave junto a uma instituição financeira e não deve receber dados reais de pagamento.

Exemplo de listagem autenticada local:

```powershell
$credenciais = "seu-usuario:sua-senha"
curl.exe -u $credenciais http://127.0.0.1:8000/api/lojistas/
```

`Transacao.lojista` recebe o ID de um lojista existente. Use somente valores simulados; a API não processa pagamentos reais nem deve receber dados de cartão.

## Executar localmente

Requisitos: Python 3.12 ou superior e acesso à internet para instalar as dependências.

No PowerShell, execute a partir da raiz do repositório:

```powershell
python -m pip install -r .\scr\DeployEB\requirements.txt
python .\scr\DeployEB\manage.py migrate
python .\scr\DeployEB\manage.py runserver
```

A aplicação fica disponível em `http://127.0.0.1:8000/`; o health check retorna `{"status": "ok"}`. O servidor local usa configurações de desenvolvimento automaticamente. Para entrar no Admin e testar os endpoints protegidos, execute `python .\scr\DeployEB\manage.py createsuperuser` uma vez. Não use a configuração de desenvolvimento em produção.

### Verificar localmente

Em outro terminal, a partir da raiz do repositório, valide a configuração e execute os testes automatizados:

```powershell
python .\scr\DeployEB\manage.py check
python .\scr\DeployEB\manage.py makemigrations --check --dry-run
python .\scr\DeployEB\manage.py test pagamentos
```

O estado esperado é `System check identified no issues`, `No changes detected` e todos os testes aprovados. O endpoint `/admin/` redireciona visitantes não autenticados à página de login; isso é esperado. O endpoint de dados `/api/lojistas/` retorna HTTP 401 sem autenticação.

## Empacotar e publicar no AWS Elastic Beanstalk

### Pré-requisitos

- Uma conta AWS com permissões para Elastic Beanstalk e os recursos necessários ao ambiente.
- AWS CLI e EB CLI instalados e configurados.
- A configuração atual em `scr/DeployEB/.elasticbeanstalk/config.yml` seleciona o perfil `eb-cli`, a região Ohio (`us-east-2`), a aplicação `zuumpay-api` e a plataforma Python 3.12. Confirme esses valores e o ambiente Elastic Beanstalk antes de publicar; eles podem precisar ser ajustados para a conta AWS de destino.
- Defina a variável `DJANGO_SECRET_KEY` nas propriedades de ambiente do Elastic Beanstalk. Gere uma chave nova e mantenha-a fora do repositório. Defina também `DJANGO_ALLOWED_HOSTS` com o CNAME do ambiente, por exemplo `meu-ambiente.us-east-2.elasticbeanstalk.com`. `DJANGO_DEBUG` já é configurado como `False` em `.ebextensions/django.config`.
- Configure HTTPS no balanceador/proxy do ambiente antes de definir `DJANGO_SECURE_SSL=True`; isso ativa o redirecionamento HTTPS e cookies seguros. Defina `DJANGO_HSTS_SECONDS` somente após confirmar que todo o domínio será servido por HTTPS.

Configure as credenciais AWS para o perfil `eb-cli` sem adicioná-las ao código ou aos arquivos versionados:

```powershell
aws configure --profile eb-cli
```

### Deploy

Execute os comandos a partir de `scr/DeployEB`:

```powershell
cd .\scr\DeployEB
python package_eb.py
eb status
eb deploy <nome-do-ambiente>
eb status <nome-do-ambiente>
```

O empacotador cria `app.zip`, conforme configurado no EB CLI. Ele inclui os arquivos ocultos `.ebextensions` necessários à configuração e às migrações e exclui o banco SQLite local, arquivos de mídia, ambientes virtuais e caches. As migrações e a coleta de arquivos estáticos são executadas durante o deploy.

Se ainda não existir um ambiente, `eb create <nome-do-ambiente>` cria recursos AWS e pode gerar custos. Revise a configuração e os custos na conta antes de executar esse comando. Depois do deploy, copie o CNAME exibido por `eb status` para a seção **URL pública** acima e teste `http://<CNAME>/`. Use `https://` somente se TLS estiver configurado no ambiente.

Depois de conectar-se à instância com `eb ssh <nome-do-ambiente>`, crie o superusuário dentro da instância:

```bash
cd /var/app/current
python manage.py createsuperuser
```

Use o usuário criado para entrar em `http://<CNAME>/admin/`. Confirme os endpoints `/`, `/api/`, `/api/lojistas/` e `/api/transacoes/`; sem autenticação, as coleções devem responder HTTP 401. Adicione ao README o CNAME real somente depois de verificar que o ambiente está saudável.

### Observações sobre produção

- A aplicação usa SQLite por padrão. O armazenamento local do Elastic Beanstalk não é compartilhado entre instâncias e não oferece persistência adequada para produção; para dados reais, configure um banco gerenciado, como Amazon RDS, antes de escalar ou tratar transações reais.
- O `check --deploy` alerta quando HSTS e HTTPS ainda não estão configurados. Configure HTTPS no ambiente antes de ativar essas opções; habilitar redirecionamento HTTPS sem um listener TLS pode deixar o serviço inacessível.
- Arquivos de mídia também não devem depender do disco local do ambiente; use armazenamento persistente, como Amazon S3, se a aplicação passar a recebê-los.
- A chave Django anteriormente escrita no código foi removida da configuração. Como ela já esteve versionada, use uma chave nova no ambiente AWS; removê-la do código atual não apaga seu histórico Git.
