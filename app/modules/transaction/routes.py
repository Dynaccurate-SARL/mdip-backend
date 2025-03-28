from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Form, File, UploadFile

from ...lib.utils.exceptions import ResourseNotFound
from ...lib.utils.exceptions import ResourceNotReady
from ...lib.utils.exceptions import BadRequest

from .services import TransactionService
from .schemas import TransactionCreate
from .schemas import TransactionResponse
from .schemas import TransactionTypeEnum
from typing import Annotated, List


route = APIRouter()
transaction_service = TransactionService()


@route.post("/entities/{entity_id}/transactions", response_model=TransactionResponse, status_code=201)
async def create(entity_id: int, title: Annotated[str, Form()],
                 category: Annotated[TransactionTypeEnum, Form()],
                 summary: Annotated[str | None, Form()] = None, file: Annotated[UploadFile | None, File()] = None):
    """
    ## Creates a transaction.

    ### Args:  
      >  payload (TransactionCreate): The payload model.

    ### Raises:  
      >  HTTPException: Raises 404 if entity was not found.  
      >  HTTPException: Raises 422 if the name is already in use.  

    ### Returns:  
      >  TransactionResponse: The response model.
    """
    try:
        payload = TransactionCreate(
            title=title, category=category, summary=summary, file=file)
        transaction = await transaction_service.create(entity_id, payload)
        return transaction
    except ResourseNotFound as err:
        raise HTTPException(status_code=422, detail=str(err),
                            headers={'X-Reason': err.reason})


@route.get("/transactions/{id}", response_model=TransactionResponse)
async def get_by_id(id: str):
    """
    ## Retrieve a transaction by id.

    ### Args:  
      >  id (int): The transaction ID.  

    ### Raises:  
      >  HTTPException: Raises 404 if transaction was not found.  

    ### Returns:  
      >  TransactionResponse: The response model.
    """
    try:
        transaction = await transaction_service.get_by_id(id)
        return transaction
    except ResourseNotFound as err:
        raise HTTPException(status_code=404, detail=str(err),
                            headers={'X-Reason': err.reason})
    except ResourceNotReady as err:
        raise HTTPException(status_code=404, detail=str(err),
                            headers={'X-Reason': err.reason})
    except BadRequest as err:
        raise HTTPException(status_code=400, detail=str(err),
                            headers={'X-Reason': err.reason})


@route.get("/transactions/files/{id}", response_model=TransactionResponse)
async def get_file_by_id(id: str):
    """
    ## Retrieve a transaction by id.

    ### Args:  
      >  id (int): The transaction ID.  

    ### Raises:  
      >  HTTPException: Raises 404 if transaction was not found.  

    ### Returns:  
      >  TransactionResponse: The response model.
    """
    try:
        transaction = await transaction_service.download_file(id)
        return transaction
    except ResourseNotFound as err:
        raise HTTPException(status_code=404, detail=str(err),
                            headers={'X-Reason': err.reason})
    except ResourceNotReady as err:
        raise HTTPException(status_code=404, detail=str(err),
                            headers={'X-Reason': err.reason})
    except BadRequest as err:
        raise HTTPException(status_code=400, detail=str(err),
                            headers={'X-Reason': err.reason})
