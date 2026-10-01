# DOCUMENTO DE REQUISITOS SUPLEMENTARES (v1.2)

## ZuumPay — Plataforma de Pagamentos Instantâneos

**Projeto:** Projeto de Cloud - Fase de Inception / Extensão Acadêmica  
**Data:** 01/10/2026  
**Status:** Versão ajustada e alinhada ao Documento de Visão do ZuumPay

---

## 1. Propósito e escopo

Este documento define os requisitos não-funcionais, os objetivos de nível de serviço (SLOs), o acordo de nível de serviço (SLA) e as condições operacionais da plataforma **ZuumPay**, uma solução de pagamentos instantâneos e gestão financeira para pequenos e médios comerciantes hospedada na AWS.

O escopo inclui:

- O Portal Administrativo e a API Transacional em Python (Django REST Framework) hospedados no Amazon EC2 (t3.micro).
- A camada de cache de alta performance utilizando Amazon ElastiCache (Redis).
- A persistência de dados transacionais no Amazon RDS (PostgreSQL) em ambiente Single-AZ otimizado para MVP.

Não fazem parte deste documento a implementação de redes físicas locais, processamento de dados reais de cartões (PAN/CVV) ou auditorias jurídicas externas.

---

## 2. Contexto e restrições

| Item | Premissa ou restrição |
|---|---|
| Escala inicial | MVP voltado para validação acadêmica e suporte inicial a dezenas de lojistas ativos. |
| Frequência de telemetria | Coleta de métricas básicas de infraestrutura (CPU, disco e rede) a cada 1 minuto via Amazon CloudWatch. |
| Pico de ingestão | Simulação de picos moderados de vendas no comércio local suportados por cache em memória. |
| Stack obrigatória | AWS (VPC, EC2 t3.micro, RDS PostgreSQL, ElastiCache Redis, KMS, CloudWatch) e Python / Django REST Framework. |
| Equipe | Equipe fixa de estudantes dividindo papéis de engenharia de software, arquitetura e operações. |
| Orçamento | Teto operacional máximo de US$ 2.000,00/mês, com custo projetado otimizado em torno de US$ 74,00/mês. |
| Regulamentação | Conformidade conceitual com a LGPD e diretrizes de segurança de mercado (PCI-DSS), utilizando dados exclusivamente tokenizados/simulados. |
| Crescimento esperado | Evolução controlada da base de usuários ao longo do cronograma semestral da disciplina. |

---

## 3. Definições e indicadores

- **SLA:** compromisso formal de desempenho e estabilidade da plataforma.
- **SLO:** objetivo mensurável que orienta o serviço (ex: latência inferior a 50ms para 90% das consultas cacheadas).
- **SLI:** indicador observado para verificar um SLO (tempo de resposta das requisições na API).
- **p95:** valor abaixo do qual estão 95% das medições de latência.
- **RPO:** máximo de dados que podem ser perdidos após uma falha (mitigado por backups periódicos no RDS).
- **RTO:** tempo máximo para restaurar o serviço em caso de desastre (otimizado pelos recursos gerenciados da AWS).
- **MTTR:** tempo médio para reparar ou restaurar o serviço após uma ocorrência operacional.

---

## 4. Requisitos de desempenho e capacidade

| ID | Requisito | Critério de aceitação |
|---|---|---|
| RNF-PER-01 | Latência de Consultas Frequentes | O sistema deve alcançar uma latência inferior a 50ms para 90% das consultas frequentes, apoiado pelo cache no Amazon ElastiCache (Redis). |
| RNF-PER-02 | Resposta da API Transacional | O tempo de resposta da API em Django REST Framework no Amazon EC2 (t3.micro) deve manter-se estável sob as requisições do MVP. |
| RNF-PER-03 | Otimização de Consultas | Redução da carga no banco relacional através do armazenamento prévio de dados de acesso recorrente no Redis. |
| RNF-PER-04 | Eficiência de Processamento | Execução fluida das rotinas de extrato e relatórios sem degradação perceptível no painel administrativo. |
| RNF-CAP-01 | Dimensionamento Enxuto | A infraestrutura deve operar eficientemente utilizando instâncias de dimensionamento enxuto (t3.micro), adequadas ao escopo acadêmico. |
| RNF-CAP-02 | Capacidade de Armazenamento | O Amazon RDS (PostgreSQL) deve comportar confortavelmente o volume de cadastros e transações simuladas do escopo. |

**Medição:** Amazon CloudWatch e métricas de monitoramento de desempenho da aplicação. As medições devem registrar percentis, taxa de erro, throughput e cenário utilizado.

---

## 5. Requisitos de disponibilidade e confiabilidade

