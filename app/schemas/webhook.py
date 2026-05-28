from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class PipefyCardUpdatedWebhook(BaseModel):
    event_id: str = Field(..., min_length=1)
    card_id: str = Field(..., min_length=1)
    cliente_email: EmailStr
    timestamp: datetime

class WebhookResponse(BaseModel):
    mensagem: str
    cliente_email: str
    novo_status: str
    prioridade: str