from app.config import settings


CREATE_CARD_MUTATION = """
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
"""

UPDATE_CARD_FIELD_MUTATION = """
mutation UpdateCardField($input: UpdateCardFieldInput!) {
  updateCardField(input: $input) {
    card {
      id
      title
    }
    success
  }
}
"""


class PipefyService:
    """
    Camada responsável por montar e (em produção) disparar as mutations
    GraphQL para a API do Pipefy em https://api.pipefy.com/graphql.

    No ambiente atual o envio HTTP está simulado: os payloads são construídos
    de forma idêntica ao que seria enviado em produção e retornados para
    rastreabilidade nos logs.
    """
    def _build_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.PIPEFY_TOKEN}",
        }

    def build_create_card_payload(
        self, nome: str, email: str, valor_patrimonio: float, tipo_solicitacao: str
    ) -> dict:
        return {
            "query": CREATE_CARD_MUTATION,
            "variables": {
                "input": {
                    "pipe_id": settings.PIPEFY_PIPE_ID,
                    "title": nome,
                    "fields_attributes": [
                        {"field_id": "email", "field_value": email},
                        {"field_id": "valor_patrimonio", "field_value": str(valor_patrimonio)},
                        {"field_id": "tipo_solicitacao", "field_value": tipo_solicitacao},
                    ],
                }
            },
        }

    def build_update_card_field_payload(
        self, card_id: str, novo_status: str, prioridade: str
    ) -> dict:
        return {
            "query": UPDATE_CARD_FIELD_MUTATION,
            "variables": {
                "input": {
                    "card_id": card_id,
                    "field_id": "status_processamento",
                    "new_value": novo_status,
                }
            },
        }

    def simulate_create_card(
        self, nome: str, email: str, valor_patrimonio: float, tipo_solicitacao: str
    ) -> dict:
        payload = self.build_create_card_payload(nome, email, valor_patrimonio, tipo_solicitacao)

        simulated_response = {
            "data": {
                "createCard": {
                    "card": {
                        "id": f"sim_card_{email.replace('@', '_').replace('.', '_')}",
                        "title": nome,
                        "url": "https://app.pipefy.com/pipes/simulated",
                        "createdAt": "2026-01-01T00:00:00Z",
                    }
                }
            }
        }

        return {
            "payload_enviado": payload,
            "headers": self._build_headers(),
            "resposta_simulada": simulated_response,
        }

    def simulate_update_card_field(
        self, card_id: str, novo_status: str, prioridade: str
    ) -> dict:
        payload = self.build_update_card_field_payload(card_id, novo_status, prioridade)

        simulated_response = {
            "data": {
                "updateCardField": {
                    "card": {"id": card_id},
                    "success": True,
                }
            }
        }

        return {
            "payload_enviado": payload,
            "headers": self._build_headers(),
            "resposta_simulada": simulated_response,
        }