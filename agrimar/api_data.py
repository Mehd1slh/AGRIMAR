import requests as r
from opencage.geocoder import OpenCageGeocode
from flask_babel import _

def get_address_info_from_coords(lat, lon):
    key = 'b54875250f1a448d91b56a8a5b6a50c1'
    geocoder = OpenCageGeocode(key)
    result = geocoder.reverse_geocode(lat, lon, language='ar')
    
    if result and len(result):
        address_components = result[0]['components']
        address = result[0]['formatted']
        city = address_components.get('city', '') or address_components.get('town', '') or address_components.get('village', '')
        region = address_components.get('state', '') or address_components.get('region', '')
        country = address_components.get('country', '')
        return {
            'address': address,
            'city': city,
            'region': region,
            'country': country
        }
    return None

def get_weather_data(lat , lon , format="optimized"):
    weather_key = "65c19ff251fedc2e059c2fbfed70adfa"
    if format == "full" :
        weather_url = (f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&lang=fr&appid={weather_key}&units=metric")
    else:
        weather_url = (f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&lang=fr&exclude=minutely,hourly&appid={weather_key}&units=metric")
    response = r.get(weather_url)
    if response.status_code != 200:
        raise Exception(_(f"Failed to fetch weather data: {response.status_code}"))
    return response.json()

def get_soil_data(lat, lon , format="optimized"):
    if format == "full":
        url = (f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&"
            f"property=bdod&property=cec&property=cfvo&property=clay&property=nitrogen&"
            f"property=ocd&property=ocs&property=phh2o&property=sand&property=silt&"
            f"property=soc&property=wv0010&property=wv0033&property=wv1500&"
            f"depth=0-5cm&depth=0-30cm&depth=5-15cm&depth=15-30cm&depth=30-60cm&"
            f"depth=60-100cm&depth=100-200cm&value=Q0.05&value=Q0.5&value=Q0.95&value=mean&value=uncertainty")
    else:
        url = (f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&"
        f"property=bdod&property=cec&property=cfvo&property=clay&property=nitrogen&"
        f"property=ocd&property=ocs&property=phh2o&property=sand&property=silt&"
        f"property=soc&"
        f"depth=0-5cm&depth=0-30cm&depth=5-15cm&depth=15-30cm&depth=30-60cm&"
        f"depth=60-100cm&depth=100-200cm&value=mean")

    response = r.get(url)
    if response.status_code != 200:
        raise Exception(_(f"Failed to fetch soil data: {response.status_code}"))
    return response.json()