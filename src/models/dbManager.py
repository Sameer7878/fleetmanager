"""
This module contains methods to interact with the database.
"""
import sys

sys.path.append('src')
from config.dbConfig import db
from util.helperFunctions import getDateTime, getCurrentTime, getUniqueId, getCurrentDateForDb, getDistanceFromCollege
from bson import json_util
import json


class DBManager:

    def __init__(self):
        self.routesCol = db [ 'routes' ]
        self.usersCol = db [ 'users' ]
        self.busesCol = db [ 'buses' ]

    def createRoute(self, routeData):
        routeData [ "routeId" ] = getUniqueId()
        routeData [ "createdAt" ] = getCurrentTime()
        routeData [ "updatedAt" ] = getCurrentTime()
        self.routesCol.insert_one(routeData)
        return json.loads(json_util.dumps(routeData))

    def modifyRoute(self, routeData, insideCal=False):
        routeData [ "updatedAt" ] = getCurrentTime()
        self.routesCol.update_one({"routeId": routeData [ "routeId" ]}, {"$set": routeData})
        return json.loads(json_util.dumps(routeData))

    def getRouteDetails(self, busPlateNumber):
        routeData = self.routesCol.find_one({"busPlateNumber": busPlateNumber})
        return json.loads(json_util.dumps(routeData))

    def getAllRoutes(self, filterOut):
        allRoutes = self.routesCol.find({}, filterOut)
        return json.loads(json_util.dumps(allRoutes))

    def deleteBus(self, busPlateNumber):
        self.routesCol.delete_one({"busPlateNumber": busPlateNumber})
        return True

    async def fetchRouteLocation(self, busPlateNumber):
        location = self.routesCol.find_one({"busPlateNumber": busPlateNumber}, {"lastUpdatedLoc": 1})
        if location [ 'lastUpdatedLoc' ] == [ ]:
            print("No location found")
            return self.getAllStagesCoords(busPlateNumber) [ 0 ] [ 'stageCoord' ]
        return location [ 'lastUpdatedLoc' ] [ -1 ]

    async def updateNewLocation(self, location: list, busPlateNumber):
        getDistancefromClg = getDistanceFromCollege(location [ 0 ], location [ 1 ])
        if getDistancefromClg > 1000:
            self.updateGeofenceState(busPlateNumber, False)
        self.routesCol.update_one({"busPlateNumber": busPlateNumber},
                                  {"$push": {"lastUpdatedLoc": {"$each": [ location ], "$slice": -10}}})
        self.routesCol.update_one({"busPlateNumber": busPlateNumber},
                                  {"$set": {"geofenceDistance": getDistancefromClg}})
        return True

    def getAllStagesCoords(self, busPlateNumber):
        AllStages = self.routesCol.find_one({"busPlateNumber": busPlateNumber}, {"routeStageWithNames": 1})
        return AllStages [ 'routeStageWithNames' ]

    def gettotalDistance(self, busPlateNumber):
        totalDistance = self.routesCol.find_one({"busPlateNumber": busPlateNumber}, {"totalRouteDistance": 1})
        return totalDistance [ 'totalRouteDistance' ]

    def getCurStage(self, busPlateNumber):
        curStage = self.routesCol.find_one({"busPlateNumber": busPlateNumber}, {"curStage": 1})
        return curStage [ 'curStage' ]

    def updateCurStage(self, busPlateNumber, curStage):
        self.routesCol.update_one({"busPlateNumber": busPlateNumber}, {"$set": {"curStage": curStage}})

    def getLastTwoLOcations(self, busPlateNumber):
        lastTwoLOcations = self.routesCol.find_one({"busPlateNumber": busPlateNumber}, {"lastUpdatedLoc": 1})
        if lastTwoLOcations [ 'lastUpdatedLoc' ] == [ ] or len(lastTwoLOcations [ 'lastUpdatedLoc' ]) < 2:
            return False
        return lastTwoLOcations [ 'lastUpdatedLoc' ] [ -1:-3:-1 ]

    def getVehicleDirection(self, busPlateNumber):
        vehicleDirection = self.routesCol.find_one({"busPlateNumber": busPlateNumber}, {"busMoveDirection": 1})
        return vehicleDirection [ 'busMoveDirection' ]

    def updateBusDirection(self, busPlateNumber, direction):
        self.routesCol.update_one({"busPlateNumber": busPlateNumber}, {"$set": {"busMoveDirection": direction}})
        return True

    def updateBusHistory(self, busPlateNumber, locationHistory):
        self.routesCol.update_one({"busPlateNumber": busPlateNumber},
                                  {"$push": {
                                      f"routeStageVisitInfo.{getCurrentDateForDb()}": {"$each": [ locationHistory ]}}},
                                  upsert=True)

    def getLocationHistory(self, busPlateNumber):
        locationHis = self.routesCol.find_one({"busPlateNumber": busPlateNumber}, {"routeStageVisitInfo": 1, "_id": 0})
        print(locationHis)
        return json.loads(json_util.dumps(locationHis))

    def getGeoDetails(self):
        unsentGeoFence = self.routesCol.find({"geofenceFlag": False, "geofenceDistance": {"$lt": 1000}},
                                             {"geofenceFlag": 1, "geofenceDistance": 1, "busPlateNumber": 1,
                                              "busNumber": 1, "_id": 0})
        return json.loads(json_util.dumps(unsentGeoFence))

    def updateGeofenceState(self, busPlateNumber, state):
        self.routesCol.update_one({"busPlateNumber": busPlateNumber}, {"$set": {"geofenceFlag": state}})
        return True
