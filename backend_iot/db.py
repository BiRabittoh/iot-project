from peewee import Model, IntegerField, DateTimeField, DoesNotExist, FloatField, BooleanField
from playhouse.sqliteq import SqliteQueueDatabase
from backend_iot.api import get_aqi_owm
from datetime import datetime, timedelta

db = SqliteQueueDatabase("records.db")
api_interval = timedelta(minutes=3)
lat_threshold = 0.03
lon_threshold = 0.03

class BaseModel(Model):
    class Meta:
        database = db

class Record(BaseModel):
    timestamp = DateTimeField(default=datetime.now)
    latitude = FloatField()
    longitude = FloatField()
    aqi = IntegerField()
    t_in = FloatField()
    t_out = FloatField()
    t_setpoint = FloatField()
    fan_speed = IntegerField()
    power = BooleanField()
    auto = BooleanField()
    co_in = FloatField()
    co_out = FloatField()
    no2_in = FloatField()
    pm10_out = FloatField()
    airflow = IntegerField()
    aq_in = IntegerField()

class AQI(BaseModel):
    timestamp = DateTimeField(default=datetime.now)
    value = IntegerField()

def set_aqi(value: int):
    try:
        AQI.delete().execute()
    except DoesNotExist:
        pass
    return AQI.create(value=value)

def get_aqi_from_cache(latitude, longitude):
    try:
        temp = AQI.select().order_by(AQI.timestamp.desc()).get()
    except DoesNotExist:
        return None
    
    if temp.latitude - latitude > lat_threshold:
        return None
    
    if temp.longitude - longitude > lon_threshold:
        return None
    
    delta = datetime.now() - temp.timestamp
    if delta > api_interval:
        return None
    
    return temp

def get_aqi(latitude, longitude):
    aqi = get_aqi_from_cache(latitude, longitude)

    if aqi is not None:
        return aqi.value
    
    return get_aqi_owm(latitude, longitude)

db.connect()
db.create_tables([Record])

def getLatestRecord():
    #User.select().order_by(User.id.desc()).get()
    try:
        return Record.select().order_by(Record.timestamp.desc()).get()
    except DoesNotExist:
        return None

def addRecord(**info):
    Record.create(**info)