import os
from agrimar.model import Conversation, Message
from agrimar.api_data import get_address_info_from_coords, get_soil_data, get_weather_data
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('variables.env')

# Initialize the OpenAI chatbot with the API key from the .env file
openai_api_key = os.getenv('OPENAI_API_KEY')
chatbot = OpenAI(api_key=openai_api_key)

def CustomChatBot(user_input, lat=None, lon=None):
    if lat is None and lon is None:
        prompt = "You are an agriculture expert who answers farmers' questions such as crop types, weather, and other queries to improve their cultivation. if the user asked for weather related infos or soil properties infos that you can't provide without external source of data , tell the user to insert his location on our website."
    else:
        weather_data = get_weather_data(lat, lon)
        soil_data = 'null'#get_soil_data(lat, lon)
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
        chat_history.append(f"Role: {message.role}, Content: {message.content}")
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