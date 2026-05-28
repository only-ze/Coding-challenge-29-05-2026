from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator

class ClienteCreateRequest(BaseModel):
    cliente_nome: str = Field(..., min_length=2, max_length=255)
    cliente_email: EmailStr
    tipo_solicitacao: str = Field(..., min_length=2, max_length=255)
    valor_patrimonio: float = Field(..., gt=0)

    @field_validator("cliente_nome", "tipo_solicitacao")
    @classmethod
    def must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("O campo não pode ser vazio ou conter apenas espaços.")
        return v.strip()

class ClienteResponse(BaseModel):
    id: int
    nome: str
    email: str
    tipo_solicitacao: str
    valor_patrimonio: float
    status: str
    prioridade: str | None
    pipefy_card_id: str | None
    criado_em: datetime
    atualizado_em: datetime

    model_config = {"from_attributes": True}