from sqlalchemy.orm import Session
from app.database.models.client import Cliente
from app.repositories.client_repository import ClienteRepository, ProcessedEventRepository
from app.schemas.client import ClienteCreateRequest
from app.schemas.webhook import PipefyCardUpdatedWebhook
from app.services.pipefy_service import PipefyService

PATRIMONIO_ALTO_THRESHOLD = 200_000.0
PRIORIDADE_ALTA = "prioridade_alta"
PRIORIDADE_NORMAL = "prioridade_normal"
STATUS_PROCESSADO = "Processado"


class ClienteService:
    def __init__(self, db: Session):
        self.db = db
        self.cliente_repo = ClienteRepository(db)
        self.event_repo = ProcessedEventRepository(db)
        self.pipefy = PipefyService()

    def criar_cliente(self, payload: ClienteCreateRequest) -> Cliente:
        cliente = self.cliente_repo.criar(
            nome=payload.cliente_nome,
            email=str(payload.cliente_email),
            tipo_solicitacao=payload.tipo_solicitacao,
            valor_patrimonio=payload.valor_patrimonio,
        )

        resultado_pipefy = self.pipefy.simulate_create_card(
            nome=cliente.nome,
            email=cliente.email,
            valor_patrimonio=float(cliente.valor_patrimonio),
            tipo_solicitacao=cliente.tipo_solicitacao,
        )

        card_id = (
            resultado_pipefy["resposta_simulada"]["data"]["createCard"]["card"]["id"]
        )
        cliente = self.cliente_repo.atualizar_pipefy_card_id(cliente, card_id)

        return cliente

    def processar_webhook(self, payload: PipefyCardUpdatedWebhook) -> Cliente:
        if self.event_repo.evento_ja_processado(payload.event_id):
            raise EventoDuplicadoError(
                f"O evento '{payload.event_id}' já foi processado anteriormente."
            )

        cliente = self.cliente_repo.buscar_por_email(str(payload.cliente_email))
        if cliente is None:
            raise ClienteNaoEncontradoError(
                f"Nenhum cliente encontrado com o e-mail '{payload.cliente_email}'."
            )

        prioridade = (
            PRIORIDADE_ALTA
            if float(cliente.valor_patrimonio) >= PATRIMONIO_ALTO_THRESHOLD
            else PRIORIDADE_NORMAL
        )

        card_id = cliente.pipefy_card_id or payload.card_id
        self.pipefy.simulate_update_card_field(
            card_id=card_id,
            novo_status=STATUS_PROCESSADO,
            prioridade=prioridade,
        )

        cliente = self.cliente_repo.atualizar_status_e_prioridade(
            cliente, STATUS_PROCESSADO, prioridade
        )

        self.event_repo.registrar_evento(payload.event_id)

        return cliente


class EventoDuplicadoError(Exception):
    pass


class ClienteNaoEncontradoError(Exception):
    pass