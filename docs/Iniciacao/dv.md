# Documento de Visão: ZuumPay — Plataforma de Pagamentos Instantâneos (Projeto de Extensão Acadêmica)

## 1. Introdução

### 1.1 Propósito
Definir a visão de escopo e arquitetura lógica/física para a implantação da plataforma **ZuumPay** na infraestrutura de nuvem AWS, demonstrando a viabilidade de uma arquitetura resiliente, de alta performance e custo otimizado para o processamento de transações financeiras e gestão de lojistas em tempo real.

### 1.2 Escopo
O escopo deste projeto de cloud engloba os seguintes componentes e serviços AWS:
1. **Portal Administrativo e API Transacional:** Desenvolvido em Python com Django REST Framework para cadastros de lojistas, gestão de usuários, processamento de pagamentos e emissão de relatórios consolidados.
2. **Camada de Cache de Alta Performance:** Utilização de Redis para acelerar consultas frequentes e mitigar gargalos de latência.
3. **Persistência de Dados Relacional:** Armazenamento relacional altamente disponível para as operações transacionais e controle financeiro.
4. **Infraestrutura de Rede e Segurança:** Isolamento lógico dos servidores de aplicação e banco de dados em VPC, firewall rígido (Security Groups) e gerenciamento seguro de variáveis de ambiente.
5. **Automação e Observabilidade:** Coleta centralizada de métricas e logs para auditoria e monitoramento de desempenho.

### 1.3 Definições, Acrônimos e Abreviações
- **API:** Application Programming Interface
- **VPC:** Virtual Private Cloud (Rede Virtual Privada)
- **RDS:** Relational Database Service (Banco de Dados Relacional Gerenciado)
- **SLA:** Service Level Agreement (Acordo de Nível de Serviço)
- **RPO:** Recovery Point Objective (Objetivo de Ponto de Recuperação)
- **RTO:** Recovery Time Objective (Objetivo de Tempo de Recuperação)
- **MVP:** Minimum Viable Product (Produto Viável Mínimo)

### 1.4 Referências
- AWS Well-Architected Framework (Pilares de Excelência Operacional, Segurança, Confiabilidade, Eficiência de Performance e Otimização de Custos).
- Lei Geral de Proteção de Dados (LGPD - Lei nº 13.709/2018).
- Requisitos do desafio acadêmico de Arquitetura Cloud.

---

## 2. Posicionamento

### 2.1 Oportunidade de Negócio
Pequenos e médios comerciantes locais exigem agilidade e precisão nas autorizações de vendas para evitar filas e abandono de carrinhos. Ecossistemas de tecnologia financeira bem-sucedidos (como a inspiração conceitual da Stone) demonstram que a proximidade com o lojista e a eficiência operacional são diferenciais críticos. No entanto, negócios em estágio inicial não dispõem de capital para manter datacenters físicos locais. Oferecer uma plataforma escalável na nuvem, com modelo flexível e dashboards em tempo real, atende a essa demanda de mercado com eficiência.

### 2.2 Descrição do Problema
O problema de... Lentidão sistêmica (latência média de ~200ms), perda ocasional de pacotes de autorização e quedas completas do portal administrativo durante picos de vendas no comércio.
Afeta... Comerciantes lojistas, operadores da plataforma e, indiretamente, os consumidores finais que enfrentam filas e falhas no checkout.
Cujo impacto é... Abandono de vendas, insatisfação dos lojistas, perda de receita, erosão da confiança na marca e sobrecarga da equipe de suporte técnico.
Uma solução bem-sucedida incluiria... Uma arquitetura enxuta e desacoplada na AWS que utilize cache em memória para otimizar consultas, garantindo respostas rápidas nas transações e estabilidade no portal de gestão.

### 2.3 Posicionamento do Produto
Para pequenos e médios comerciantes brasileiros, o ZuumPay é uma solução inteligente de pagamentos e gestão financeira que provê transações ágeis com meta de latência inferior a 50ms para 90% das requisições e alta disponibilidade. Diferente de sistemas legados on-premises lentos e caros, nossa solução combina a flexibilidade de microsserviços em Python com recursos gerenciados na AWS de forma economicamente viável para o contexto acadêmico e de mercado inicial.

---

## 3. Descrição dos Stakeholders e Usuários

| Stakeholder (Perfil) | Necessidade Primária | Expectativa na Nuvem (AWS) |
| :--- | :--- | :--- |
| **Comerciantes / Lojistas** | Processamento de pagamentos rápido e relatórios claros de vendas diárias. | Estabilidade ininterrupta e painéis que carreguem instantaneamente nos horários de pico. |
| **Equipe Acadêmica / Professores** | Validar a qualidade técnica, o rigor de engenharia e a coerência do projeto proposto. | Solução justificada à luz do AWS Well-Architected Framework e documentada de forma clara. |
| **Diretoria / Área Financeira (CFO)** | Manter o custo operacional da nuvem rigorosamente dentro do orçamento estipulado. | Uso otimizado de recursos com custos previsíveis, operando muito abaixo do teto de US$ 2.000,00/mês. |
| **Profissionais de Segurança (CISO)** | Proteger dados corporativos e credenciais de acesso contra ameaças externas. | Criptografia de dados, isolamento de rede em VPC e gerenciamento seguro de segredos. |

---

## 4. Visão Geral do Produto/Solução

### 4.1 Perspectiva do Produto
O ZuumPay operará como um ecossistema enxuto na nuvem AWS. A aplicação principal em Django REST Framework servirá as requisições web e administrativas via HTTPS, apoiada por uma instância de banco de dados relacional e uma camada de cache em memória para assegurar o cumprimento das metas de performance do MVP.

