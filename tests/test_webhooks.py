import pytest
from fastapi.testclient import TestClient
from app.database.models.client import Cliente, ProcessedEvent

PAYLOAD_CLIENTE_ACIMA = {
    "cliente_nome": "Ana Souza",
    "cliente_email": "ana.souza@example.com",
    "tipo_solicitacao": "Abertura de conta",
    "valor_patrimonio": 500000,
}

PAYLOAD_CLIENTE_NORMAL = {
    "cliente_nome": "Carlos Lima",
    "cliente_email": "carlos.lima@example.com",
    "tipo_solicitacao": "Consulta",
    "valor_patrimonio": 50000,
}

PAYLOAD_CLIENTE_EXATO = {
    "cliente_nome": "Maria Exata",
    "cliente_email": "maria.exata@example.com",
    "tipo_solicitacao": "Atualização",
    "valor_patrimonio": 200000,
}

def _webhook_payload(email: str, event_id: str = "evt_001", card_id: str = "card_001") -> dict:
    return {
        "event_id": event_id,
        "card_id": card_id,
        "cliente_email": email,
        "timestamp": "2026-05-18T12:00:00Z",
    }

def test_webhook_define_prioridade_alta_para_patrimonio_maior_ou_igual_200k(client: TestClient):
    client.post("/clientes", json=PAYLOAD_CLIENTE_ACIMA)

    response = client.post(
        "/webhooks/pipefy/card-updated",
        json=_webhook_payload(PAYLOAD_CLIENTE_ACIMA["cliente_email"]),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["prioridade"] == "prioridade_alta"
    assert body["novo_status"] == "Processado"

def test_webhook_define_prioridade_normal_para_patrimonio_menor_200k(client: TestClient):
    client.post("/clientes", json=PAYLOAD_CLIENTE_NORMAL)

    response = client.post(
        "/webhooks/pipefy/card-updated",
        json=_webhook_payload(PAYLOAD_CLIENTE_NORMAL["cliente_email"], event_id="evt_002"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["prioridade"] == "prioridade_normal"
    assert body["novo_status"] == "Processado"

def test_webhook_patrimonio_exatamente_200k_e_prioridade_alta(client: TestClient):
    client.post("/clientes", json=PAYLOAD_CLIENTE_EXATO)

    response = client.post(
        "/webhooks/pipefy/card-updated",
        json=_webhook_payload(PAYLOAD_CLIENTE_EXATO["cliente_email"], event_id="evt_003"),
    )

    assert response.status_code == 200
    assert response.json()["prioridade"] == "prioridade_alta"

def test_webhook_atualiza_status_no_banco(client: TestClient, db_session):
    client.post("/clientes", json=PAYLOAD_CLIENTE_ACIMA)
    client.post(
        "/webhooks/pipefy/card-updated",
        json=_webhook_payload(PAYLOAD_CLIENTE_ACIMA["cliente_email"]),
    )

    cliente_no_banco = (
        db_session.query(Cliente)
        .filter(Cliente.email == PAYLOAD_CLIENTE_ACIMA["cliente_email"])
        .first()
    )

    assert cliente_no_banco.status == "Processado"
    assert cliente_no_banco.prioridade == "prioridade_alta"

def test_webhook_event_id_duplicado_retorna_409(client: TestClient):
    client.post("/clientes", json=PAYLOAD_CLIENTE_ACIMA)

    webhook_payload = _webhook_payload(PAYLOAD_CLIENTE_ACIMA["cliente_email"])
    client.post("/webhooks/pipefy/card-updated", json=webhook_payload)

    response_duplicada = client.post("/webhooks/pipefy/card-updated", json=webhook_payload)

    assert response_duplicada.status_code == 409
    assert "já foi processado" in response_duplicada.json()["detail"]

def test_webhook_com_email_inexistente_retorna_404(client: TestClient):
    response = client.post(
        "/webhooks/pipefy/card-updated",
        json=_webhook_payload("naoexiste@example.com", event_id="evt_999"),
    )
    assert response.status_code == 404

def test_webhook_event_id_duplicado_nao_altera_banco(client: TestClient, db_session):
    client.post("/clientes", json=PAYLOAD_CLIENTE_NORMAL)

    webhook_payload = _webhook_payload(
        PAYLOAD_CLIENTE_NORMAL["cliente_email"], event_id="evt_idem"
    )
    client.post("/webhooks/pipefy/card-updated", json=webhook_payload)
    client.post("/webhooks/pipefy/card-updated", json=webhook_payload)

    eventos = (
        db_session.query(ProcessedEvent)
        .filter(ProcessedEvent.event_id == "evt_idem")
        .all()
    )
    assert len(eventos) == 1