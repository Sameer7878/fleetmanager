"""
This module contains methods to interact with the database.
"""
import sys

sys.path.append('src')
from config.dbConfig import db
from util.helperFunctions import getDateTime, getCurrentTime, getUniqueId
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

    def getAllRoutes(self):
        allRoutes = self.routesCol.find({})
        return json.loads(json_util.dumps(allRoutes))

    async def fetchRouteLocation(self, busPlateNumber):
        location = self.routesCol.find_one({"busPlateNumber": busPlateNumber}, {"lastUpdatedLoc": 1})
        if location [ 'lastUpdatedLoc' ] == [ ]:
            print("No location found")
            return self.getAllStagesCoords(busPlateNumber) [ 0 ] [ 'stageCoord' ]
        return location [ 'lastUpdatedLoc' ] [ -1 ]

    async def updateNewLocation(self, location: list, busPlateNumber):
        self.routesCol.update_one({"busPlateNumber": busPlateNumber},
                                  {"$push": {"lastUpdatedLoc": {"$each": [ location ], "$slice": -10}}})
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

    def updateStagesDetails(self, busPlateNumber, stageDetails):
        self.routesCol.update_one({"busPlateNumber": busPlateNumber},
                                  {"$push": {"routeStageVisitInfo": {"$each": [ stageDetails ], "$slice": -10000}}})
