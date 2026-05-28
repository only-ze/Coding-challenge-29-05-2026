from app.services.pipefy_service import PipefyService

def test_create_card_payload_contem_mutation_graphql():
    service = PipefyService()
    result = service.build_create_card_payload(
        nome="Test User",
        email="test@example.com",
        valor_patrimonio=100000.0,
        tipo_solicitacao="Teste",
    )

    assert "query" in result
    assert "createCard" in result["query"]
    assert "CreateCardInput" in result["query"]
    assert "variables" in result
    assert result["variables"]["input"]["title"] == "Test User"

def test_create_card_payload_contem_fields_attributes():
    service = PipefyService()
    result = service.build_create_card_payload(
        nome="Test User",
        email="test@example.com",
        valor_patrimonio=300000.0,
        tipo_solicitacao="Abertura",
    )

    fields = result["variables"]["input"]["fields_attributes"]
    field_ids = [f["field_id"] for f in fields]
    assert "email" in field_ids
    assert "valor_patrimonio" in field_ids
    assert "tipo_solicitacao" in field_ids

def test_update_card_field_payload_contem_mutation_graphql():
    service = PipefyService()
    result = service.build_update_card_field_payload(
        card_id="card_123",
        novo_status="Processado",
        prioridade="prioridade_alta",
    )

    assert "query" in result
    assert "updateCardField" in result["query"]
    assert "UpdateCardFieldInput" in result["query"]
    assert "variables" in result
    assert result["variables"]["input"]["card_id"] == "card_123"

def test_simulate_create_card_retorna_card_id():
    service = PipefyService()
    result = service.simulate_create_card(
        nome="Test",
        email="test@example.com",
        valor_patrimonio=50000.0,
        tipo_solicitacao="Consulta",
    )

    card_id = result["resposta_simulada"]["data"]["createCard"]["card"]["id"]
    assert card_id is not None
    assert len(card_id) > 0

def test_simulate_update_card_field_retorna_sucesso():
    service = PipefyService()
    result = service.simulate_update_card_field(
        card_id="card_456",
        novo_status="Processado",
        prioridade="prioridade_normal",
    )

    assert result["resposta_simulada"]["data"]["updateCardField"]["success"] is True