### 4.2 Funcionalidades Principais
- **Portal de Gestão Financeira:** Cadastro de lojistas, controle de usuários e visualização de extratos.
- **Processador de Pagamentos (Simulado):** Criação e autorização de transações financeiras em tempo real.
- **Dashboard de Vendas:** Resumo consolidados de recebimentos e fluxo de caixa.
- **Módulo de Conciliação e Extratos:** Consulta de histórico detalhado e suporte a estornos/cancelamentos.

### 4.3 Suposições e Dependências
- **Suposições:** Os usuários acessam a plataforma via navegadores modernos com conexão estável à internet; a equipe possui familiaridade com o ecossistema AWS e Python/Django.
- **Dependências:** Utilização exclusiva de dados tokenizados ou simulados para transações de cartões, descartando o uso de dados reais (PAN/CVV) em conformidade com o escopo educacional.

---

## 5. Recursos do Produto (Arquitetura AWS)

Para implementar a visão proposta de forma ideal e cobrir os requisitos do projeto acadêmico de extensão, a arquitetura AWS foi desenhada com os seguintes componentes enxutos:

| Serviço AWS | Papel na Arquitetura | Justificativa Técnica (Por que usar?) |
| :--- | :--- | :--- |
| **Amazon VPC** | Isolamento de Rede e Firewalls | Configurar sub-redes públicas e privadas. Security Groups atuando como firewalls de instâncias para restringir o tráfego estritamente às portas necessárias (80/443 e 5432). |
| **Amazon EC2** | Servidor de Aplicação Web (Portal/API) | Instância leve (ex: `t3.micro`) para hospedar a API administrativa em Django REST, oferecendo excelente custo-benefício para o escopo de MVP. |
| **Amazon RDS (PostgreSQL)** | Banco de Dados Relacional Central | Persistência segura de dados transacionais complexos (usuários, perfis, extratos) com suporte a transações ACID (configurado inicialmente em Single-AZ para otimizar os custos do MVP acadêmico). |
| **Amazon ElastiCache (Redis)** | Camada de Cache em Memória | Armazenamento de acesso rápido para dados frequentes, reduzindo a carga no banco relacional e viabilizando o objetivo de latência inferior a 50ms. |
| **AWS KMS** | Gerenciamento de Chaves de Criptografia | Centralização de chaves para criptografia de dados em repouso, atendendo conceitualmente aos requisitos de segurança (PCI-DSS e LGPD). |
| **Amazon CloudWatch** | Observabilidade e Logs | Coleta de métricas operacionais básicas (como uso de CPU e monitoramento de desempenho) para validação dos SLOs do projeto. |

---

## 6. Restrições do Projeto

- **Orçamentária:** O orçamento operacional mensal para hospedagem do protótipo funcional está fixado em no máximo US$ 2.000,00 por mês, sendo projetado de forma eficiente para operar em torno de **US$ 74,00 por mês**, garantindo ampla margem de segurança financeira.
- **Prazo:** O cronograma acadêmico impõe uma restrição de tempo semestral para a entrega das etapas de documentação, prototipagem e validação final.
- **Tecnológica:** A aplicação web principal deve obrigatoriamente utilizar Django REST Framework em Python. O deploy deve ser estruturado em ambiente de nuvem AWS utilizando boas práticas arquiteturais.
- **Segurança e Compliance:** Nenhum dado real de cartões (PAN, CVV) pode ser armazenado ou trafegado. O protótipo deve adotar dados simulados e tokenizados, alinhando-se conceitualmente às diretrizes da LGPD e PCI-DSS.
- **Pessoal:** O projeto é desenvolvido por uma equipe fixa de estudantes dividindo papéis de engenharia de software, arquitetura e operações.

---

## 7. Atributos de Qualidade (SLAs E SLOs)

- **Disponibilidade:** O protótipo acadêmico busca manter estabilidade adequada para demonstração, apoiando-se nos serviços gerenciados da AWS para assegurar alta confiabilidade.
- **Performance (Latência):** O sistema visa alcançar uma latência inferior a 50ms para 90% das consultas frequentes, impulsionado pelo uso estratégico do cache Redis e otimização de requisições ao banco de dados.
- **Segurança (Criptografia):** Todas as comunicações externas devem ser executadas sob protocolo seguro HTTPS/TLS. Os dados armazenados devem contar com criptografia em repouso gerenciada via AWS KMS.
- **Continuidade de Negócio (Backup & DR):**
  - **RPO (Recovery Point Objective):** Estratégia de backups periódicos configurados no RDS para mitigar perdas de dados transacionais.
  - **RTO (Recovery Time Objective):** Tempo otimizado de recuperação de falhas utilizando a infraestrutura gerenciada da nuvem.
- **Custo-eficiencia:** Utilização de instâncias de dimensionamento enxuto (`t3.micro`) para manter o custo operacional mensal estimado em aproximadamente **US$ 74,00**, demonstrando alta eficiência financeira (cerca de 3,7% do teto máximo permitido).

---

## 8. Aprovação e Histórico de Versões

| Versão | Data | Descrição da Alteração | Autor(es) |
| :--- | :--- | :--- | :--- |
| 1.0 | 10/09/2026 | Elaboração inicial do Documento de Visão para o projeto de extensão do ZuumPay. | Equipe de Engenharia e Arquitetura Cloud (ZuumPay) |