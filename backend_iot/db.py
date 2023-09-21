from peewee import Model, IntegerField, DateTimeField, DoesNotExist, FloatField, BooleanField
from playhouse.sqliteq import SqliteQueueDatabase
from playhouse.shortcuts import model_to_dict
from backend_iot.common import current_latitude, current_longitude
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
db.create_tables([Record, AQI])

def get_latest_record():
    try:
        return Record.select().order_by(Record.timestamp.desc()).get()
    except DoesNotExist:
        return add_record()

def add_record(**info):
    return Record.create(**info)

def update_record(record):
    record["latitude"] = current_latitude
    record["longitude"] = current_longitude
    record["timestamp"] = datetime.now()
    record["aqi"] = get_aqi(current_latitude, current_longitude)
    return record

def record_to_dict(record):
    temp = model_to_dict(record)
    del temp["id"]
    return temp

def handle_new_data(form):
    latest = record_to_dict(get_latest_record())

    for key in form.keys():
        if key not in latest.keys():
            continue
        if key == "fan_speed" and latest["auto"]:
            continue
        latest[key] = form[key]

    new_record = update_record(latest)
    add_record(**new_record)
    return new_record
