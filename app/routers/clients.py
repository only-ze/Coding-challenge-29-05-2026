from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.client import ClienteCreateRequest, ClienteResponse
from app.services.client_service import ClienteService

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post(
    "",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo cliente",
    description=(
        "Cria um novo cliente no banco de dados com status inicial 'Aguardando Análise' "
        "e dispara (simulado) a mutation createCard no Pipefy."
    ),
)
def criar_cliente(payload: ClienteCreateRequest, db: Session = Depends(get_db)):
    service = ClienteService(db)
    try:
        cliente = service.criar_cliente(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return ClienteResponse.model_validate(cliente)