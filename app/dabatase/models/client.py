from datetime import datetime, timezone
from sqlalchemy import BigInteger, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from app.dabatase.db import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    tipo_solicitacao: Mapped[str] = mapped_column(String(255), nullable=False)
    valor_patrimonio: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Aguardando Análise")
    prioridade: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pipefy_card_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ProcessedEvent(Base):
    __tablename__ = "processed_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    event_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    processado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )