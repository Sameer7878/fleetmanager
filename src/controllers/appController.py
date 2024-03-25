"""
This module contains the app controller
"""
import sys

sys.path.append('src')
import asyncio, json
from typing import List
from fastapi import WebSocket, FastAPI

from models.dbManager import DBManager
from middleware.customAPIsErrors import customApiError


class AppController:
    def __init__(self):
        self.dbManager = DBManager()
        self.STREAM_DELAY = 1

    def createRoute(self, routeDetails):
        if not (routeDetails and routeDetails.allStages and routeDetails.routes):
            raise customApiError("Empty Stages or Route Data Not Found", 204)
        routeDetails.allStages = [ {"stageName": x [ 1 ], "stageCoord": x [ 0 ]} for x in routeDetails.allStages ]
        for i in range(len(routeDetails.routes [ 0 ] [ 'waypoints' ])): routeDetails.allStages [ i ] [
            'stageCoord' ] = [ routeDetails.routes [ 0 ] [ 'waypoints' ] [ i ] [ 'latLng' ] [ 'lat' ],
                               routeDetails.routes [ 0 ] [ 'waypoints' ] [ i ] [ 'latLng' ] [ 'lng' ] ]
        routeData = {
            "busNumber": routeDetails.busNumber,
            "busPlateNumber": routeDetails.busPlateNumber,
            "driverName": routeDetails.driverName,
            "driverMobile": routeDetails.driverMobile,
            "busRunningStatus": False,
            "routeName": routeDetails.routeName,
            "routeStageWithNames": routeDetails.allStages,
            "routeAllCoord": routeDetails.routes [ 0 ] [ 'coordinates' ],
            "allotedBusId": "0",
            "totalRouteDistance": routeDetails.routes [ 0 ] [ 'summary' ] [ 'totalDistance' ],
            "routeMoreInfo": routeDetails.routes,
            "areaName": routeDetails.areaName,
            "busMoveDirection": "DOWN",
            "lastUpdatedLoc": [ ],
            "remarks": [ ],
            "routeStageVisitInfo": {},
            "curStage": 0,
            "geofenceFlag": False,
            "geofenceDistance": 5000
        }
        route = self.dbManager.createRoute(routeData)
        return route

    def modifyRoute(self, routeDetails):
        if "routes" in routeDetails:
            routeDetails [ "routeAllCoord" ] = routeDetails [ 'routes' ] [ 0 ] [ 'coordinates' ]
            routeDetails [ "totalRouteDistance" ] = routeDetails [ 'routes' ] [ 0 ] [ 'summary' ] [ 'totalDistance' ]
            routeDetails [ "routeMoreInfo" ] = routeDetails [ 'routes' ]
            routeDetails [ 'allStages' ] = [ {"stageName": x [ 1 ], "stageCoord": x [ 0 ]} for x in
                                             routeDetails [ 'allStages' ] ]
            for i in range(len(routeDetails [ 'routes' ] [ 0 ] [ 'waypoints' ])): routeDetails [ 'allStages' ] [ i ] [
                'stageCoord' ] = [ routeDetails [ 'routes' ] [ 0 ] [ 'waypoints' ] [ i ] [ 'latLng' ] [ 'lat' ],
                                   routeDetails [ 'routes' ] [ 0 ] [ 'waypoints' ] [ i ] [ 'latLng' ] [ 'lng' ] ]
            routeDetails [ "routeStageWithNames" ] = routeDetails [ 'allStages' ]
        dbOut = self.dbManager.modifyRoute(routeDetails)
        return dbOut

    async def fetchLocationAndDirection(self, busId):
        location = await self.dbManager.fetchRouteLocation(busId)
        busDirection = self.dbManager.getVehicleDirection(busId)
        return location, busDirection

    async def eventGenerator(self, busId, request):
        previous_data = None
        busDirection = None
        while True:
            try:
                if await request.is_disconnected():
                    print('break')
                    break
                latest_data, busDirection = await self.fetchLocationAndDirection(busId)

                if latest_data != previous_data:
                    yield json.dumps(
                        {"event": "update", "busId": busId, "moveDirection": busDirection,
                         "location": latest_data})
                    previous_data = latest_data
                await asyncio.sleep(self.STREAM_DELAY)
            except Exception as e:
                print(f"Error occurred: {e}")

    async def notificationEventGenerator(self, request):
        while True:
            try:
                if await request.is_disconnected():
                    print('break')
                    break
                unsentData = self.dbManager.getGeoDetails()
                if unsentData:
                    for bus in unsentData:
                        yield json.dumps(
                            {"event": "notify", "message": f"Bus No: {bus [ 'busNumber' ]} Entered Into The College"
                             })
                        self.dbManager.updateGeofenceState(bus [ 'busPlateNumber' ], True)
                        await asyncio.sleep(self.STREAM_DELAY)
                await asyncio.sleep(self.STREAM_DELAY)
            except Exception as e:
                print(f"Error occurred: {e}")

    async def updateBusNewLocation(self, location: list, busPlateNumber):
        self.dbManager.updateBusHistory(busPlateNumber, location)
        return await self.dbManager.updateNewLocation(location, busPlateNumber)

    def getAllRoutes(self, filterOut={}):
        return self.dbManager.getAllRoutes(filterOut)

    def getRouteDetails(self, busNo):
        routeData = self.dbManager.getRouteDetails(busNo)
        return routeData

    def deleteRoute(self, busPlateNumber):
        return self.dbManager.deleteBus(busPlateNumber)

    def getLocationHistory(self, busPlateNumber, dateString):
        return self.dbManager.getLocationHistory(busPlateNumber) [ 'routeStageVisitInfo' ] [ dateString ]


class VehicleToServerConnectionManager:
    def __init__(self):
        self.active_connections: List [ WebSocket ] = [ ]

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def boardcast_to_web(self, data):
        for conn in self.active_connections:
            try:
                await conn.send_json(data)
            except:
                await self.disconnect(conn)

    async def boardcast_to_single(self, data, websocket: WebSocket):
        try:
            await websocket.send_json(data)
        except:
            await self.disconnect(websocket)
