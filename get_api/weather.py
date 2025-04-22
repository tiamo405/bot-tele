import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
import config
WEATHER_KEY = config.WEATHER_KEY

lat = "21.0064973"
lon = "105.8284344"
def get_weather(lat=lat, lon=lon):
    url = "https://api.weatherbit.io/v2.0/current?lat={lat}&lon={lon}&key={key}".format(lat=lat, lon=lon, key=WEATHER_KEY)
    response = requests.get(url)
    data = response.json()
    return data["data"][0]

if __name__ == '__main__':
    get_weather()
    # print(get_weather())