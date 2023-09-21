from backend_iot import app
from backend_iot.db import get_latest_record, handle_new_data, record_to_dict
from flask import request, render_template, abort

def latest_or_abort():
    latest = get_latest_record()
    if latest is None:
        return abort(400)
    return record_to_dict(latest)

@app.route("/")
def index_route():
    if request.method == 'GET':
        return render_template("index.html")

@app.route("/data", methods = ['GET', 'POST'])
def data_route():
    if request.method == "GET":
        return latest_or_abort()
    return handle_new_data(request.form)
