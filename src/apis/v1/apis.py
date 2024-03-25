"""
This module contains all the API endpoints.
"""
import sys

sys.path.append('src')
from controllers.appController import AppController, VehicleToServerConnectionManager
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from pydantic import BaseModel
import asyncio
from sse_starlette.sse import EventSourceResponse
import ast


class AddRouteType(BaseModel):
    busNumber: str
    busPlateNumber: str
    driverName: str
    driverMobile: str
    allStages: list
    routeName: str
    routes: list
    areaName: str


class NewLocation(BaseModel):
    locationCoord: list
    busPlateNumber: str


appController = AppController()
connectionManager = VehicleToServerConnectionManager()

api = APIRouter(prefix="/apis",
                tags=[ "apis" ])


@api.post('/addroute/')
async def addroute(request: Request, routeData: AddRouteType):
    return appController.createRoute(routeData)


@api.get('/locationStream/{busPlateNumber}/')
async def locationStream(request: Request, busPlateNumber):
    return EventSourceResponse(appController.eventGenerator(busPlateNumber, request),
                               headers={"Cache-Control": "no-cache"})


@api.get('/notification/')
async def locationStream(request: Request):
    return EventSourceResponse(appController.notificationEventGenerator(request),
                               headers={"Cache-Control": "no-cache"})


@api.get('/getRouteData/')
async def getRouteData(request: Request):
    routeDetails = appController.getRouteDetails(request.query_params.get("busPlateNumber"))
    return routeDetails


@api.post("/updateData/")
async def updateData(request: Request):
    rUpdateData = await request.json()
    if request.query_params.get('type') == 'route':
        route = appController.modifyRoute(rUpdateData)
        return route
    return {"error": "Invalid request type"}


@api.get("/deleteRoute/")
async def deleteRoute(request: Request):
    if request.query_params.get('busPlateNumber', None):
        if appController.deleteRoute(request.query_params.get('busPlateNumber')):
            return {"status": True, "message": "route deleted"}

    return {"status": False, "message": "Invalid request type Or Invalid busPlateNumber"}


@api.get('/getLocationHistory/')
async def locationHistory(request: Request):
    locationHistory = appController.getLocationHistory(request.query_params.get('busPlateNumber'),
                                                       request.query_params.get('dateString'))
    return {"busPlateNumber": request.query_params.get('busPlateNumber'), "locationHistory": locationHistory}


@api.websocket('/EstablishConnectionWithServer/')
async def websocket_endpoint(websocket: WebSocket):
    await connectionManager.connect(websocket)
    try:
        while (True):
            msgFromVehicle = await websocket.receive_text()
            print(msgFromVehicle)
            msgFromVehicle = ast.literal_eval(msgFromVehicle)
            if msgFromVehicle [ 'message' ] == 'connectionRequest':
                await connectionManager.boardcast_to_single(
                    {"busPlateNumber": msgFromVehicle [ 'busPlateNumber' ],
                     "message": "Connection Established With Server"}, websocket)
                continue
            if await appController.updateBusNewLocation(msgFromVehicle [ 'vehicleCoord' ],
                                                        msgFromVehicle [ 'busPlateNumber' ]):
                await connectionManager.boardcast_to_single(
                    {"busPlateNumber": msgFromVehicle [ 'busPlateNumber' ], "message": "Location Updated"}, websocket)
            else:
                await connectionManager.boardcast_to_single(
                    {"busPlateNumber": msgFromVehicle [ 'busPlateNumber' ], "message": "Location Not Updated"},
                    websocket)

    except WebSocketDisconnect:
        await connectionManager.disconnect(websocket)
    except Exception as e:
        print(e.args, 'erre')
        pass
