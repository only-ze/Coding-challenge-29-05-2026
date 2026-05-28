import pytest
from fastapi.testclient import TestClient
from app.dabatase.models.client import Cliente


PAYLOAD_VALIDO = {
    "cliente_nome": "João Silva",
    "cliente_email": "joao.silva@example.com",
    "tipo_solicitacao": "Atualização cadastral",
    "valor_patrimonio": 250000,
}


def test_criar_cliente_com_payload_valido(client: TestClient):
    response = client.post("/clientes", json=PAYLOAD_VALIDO)

    assert response.status_code == 201
    body = response.json()
    assert body["nome"] == "João Silva"
    assert body["email"] == "joao.silva@example.com"
    assert body["tipo_solicitacao"] == "Atualização cadastral"
    assert body["valor_patrimonio"] == 250000.0
    assert body["status"] == "Aguardando Análise"
    assert body["prioridade"] is None
    assert body["pipefy_card_id"] is not None


def test_criar_cliente_persiste_no_banco(client: TestClient, db_session):
    client.post("/clientes", json=PAYLOAD_VALIDO)

    cliente_no_banco = (
        db_session.query(Cliente)
        .filter(Cliente.email == PAYLOAD_VALIDO["cliente_email"])
        .first()
    )

    assert cliente_no_banco is not None
    assert cliente_no_banco.nome == "João Silva"
    assert float(cliente_no_banco.valor_patrimonio) == 250000.0
    assert cliente_no_banco.status == "Aguardando Análise"


def test_criar_cliente_sem_nome_retorna_422(client: TestClient):
    payload = {**PAYLOAD_VALIDO, "cliente_nome": ""}
    response = client.post("/clientes", json=payload)
    assert response.status_code == 422


def test_criar_cliente_com_email_invalido_retorna_422(client: TestClient):
    payload = {**PAYLOAD_VALIDO, "cliente_email": "email_invalido"}
    response = client.post("/clientes", json=payload)
    assert response.status_code == 422


def test_criar_cliente_sem_campo_obrigatorio_retorna_422(client: TestClient):
    payload = {
        "cliente_nome": "João Silva",
        "tipo_solicitacao": "Atualização cadastral",
    }
    response = client.post("/clientes", json=payload)
    assert response.status_code == 422


def test_criar_cliente_com_patrimonio_zero_retorna_422(client: TestClient):
    payload = {**PAYLOAD_VALIDO, "valor_patrimonio": 0}
    response = client.post("/clientes", json=payload)
    assert response.status_code == 422


def test_criar_cliente_com_patrimonio_negativo_retorna_422(client: TestClient):
    payload = {**PAYLOAD_VALIDO, "valor_patrimonio": -1000}
    response = client.post("/clientes", json=payload)
    assert response.status_code == 422