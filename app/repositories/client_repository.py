from sqlalchemy.orm import Session
from app.database.models.client import Cliente, ProcessedEvent

class ClienteRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar(self, nome: str, email: str, tipo_solicitacao: str, valor_patrimonio: float) -> Cliente:
        cliente = Cliente(
            nome=nome,
            email=email,
            tipo_solicitacao=tipo_solicitacao,
            valor_patrimonio=valor_patrimonio,
            status="Aguardando Análise",
        )
        self.db.add(cliente)
        self.db.commit()
        self.db.refresh(cliente)
        return cliente

    def buscar_por_email(self, email: str) -> Cliente | None:
        return self.db.query(Cliente).filter(Cliente.email == email).first()

    def atualizar_status_e_prioridade(
        self, cliente: Cliente, status: str, prioridade: str
    ) -> Cliente:
        cliente.status = status
        cliente.prioridade = prioridade
        self.db.commit()
        self.db.refresh(cliente)
        return cliente

    def atualizar_pipefy_card_id(self, cliente: Cliente, card_id: str) -> Cliente:
        cliente.pipefy_card_id = card_id
        self.db.commit()
        self.db.refresh(cliente)
        return cliente


class ProcessedEventRepository:
    def __init__(self, db: Session):
        self.db = db

    def evento_ja_processado(self, event_id: str) -> bool:
        return (
            self.db.query(ProcessedEvent).filter(ProcessedEvent.event_id == event_id).first()
            is not None
        )

    def registrar_evento(self, event_id: str) -> ProcessedEvent:
        evento = ProcessedEvent(event_id=event_id)
        self.db.add(evento)
        self.db.commit()
        self.db.refresh(evento)
        return evento