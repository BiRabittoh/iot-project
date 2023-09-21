from backend_iot import app
from backend_iot.db import getLatestRecord, addRecord, get_aqi
from flask import request, redirect, render_template, abort
from datetime import datetime

current_latitude, current_longitude = 45.46437891252755, 7.872049153560152

def update_record(record):
    record["latitude"] = current_latitude
    record["longitude"] = current_longitude
    record["timestamp"] = datetime.now()
    record["aqi"] = get_aqi(current_latitude, current_longitude)

def latest_or_abort():
    latest = getLatestRecord()
    if latest is None:
        return abort(400)
    return latest

@app.route("/")
def index_route():
    if request.method == 'GET':
        return render_template("index.html")
    
    form = request.form
    update_record(form)
    addRecord(**form)

editable_fields = ["t_target", "power", "fan_speed", "auto", "airflow"]

@app.route("/data", methods = ['GET', 'POST'])
def data_route():

    if request.method == "GET":
        return latest_or_abort()
    
    latest = getLatestRecord()
    form = request.form

    for key in form.keys():
        if key not in latest.keys():
            continue
        if key == "fan_speed" and latest["auto"]:
            continue
        latest[key] = form[key]

    update_record(latest)
    addRecord(**latest)