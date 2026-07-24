# Client Management API

API interna para gestão de clientes e seus patrimônios investidos, com integração simulada ao **Pipefy** via GraphQL.

---

## Índice

- [Visão Geral](#visão-geral)
- [Stack e Arquitetura](#stack-e-arquitetura)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Pré-requisitos](#pré-requisitos)
- [Execução Local](#execução-local)
- [Executando os Testes](#executando-os-testes)
- [Exemplos de Requisição (curl)](#exemplos-de-requisição-curl)
- [Documentação Interativa](#documentação-interativa)
- [Mutations GraphQL do Pipefy](#mutations-graphql-do-pipefy)
- [Visão de Produção na AWS](#visão-de-produção-na-aws)

---

## Visão Geral

A aplicação expõe dois fluxos principais:

**Fluxo 1 — Criação de cliente (`POST /clientes`)**
Valida o payload recebido, persiste o cliente no PostgreSQL com status `"Aguardando Análise"` e simula o envio da mutation `createCard` ao Pipefy.

**Fluxo 2 — Webhook de atualização (`POST /webhooks/pipefy/card-updated`)**
Recebe o evento disparado pelo Pipefy, garante idempotência via `event_id`, calcula a prioridade do cliente com base no patrimônio e simula o envio da mutation `updateCardField`, atualizando o banco local para o status `"Processado"`.

---

## Stack e Arquitetura

| Camada | Tecnologia |
|---|---|
| Framework web | FastAPI |
| ORM | SQLAlchemy 2.x (Mapped / DeclarativeBase) |
| Banco de dados | PostgreSQL 16 via Docker |
| Validação | Pydantic v2 |
| Configuração | pydantic-settings + `.env` |
| Testes | pytest + pytest-cov |

A arquitetura segue a separação em quatro camadas:

```
Routers → Services → Repositories → Models
```

- **Routers**: recebem a requisição HTTP, delegam ao service e serializam a resposta.
- **Services**: contêm toda a regra de negócio (cálculo de prioridade, idempotência, orquestração das chamadas ao Pipefy).
- **Repositories**: isolam o acesso ao banco; nenhuma query SQL aparece fora desta camada.
- **Models**: mapeamento ORM das tabelas `clientes` e `processed_events`.

---

## Estrutura de Pastas

```
mundo-invest-api/
├── app/
│   ├── main.py                  # factory da aplicação FastAPI + lifespan
│   ├── config.py                # settings via pydantic-settings
│   ├── database.py              # engine, SessionLocal e get_db
│   ├── models/
│   │   └── cliente.py           # ORM: Cliente e ProcessedEvent
│   ├── schemas/
│   │   ├── cliente.py           # request/response de cliente
│   │   └── webhook.py           # payload e response do webhook
│   ├── repositories/
│   │   └── cliente_repository.py  # CRUD de Cliente e ProcessedEvent
│   ├── services/
│   │   ├── cliente_service.py   # regras de negócio
│   │   └── pipefy_service.py    # mutations GraphQL do Pipefy
│   └── routers/
│       ├── clientes.py          # POST /clientes
│       └── webhooks.py          # POST /webhooks/pipefy/card-updated
├── tests/
│   ├── conftest.py              # fixtures com SQLite em memória
│   ├── test_clientes.py         # testes do endpoint de criação
│   ├── test_webhooks.py         # testes de prioridade e idempotência
│   └── test_pipefy_service.py   # testes unitários das mutations GraphQL
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/)
- Python 3.12+ (apenas para rodar os testes localmente sem Docker)

---

## Execução Local

### Opção 1 — Docker Compose (recomendado)

Sobe o banco PostgreSQL e a API em conjunto:

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd mundo-invest-api

# 2. Copie o arquivo de variáveis de ambiente
cp .env.example .env

# 3. Suba os serviços
docker compose up --build
```

A API estará disponível em `http://localhost:8000`.

### Opção 2 — Somente o banco via Docker + API local

```bash
# 1. Suba apenas o PostgreSQL
docker compose up db -d

# 2. Instale as dependências Python
pip install -r requirements.txt

# 3. Configure as variáveis de ambiente
cp .env.example .env

# 4. Inicie a API
uvicorn app.main:app --reload
```

---

## Executando os Testes

Os testes usam um banco **SQLite em memória**, portanto não é necessário ter o PostgreSQL rodando para executá-los.

```bash
# Instale as dependências (se ainda não instalou)
pip install -r requirements.txt

# Execute todos os testes com cobertura
pytest tests/ -v --cov=app --cov-report=term-missing
```

Saída esperada:

```
tests/test_clientes.py::test_criar_cliente_com_payload_valido          PASSED
tests/test_clientes.py::test_criar_cliente_persiste_no_banco           PASSED
tests/test_clientes.py::test_criar_cliente_sem_nome_retorna_422        PASSED
tests/test_clientes.py::test_criar_cliente_com_email_invalido_retorna_422  PASSED
tests/test_clientes.py::test_criar_cliente_sem_campo_obrigatorio_retorna_422 PASSED
tests/test_clientes.py::test_criar_cliente_com_patrimonio_zero_retorna_422  PASSED
tests/test_clientes.py::test_criar_cliente_com_patrimonio_negativo_retorna_422 PASSED
tests/test_webhooks.py::test_webhook_define_prioridade_alta_...        PASSED
tests/test_webhooks.py::test_webhook_define_prioridade_normal_...      PASSED
tests/test_webhooks.py::test_webhook_patrimonio_exatamente_200k_...    PASSED
tests/test_webhooks.py::test_webhook_atualiza_status_no_banco          PASSED
tests/test_webhooks.py::test_webhook_event_id_duplicado_retorna_409    PASSED
tests/test_webhooks.py::test_webhook_com_email_inexistente_retorna_404 PASSED
tests/test_webhooks.py::test_webhook_event_id_duplicado_nao_altera_banco PASSED
tests/test_pipefy_service.py::test_create_card_payload_contem_mutation_graphql PASSED
tests/test_pipefy_service.py::test_create_card_payload_contem_fields_attributes PASSED
tests/test_pipefy_service.py::test_update_card_field_payload_contem_mutation_graphql PASSED
tests/test_pipefy_service.py::test_simulate_create_card_retorna_card_id PASSED
tests/test_pipefy_service.py::test_simulate_update_card_field_retorna_sucesso PASSED
```

---

## Exemplos de Requisição (curl)

### POST /clientes — Criar cliente

```bash
curl -s -X POST http://localhost:8000/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_nome": "João Silva",
    "cliente_email": "joao.silva@example.com",
    "tipo_solicitacao": "Atualização cadastral",
    "valor_patrimonio": 250000
  }' | python3 -m json.tool
```

**Resposta (201 Created):**

```json
{
  "id": 1,
  "nome": "João Silva",
  "email": "joao.silva@example.com",
  "tipo_solicitacao": "Atualização cadastral",
  "valor_patrimonio": 250000.0,
  "status": "Aguardando Análise",
  "prioridade": null,
  "pipefy_card_id": "sim_card_joao_silva_example_com",
  "criado_em": "2026-05-18T12:00:00Z",
  "atualizado_em": "2026-05-18T12:00:00Z"
}
```

**Erro de validação (422):**

```bash
curl -s -X POST http://localhost:8000/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_nome": "João",
    "cliente_email": "email-invalido",
    "tipo_solicitacao": "Consulta"
  }' | python3 -m json.tool
```

---

### POST /webhooks/pipefy/card-updated — Processar webhook

```bash
curl -s -X POST http://localhost:8000/webhooks/pipefy/card-updated \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt_123",
    "card_id": "card_456",
    "cliente_email": "joao.silva@example.com",
    "timestamp": "2026-05-18T12:00:00Z"
  }' | python3 -m json.tool
```

**Resposta (200 OK) — cliente com patrimônio >= 200.000:**

```json
{
  "mensagem": "Evento processado com sucesso.",
  "cliente_email": "joao.silva@example.com",
  "novo_status": "Processado",
  "prioridade": "prioridade_alta"
}
```

**Reenvio do mesmo evento (409 Conflict):**

```bash
curl -s -X POST http://localhost:8000/webhooks/pipefy/card-updated \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt_123",
    "card_id": "card_456",
    "cliente_email": "joao.silva@example.com",
    "timestamp": "2026-05-18T12:00:00Z"
  }' | python3 -m json.tool
```

```json
{
  "detail": "O evento 'evt_123' já foi processado anteriormente."
}
```

**Cliente não encontrado (404 Not Found):**

```bash
curl -s -X POST http://localhost:8000/webhooks/pipefy/card-updated \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt_999",
    "card_id": "card_000",
    "cliente_email": "nao.existe@example.com",
    "timestamp": "2026-05-18T12:00:00Z"
  }' | python3 -m json.tool
```

```json
{
  "detail": "Nenhum cliente encontrado com o e-mail 'nao.existe@example.com'."
}
```

---

## Documentação Interativa

Com a API rodando, acesse:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## Mutations GraphQL do Pipefy

As mutations estão implementadas em `app/services/pipefy_service.py`. A sintaxe foi obtida na [documentação pública do Pipefy](https://developers.pipefy.com/reference/mutations).

### createCard

Utilizada ao criar um novo cliente para registrar o card correspondente no pipe configurado.

```graphql
mutation CreateCard($input: CreateCardInput!) {
  createCard(input: $input) {
    card {
      id
      title
      url
      createdAt
    }
  }
}
```

**Variáveis enviadas:**

```json
{
  "input": {
    "pipe_id": "999999",
    "title": "João Silva",
    "fields_attributes": [
      { "field_id": "email",            "field_value": "joao.silva@example.com" },
      { "field_id": "valor_patrimonio", "field_value": "250000" },
      { "field_id": "tipo_solicitacao", "field_value": "Atualização cadastral" }
    ]
  }
}
```

### updateCardField

Utilizada ao processar o webhook para atualizar o status do card no Pipefy.

```graphql
mutation UpdateCardField($input: UpdateCardFieldInput!) {
  updateCardField(input: $input) {
    card {
      id
      title
    }
    success
  }
}
```

**Variáveis enviadas:**

```json
{
  "input": {
    "card_id": "card_456",
    "field_id": "status_processamento",
    "new_value": "Processado"
  }
}
```

Em produção, ambas as mutations seriam enviadas via `POST https://api.pipefy.com/graphql` com o header `Authorization: Bearer <PIPEFY_TOKEN>`.

---

## Visão de Produção na AWS

A estrutura atual é facilmente escalável na AWS seguindo o padrão serverless ou containerizado. Abaixo a proposta para cada componente.

### Banco de Dados

A tabela `clientes` e a tabela `processed_events` migrariam para o **Amazon RDS (PostgreSQL)** em configuração Multi-AZ, garantindo alta disponibilidade e failover automático. Para cargas de leitura intensas, um **RDS Read Replica** seria adicionado. O gerenciamento de credenciais passaria pelo **AWS Secrets Manager**, eliminando variáveis de ambiente em texto plano.

### API e Processamento

O código FastAPI seria containerizado e hospedado no **Amazon ECS (Fargate)** ou convertido para funções **AWS Lambda** usando a biblioteca `Mangum` como adapter ASGI. O **API Gateway** ficaria na frente, gerenciando autenticação (API Keys ou Cognito), throttling e roteamento para os endpoints `/clientes` e `/webhooks/pipefy/card-updated`.

### Webhook e Idempotência em Escala

Em alta volumetria, o endpoint de webhook não processaria o evento de forma síncrona. O fluxo recomendado seria:

1. O API Gateway recebe o evento do Pipefy e publica uma mensagem no **Amazon SQS** (fila com Dead Letter Queue configurada).
2. Uma função **Lambda** consome a fila SQS, verifica a idempotência consultando o `event_id` no **Amazon DynamoDB** (tabela `processed_events` com TTL automático) e executa as regras de negócio.
3. O DynamoDB é escolhido para a tabela de idempotência por sua latência de leitura em sub-milissegundo e pelo modelo de precificação por operação, ideal para verificações de deduplicação de alta frequência.
4. Após processar, a Lambda atualiza o RDS com o novo status do cliente.

Essa arquitetura desacopla a recepção do evento do processamento, absorve picos de tráfego sem perda de mensagens e garante que cada `event_id` seja processado exatamente uma vez mesmo em cenários de retry do Pipefy.

### Diagrama Resumido

```
Pipefy
  │
  ▼
API Gateway ──► SQS ──► Lambda (processa regra de negócio)
  │                          │
  │                          ├──► DynamoDB (idempotência)
  ▼                          └──► RDS PostgreSQL (clientes)
Lambda / ECS Fargate
(POST /clientes)
  │
  └──► RDS PostgreSQL
```
