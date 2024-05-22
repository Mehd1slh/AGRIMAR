from agrimar.model import Conversation, Message
from flask import request, session
from openai import OpenAI
import requests as r
from opencage.geocoder import OpenCageGeocode

chatbot = OpenAI()
weather_key = "65c19ff251fedc2e059c2fbfed70adfa"


def get_address_info_from_coords(lat, lon):
    key = 'b54875250f1a448d91b56a8a5b6a50c1'
    geocoder = OpenCageGeocode(key)
    result = geocoder.reverse_geocode(lat, lon, language='ar')

    if result and len(result):
        address_components = result[0]['components']
        address = result[0]['formatted']
        city = address_components.get(
            'city',
            '') or address_components.get(
            'town',
            '') or address_components.get(
            'village',
            '')
        region = address_components.get(
            'state', '') or address_components.get(
            'region', '')
        country = address_components.get('country', '')
        return {
            'address': address,
            'city': city,
            'region': region,
            'country': country
        }
    return None


def get_weather_data(lat, lon):
    weather_url = (
        f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={weather_key}&units=metric&timezone=")
    response = r.get(weather_url)
    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch weather data: {response.status_code}")
    return response.json()


def get_soil_data(lat, lon):
    url = (
        f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&"
        f"property=bdod&property=cec&property=cfvo&property=clay&property=nitrogen&"
        f"property=ocd&property=ocs&property=phh2o&property=sand&property=silt&"
        f"property=soc&property=wv0010&property=wv0033&property=wv1500&"
        f"depth=0-5cm&depth=0-30cm&depth=5-15cm&depth=15-30cm&depth=30-60cm&"
        f"depth=60-100cm&depth=100-200cm&value=Q0.05&value=Q0.5&value=Q0.95&value=mean&value=uncertainty")
    response = r.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch soil data: {response.status_code}")
    return response.json()


def CustomChatBot(user_input, lat=None, lon=None):
    if lat is None and lon is None:
        prompt = "You are an agriculture expert who answers farmers' questions such as crop types, weather, and other queries to improve their cultivation. if the user asked for weather related infos or soil properties infos that you can't provide without external source of data , tell the user to insert his location on our website ."
    else:
        weather_data = get_weather_data(lat, lon)
        soil_data = get_soil_data(lat, lon)
        address = get_address_info_from_coords(lat, lon)
        prompt = f"""
        Based on the following data:
        - User's address: {address}
        - Local Weather data: {weather_data} (exclude sunrise and sunset data)
        - Local Soil data: {soil_data}
        You are an agriculture expert who answers farmers' questions such as crop types, weather, and provides weather information. Additionally, you only answer agriculture-related questions in a simple and clear way.
        """

    chat = [{"role": "system", "content": prompt}]
    chat.append({"role": "user", "content": user_input})
    response = chatbot.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=chat
    )
    ChatGPT_reply = response.choices[0].message.content
    chat.append({"role": "assistant", "content": ChatGPT_reply})
    return ChatGPT_reply


def generate_title(convo):
    convo = Conversation()
    message = Message()
    msges = convo.messages
    chat_history = [{"role": "system", "content": " given the agriculture chatbot conversation i provide ,analyze both the user input and the assistant response with caution and generate a title that describes what's the conversation about ,what the chatter asked for.give me just the phrase no need for 'title:' wording "}]
    for message in msges:
        chat_history.append(
            f"Role: {message.role}, Content: {message.content}")
    response = chatbot.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=chat_history,
        max_tokens=30,
        temperature=0.5,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    # Extract the title from the completion
    title = response.choices[0].message.content
    return title