| ID | Requisito | Critério de aceitação |
|---|---|---|
| RNF-CON-01 | Confiabilidade Gerenciada | O protótipo acadêmico deve manter estabilidade adequada para demonstração utilizando os serviços gerenciados da AWS. |
| RNF-CON-02 | Continuidade de Negócio (Backup) | Configuração de rotinas de backup periódicos no Amazon RDS (PostgreSQL) para mitigação de perda de dados transacionais. |
| RNF-CON-03 | Isolamento de Componentes | A separação lógica entre a aplicação, o cache e o banco de dados deve prevenir falhas em cascata entre as camadas. |
| RNF-CON-04 | Resiliência a Reinicializações | Instâncias EC2 e serviços de cache devem recuperar o estado operacional de forma controlada após manutenções ou ajustes. |
| RNF-CON-05 | Integridade Operacional | Prevenção contra corrupção de dados transacionais através do uso de restrições relacionais nativas do PostgreSQL. |
| RNF-CON-06 | Monitoramento de Conexões | Alertas básicos configurados para mitigar eventuais esgotamentos de conexões simultâneas no banco de dados. |

**Diretriz:** utilizar, quando compatível com o orçamento e o escopo de MVP acadêmico, os recursos gerenciados da AWS para assegurar alta confiabilidade.

---

## 6. Requisitos de segurança e privacidade

| ID | Requisito | Critério de aceitação |
|---|---|---|
| RNF-SEG-01 | Comunicação Segura | Todas as comunicações externas e acessos ao portal/API devem ser executados obrigatoriamente sob protocolo seguro HTTPS/TLS. |
| RNF-SEG-02 | Criptografia em Repouso | Os dados armazenados no banco de dados e volumes devem contar com criptografia gerenciada via AWS KMS. |
| RNF-SEG-03 | Isolamento de Rede | A infraestrutura deve ser isolada em Amazon VPC, utilizando sub-redes e Security Groups restritos às portas necessárias (80/443 e 5432). |
| RNF-SEG-04 | Conformidade de Dados (LGPD/PCI) | Proibição absoluta de armazenamento ou tráfego de dados reais de cartões (PAN/CVV), adotando exclusivamente dados simulados e tokenizados. |
| RNF-SEG-05 | Gestão de Credenciais | Proteção de chaves de acesso e variáveis sensíveis, evitando a exposição de segredos diretamente no código-fonte. |
| RNF-SEG-06 | Controle de Acesso ao Painel | O Portal Administrativo deve exigir autenticação segura para restrição de visualização de dados financeiros e cadastrais. |
| RNF-SEG-07 | Princípio do Menor Privilégio | Restrição de permissões nas políticas de acesso da AWS estritamente ao necessário para a execução do projeto. |

---

## 7. Requisitos de operação e observabilidade

| ID | Requisito | Critério de aceitação |
|---|---|---|
| RNF-OPS-01 | Coleta de Métricas Básicas | Utilização do Amazon CloudWatch para monitorar o uso de CPU das instâncias EC2 e a saúde geral do ambiente. |
| RNF-OPS-02 | Rastreabilidade Operacional | Centralização de logs de execução da API Django para auditoria e suporte à validação dos SLOs do projeto. |
| RNF-OPS-03 | Visibilidade de Recursos | Acompanhamento simplificado do consumo de instâncias e armazenamento para controle rigoroso de custos. |
| RNF-OPS-04 | Verificações de Saúde (Health Checks) | Validação periódica do status de resposta das rotas principais da aplicação e conectividade com o banco. |
| RNF-OPS-05 | Padronização de Logs | Formato de logs legíveis para facilitar a identificação de erros de requisição durante a fase de testes. |
| RNF-OPS-06 | Alertas Operacionais | Notificações básicas em caso de indisponibilidade severa dos serviços principais da arquitetura. |

---

## 8. Requisitos de manutenibilidade e entrega

| ID | Requisito | Critério de aceitação |
|---|---|---|
| RNF-MAN-01 | Stack Tecnológica Padronizada | A aplicação principal deve ser construída obrigatoriamente em Python utilizando o framework Django REST Framework. |
| RNF-MAN-02 | Organização do Código | Estrutura modular limpa e desacoplada, facilitando a integração entre o portal de gestão e a API de pagamentos simulados. |
| RNF-MAN-03 | Versionamento de Código | Utilização de controle de versão (Git) para rastreabilidade de todas as alterações na aplicação e infraestrutura. |
| RNF-MAN-04 | Documentação Técnica | Manutenção de documentação clara descrevendo os endpoints da API e as decisões arquiteturais adotadas. |
| RNF-MAN-05 | Clareza de Manutenção | Facilidade para realização de ajustes rápidos e correções de bugs pela equipe de desenvolvimento acadêmico. |

