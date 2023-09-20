from waitress import serve
from backend_iot import app

serve(app, listen='*:1111')
