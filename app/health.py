from fastapi import APIRouter


route = APIRouter()


@route.get("/readiness")
def readiness():
    return {'message': 'ok'}

@route.get("/liveness")
def liveness():
    return {'status': 'up'}