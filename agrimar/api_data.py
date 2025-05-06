import os
import requests as r
from opencage.geocoder import OpenCageGeocode
from flask_babel import _
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('variables.env')

def get_address_info_from_coords(lat, lon):
    key = os.getenv('OPENCAGE_API_KEY')  # Fetch OpenCage API key from .env
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

def get_weather_data(lat, lon, format="optimized"):
    weather_key = os.getenv('WEATHER_API_KEY')  # Fetch OpenWeatherMap API key from .env
    weather_url = (f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&lang=fr&exclude=minutely,hourly&appid={weather_key}&units=metric")
    response = r.get(weather_url)
    if response.status_code != 200:
        raise Exception(_(f"Failed to fetch weather data: {response.status_code}"))
    return response.json()

def format_weather_summary(weather_data):
    current = weather_data['current']
    today = weather_data['daily'][0]
    
    temp_now = current.get('temp')
    humidity = current.get('humidity')
    wind = current.get('wind_speed')
    uvi = current.get('uvi')
    description = current['weather'][0].get('description', 'No description')
    
    temp_max = today['temp']['max']
    temp_min = today['temp']['min']
    rain_chance = today.get('pop', 0) * 100  # convert to %
    rain_amount = today.get('rain', 0)  # optional if provided

    summary = (f"Current weather: {temp_now}°C, {humidity}% humidity, "
               f"{wind} m/s wind, UV index {uvi}, {description}. "
               f"Today: High {temp_max}°C, Low {temp_min}°C, "
               f"{rain_chance:.0f}% chance of rain")
    
    if rain_amount:
        summary += f", {rain_amount}mm expected."
    
    return summary


def get_soil_data(lat, lon, format="optimized"):
    if format == "full":
        url = (f"https://rest.isric.org/soilgrids/v2.0/properties/query?"
                    f"lon={lon}&lat={lat}"
                    f"&property=bdod&property=cec&property=cfvo&property=clay"
                    f"&property=nitrogen&property=ocd&property=ocs&property=phh2o"
                    f"&property=sand&property=silt&property=soc&property=wv0010"
                    f"&property=wv0033&property=wv1500"
                    f"&depth=0-5cm&depth=5-15cm&depth=15-30cm&depth=30-60cm"
                    f"&depth=60-100cm&depth=100-200cm"
                    f"&value=mean")
    else:
        url = (f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property=phh2o&property=clay&property=sand&property=silt&property=nitrogen&property=ocd&depth=0-5cm&depth=0-30cm&value=mean")

    response = r.get(url)
    if response.status_code != 200:
        raise Exception(_(f"Failed to fetch soil data: {response.status_code}"))
    return response.json()

def format_soil_summary(soil_data):
    layers = soil_data.get('properties', {}).get('layers', [])
    
    def get_mean(layer_name):
        for layer in layers:
            if layer.get('name') == layer_name:
                depths = layer.get('depths', [])
                if depths and 'values' in depths[0]:
                    return depths[0]['values'].get('mean')
        return None

    ph = get_mean('phh2o')
    clay = get_mean('clay')
    sand = get_mean('sand')
    silt = get_mean('silt')
    nitrogen = get_mean('nitrogen')
    ocd = get_mean('ocd')

    # format strings
    ph_str = f"pH {ph/10:.1f}" if ph is not None else "pH unavailable"  # divide by 10 per d_factor
    clay_str = f"{clay/10:.0f}%" if clay is not None else "clay unavailable"
    sand_str = f"{sand/10:.0f}%" if sand is not None else "sand unavailable"
    silt_str = f"{silt/10:.0f}%" if silt is not None else "silt unavailable"
    nitrogen_str = f"{nitrogen/100:.2f}%" if nitrogen is not None else "nitrogen unavailable"
    ocd_str = f"{ocd/10:.2f}%" if ocd is not None else "organic carbon unavailable"

    return (f"Soil summary: {ph_str}; "
            f"Texture: {clay_str}, {sand_str}, {silt_str}; "
            f"Nitrogen: {nitrogen_str}; Organic Carbon: {ocd_str}")