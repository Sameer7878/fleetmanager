"""
This files consists of all the routes
"""
import sys
sys.path.append('src')
from controllers.appController import AppController
from fastapi import APIRouter,Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

routes = APIRouter()
templates = Jinja2Templates(directory="src/templates")
appController = AppController()

@routes.get('/')
def index(request: Request):
    driversDetails=appController.getAllRoutes(filterOut={"driverName":1,"driverMobile":1,"busNumber":1,"busPlateNumber":1,"routeName":1,"areaName":1,"_id":0,"busRunningStatus":1})
    allBuses=len(driversDetails)
    activeBuses=len([1 for bus in driversDetails if bus['busRunningStatus']])
    return templates.TemplateResponse('index.html', {'request': request,'allRoutes':driversDetails,'allBuses':allBuses,'activeBuses':activeBuses,'inactiveBuses':allBuses-activeBuses})


@routes.get('/auth/')
def auth(request: Request):
    return templates.TemplateResponse('login.html',{'request': request})


@routes.get('/routing/')
async def routing(request: Request):
    allRoutes=appController.getAllRoutes()
    return templates.TemplateResponse('routing.html',{'request': request,'allRoutes':allRoutes})

@routes.get('/recordLocation/{busPlateNumber}')
async def recordLocation(request:Request,busPlateNumber):
    return templates.TemplateResponse('demoRecordMobileGps.html',{"request":request,"busId":busPlateNumber})
@routes.get('/tracking/')
async def tracking(request: Request):
    allRoutes = appController.getAllRoutes()
    return templates.TemplateResponse('tracking.html',{"request":request,'allRoutes':allRoutes})
@routes.get('/profile/')
async def profile(request: Request):
    return templates.TemplateResponse('profile.html',{"request":request})
@routes.get('/logout/')
async def logout(request: Request):
    return templates.TemplateResponse('logout.html',{"request":request})
@routes.get('/locationHistory/')
async def locationHistory(request: Request):
    allRoutes = appController.getAllRoutes()
    return templates.TemplateResponse('locationHistory.html',{"request":request,'allRoutes':allRoutes})

