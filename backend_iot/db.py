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
    latitude = FloatField(default=0)
    longitude = FloatField(default=0)
    aqi = IntegerField(default=0)
    t_in = FloatField(default=0)
    t_out = FloatField(default=0)
    t_setpoint = FloatField(default=0)
    fan_speed = IntegerField(default=0)
    power = BooleanField(default=False)
    auto = BooleanField(default=False)
    co_in = FloatField(default=0)
    co_out = FloatField(default=0)
    no2_in = FloatField(default=0)
    pm10_out = FloatField(default=0)
    airflow = IntegerField(default=0)
    aq_in = IntegerField(default=0)

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
        return addRecord()

def addRecord(**info):
    return Record.create(**info)