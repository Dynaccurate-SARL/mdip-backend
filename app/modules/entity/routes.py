from fastapi import APIRouter
from fastapi import HTTPException

from typing import List

from ...lib.utils.exceptions import ResourseNotFound
from ...lib.utils.exceptions import ConflictErrorCode

from .services import EntityService
from .schemas import EntityCreate, EntityTypeEnum
from .schemas import EntityResponse


route = APIRouter()
entity_service = EntityService()


@route.post("/entity", response_model=EntityResponse, status_code=201)
async def create(payload: EntityCreate):
    """
    ## Creates an entity.

    ### Args:  
      >  payload (EntityCreate): The payload model.

    ### Raises:  
      >  HTTPException: Raises 422 if the name is already in use.  

    ### Returns:  
      >  EntityResponse: The response model.
    """
    try:
        entity = await entity_service.create(payload)
        return entity
    except ConflictErrorCode as err:
        raise HTTPException(status_code=422, detail=str(err),
                            headers={'X-Reason': err.reason})


@route.put("/entity/{id}", response_model=EntityResponse, status_code=200)
async def update_status(id: int):
    """
    ## Updates entity status.

    ### Args:  
      >  payload (EntityCreate): The payload model.

    ### Raises:  
      >  HTTPException: Raises 422 if the name is already in use.  

    ### Returns:  
      >  EntityResponse: The response model.
    """
    try:
        entity = await entity_service.update_status(id)
        return entity
    except ConflictErrorCode as err:
        raise HTTPException(status_code=422, detail=str(err),
                            headers={'X-Reason': err.reason})
    

@route.get("/entity/{id}", response_model=EntityResponse)
async def get_by_id(id: int):
    """
    ## Retrieve a entity by id.

    ### Args:  
      >  id (int): The entity ID.  

    ### Raises:  
      >  HTTPException: Raises 404 if entity was not found.  

    ### Returns:  
      >  EntityResponse: The response model.
    """
    try:
        entity = await entity_service.get_by_id(id)
        return entity
    except ResourseNotFound as err:
        raise HTTPException(status_code=404, detail=str(err),
                            headers={'X-Reason': err.reason})


@route.get("/entity", response_model=List[EntityResponse])
async def get_all(entity_type: EntityTypeEnum, name: str = ""):
    """
    ## Retrieve a list of entities.

    ### Args:  
      >  name (str): Drug name to filter (optional).

    ### Returns:  
      >  DrugsResponse: The response model.
    """
    entity = await entity_service.get_all(entity_type, name)
    return entity


@route.delete("/entity/{id}", response_model=EntityResponse)
async def delete_by_id(id: int):
    """
    ## Deletes a entity by id.

    ### Args:  
      >  id (int): The entity ID.  

    ### Raises:  
      >  HTTPException: Raises 404 if entity was not found.  

    ### Returns:  
      >  EntityResponse: The response model.
    """
    try:
        entity = await entity_service.delete_by_id(id)
        return entity
    except ResourseNotFound as err:
        raise HTTPException(status_code=404, detail=str(err),
                            headers={'X-Reason': err.reason})