---

## 9. Requisitos de usabilidade

| ID | Requisito | Critério de aceitação |
|---|---|---|
| RNF-USA-01 | Acessibilidade do Portal | O Portal de Gestão Financeira deve ser acessível via navegadores web modernos com padrão responsivo para visualização de relatórios. |
| RNF-USA-02 | Clareza de Indicadores | Os dashboards de vendas e extratos devem apresentar resumos consolidados intuitivos para os lojistas. |
| RNF-USA-03 | Mensagens de Retorno Amigáveis | Retorno de códigos e mensagens compreensíveis nas requisições da API para facilitar o consumo pelo front-end ou testes. |

---

## 10. Requisitos de custo

| ID | Requisito | Critério de aceitação |
|---|---|---|
| RNF-CUS-01 | Teto Orçamentário | O custo operacional mensal da infraestrutura na AWS deve respeitar o limite máximo de US$ 2.000,00/mês estabelecido pela disciplina. |
| RNF-CUS-02 | Eficiência Financeira do MVP | O projeto deve ser dimensionado de forma otimizada (ex: uso de instâncias t3.micro e RDS/Redis adequados), mantendo o custo estimado em aproximadamente US$ 74,00/mês. |
| RNF-CUS-03 | Monitoramento Preventivo | Acompanhamento do painel de custos para garantir que não ocorram extrapolações imprevistas durante os testes. |
| RNF-CUS-04 | Descarte de Recursos Ociosos | Encerramento ou redimensionamento de recursos que não estejam em uso ativo fora dos momentos de validação. |

**Trade-off obrigatório:** O desenho arquitetural prioriza a viabilidade financeira e o teto acadêmico, optando por configurações enxutas (como instâncias t3.micro e Single-AZ) perfeitamente alinhadas ao escopo de protótipo e ao Documento de Visão.

---

## 11. SLA e responsabilidades

O SLA inicial da API de transações e gestão estabelece estabilidade adequada para o ambiente acadêmico, medido por requisições HTTP a partir de rotinas de teste.

| Responsável | Obrigações principais |
|---|---|
| AWS | Garantir a disponibilidade da infraestrutura física e dos serviços gerenciados (EC2, RDS, ElastiCache, VPC). |
| ZuumPay (Equipe) | Desenvolver o código em Django REST, configurar os recursos na AWS, garantir a segurança dos dados simulados e validar a observabilidade. |
| Equipe de projeto | Avaliar a conformidade técnica da arquitetura com o AWS Well-Architected Framework e os objetivos do projeto de extensão. |

Descumprimentos devem gerar registro de incidente, análise de causa e plano de ação. Penalidades ou créditos comerciais não se aplicam ao contexto acadêmico deste documento.

---

## 12. Dependências, riscos e decisões pendentes

| Item | Impacto | Tratamento |
|---|---|---|
| Limitações de capacidade da camada gratuita / créditos AWS | Custos operacionais acima do previsto caso os testes de carga excedam o dimensionamento. | Monitoramento constante via CloudWatch e uso estrito de instâncias de baixo custo (t3.micro). |
| Simulação de transações de pagamento | Ausência de integração com adquirentes reais de cartão de crédito. | Desenvolvimento de um mock/processador simulado interno com dados tokenizados para validação do fluxo completo. |
| Curva de aprendizado da equipe com a AWS | Possíveis atrasos na configuração correta de redes e políticas de segurança. | Divisão clara de papéis e consulta prévia à documentação oficial do AWS Well-Architected Framework. |
| Ajustes finos no cache Redis | Inconsistências temporárias se o TTL das chaves não for bem dimensionado. | Testes direcionados de integração para validar a persistência e a recuperação rápida do cache. |

---

## 13. Critérios de aprovação

O documento será considerado aprovado quando:

1. todos os requisitos técnicos estiverem alinhados ao Documento de Visão do ZuumPay;
2. a arquitetura demonstrar atendimento à meta de latência (<50ms com Redis) e eficiência de custos (~US$ 74/mês);
3. os critérios de segurança, isolamento em VPC e uso de dados simulados estiverem documentados;
4. a validação perante os pilares do AWS Well-Architected Framework estiver concluída;
5. os planos de backup, observabilidade e dimensionamento enxuto estiverem validados pela equipe.

---

## 14. Histórico de versões

| Versão | Data | Descrição | Autor |
|---|---|---|---|
| 1.0 | 27/08/2026 | Criação inicial do Documento de Requisitos Suplementares para o case ZuumPay. | Equipe do projeto |
| 1.2 | 01/10/2026 | Atualização e alinhamento completo com o Documento de Visão e stack técnica na AWS. | Equipe do projeto |