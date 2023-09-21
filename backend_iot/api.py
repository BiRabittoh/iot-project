from dotenv import load_dotenv
from os import getenv
import requests
load_dotenv()

OWM_API_KEY = getenv("OWM_API_KEY", None)

assert OWM_API_KEY is not None
api_url = "http://api.openweathermap.org/data/2.5/air_pollution?appid=" + OWM_API_KEY + "&lon={}&lat={}"


def get_aqi_owm(latitude: float, longitude: float):
    try:
        response = requests.get(api_url.format(longitude, latitude))
        weather_data = response.json()
        return weather_data['list'][0]['main']['aqi']
    except Exception as e:
        print("Exception:", e)
    return None
