from fastapi import APIRouter


health_router = APIRouter()


@health_router.get("/readiness")
def readiness():
    return {'message': 'ok'}


@health_router.get("/liveness")
def liveness():
    return {'status': 'up'}
