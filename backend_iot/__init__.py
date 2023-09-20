from flask import Flask

app = Flask(__name__)

import backend_iot.views
