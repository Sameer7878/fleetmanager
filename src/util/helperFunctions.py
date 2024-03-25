from datetime import datetime, timedelta
from pytz import timezone
import uuid
import math


def getDateTime():
    now_utc = datetime.now(timezone('UTC'))
    return now_utc


def utcfromtimestamp(date):
    return datetime.fromtimestamp(date, timezone('UTC'))


def getUniqueId():
    return str(uuid.uuid4())


def getCurrentTime():
    format = "%d-%m-%Y %H:%M:%S"
    now_utc = datetime.now(timezone('UTC'))
    asia_time = now_utc.astimezone(timezone('Asia/Kolkata'))
    return str(asia_time.strftime(format))


def getCurrentDateForDb():
    format = "%d-%m-%Y"
    now_utc = datetime.now(timezone('UTC'))
    asia_time = now_utc.astimezone(timezone('Asia/Kolkata'))
    return str(asia_time.strftime(format))


def getDistanceFromCollege(lat2, lon2,lat1=14.027382, lon1=80.021450):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [ lat1, lon1, lat2, lon2 ])

    # Haversine formula
    dlon = lon2-lon1
    dlat = lat2-lat1
    a = math.sin(dlat / 2) ** 2+math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    radius_of_earth = 6371000  # Radius of Earth in meters
    distance = radius_of_earth * c

    return distance
