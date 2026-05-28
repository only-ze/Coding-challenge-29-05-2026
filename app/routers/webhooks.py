from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dabatase.db import get_db
from app.schemas.webhook import PipefyCardUpdatedWebhook, WebhookResponse
from app.services.client_service import (
    ClienteNaoEncontradoError,
    ClienteService,
    EventoDuplicadoError,
)

router = APIRouter(prefix="/webhooks/pipefy", tags=["Webhooks Pipefy"])

@router.post(
    "/card-updated",
    response_model=WebhookResponse,
    status_code=status.HTTP_200_OK,
    summary="Webhook de card atualizado no Pipefy",
    description=(
        "Recebe o evento de atualização de card do Pipefy, aplica a regra de prioridade "
        "com base no patrimônio do cliente e atualiza o banco local. "
        "Garante idempotência por event_id para evitar processamento duplicado."
    ),
)
def card_updated(payload: PipefyCardUpdatedWebhook, db: Session = Depends(get_db)):
    service = ClienteService(db)

    try:
        cliente = service.processar_webhook(payload)
    except EventoDuplicadoError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ClienteNaoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return WebhookResponse(
        mensagem="Evento processado com sucesso.",
        cliente_email=cliente.email,
        novo_status=cliente.status,
        prioridade=cliente.prioridade,
    )