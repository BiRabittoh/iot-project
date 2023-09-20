from backend_iot import app
from flask import request, redirect, render_template

@app.route("/")
def index_route():
    return { "hello": "world" }
