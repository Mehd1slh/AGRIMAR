import os
from agrimar.api_data import get_weather_data, get_soil_data, format_soil_summary, get_address_info_from_coords
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv('variables.env')

# Initialize OpenAI client
openai_api_key = os.getenv('OPENAI_API_KEY')
chatbot = OpenAI(api_key=openai_api_key)

#prepare the system and inject api data into it
def prepare_prompt(address, weather_summary, soil_summary):
    """
    Creates a system prompt string embedding pre-fetched data,
    optimized for Moroccan dialects and rural language.
    """
    return f"""
    You are an agriculture expert assistant helping Moroccan farmers, especially those in the countryside.
    Many of these farmers speak in Moroccan Arabic (Darija) or rural dialects, sometimes mixing French or Amazigh words.

    Based on the following data:
    - User's address: {address}
    - Weather summary: {weather_summary}
    - Soil summary: {soil_summary}

    Your task:
    - Understand the farmer's question, even if expressed in Moroccan dialect.
    - If something is unclear, politely ask for clarification.
    - Answer in clear, simple language that is practical and useful for small farmers.
    - Do NOT use technical or academic terms; instead, use everyday farmer language.
    - Only answer questions related to agriculture, crops, weather, or soil.

    Remember: Your goal is to support farmers with actionable advice, adapted to their local context and way of speaking.
    """


#the Chatbot Logic
def CustomChatBot(user_input, prompt_context):
    """
    Chatbot function using pre-fetched API data injected via prompt_context.
    """
    chat = [{"role": "system", "content": prompt_context}]
    chat.append({"role": "user", "content": user_input})
    
    response = chatbot.chat.completions.create(
        model="gpt-4o-mini",  # swap to 'gpt-3.5-turbo' if needed
        messages=chat
    )
    assistant_reply = response.choices[0].message.content
    return assistant_reply

#generate a titlle based of the convo content
def generate_title(convo):
    """
    Generates a conversation title summarizing the main user query.
    """
    chat_history = [{"role": "system", "content": (
        "Given the following agriculture chatbot conversation, generate a short descriptive phrase "
        "summarizing what the user asked for. Only output the phrase—no 'title:' prefix."
    )}]
    
    for message in convo.messages:
        chat_history.append({"role": message.role, "content": message.content})
    
    response = chatbot.chat.completions.create(
        model="gpt-4o-mini",
        messages=chat_history,
        max_tokens=30,
        temperature=0.5
    )
    return response.choices[0].message.content

#summarize api data into a paragraph
def initialize_chat_context(lat, lon):
    """
    Fetches API data once per session and builds summarized prompt context.
    """
    weather_data = get_weather_data(lat, lon)
    soil_data = get_soil_data(lat, lon)
    soil_summary = format_soil_summary(soil_data)
    address = get_address_info_from_coords(lat, lon)

    # Optionally create a summarized weather string:
    weather_summary = f"Temperature: {weather_data['current']['temp']}°C, Humidity: {weather_data['current']['humidity']}%, Rain chance: {weather_data['daily'][0]['pop']*100:.0f}%."
    
    return prepare_prompt(address, weather_summary, soil_summary)


#turn audio messages into text messages
def transcribe_audio_with_gpt4o(audio_path):
    """
    Uses OpenAI's Whisper API to transcribe audio to text.
    """
    try:
        with open(audio_path, "rb") as audio_file:
            response = chatbot.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe", #use whisper-1 or gpt-4o-mini-transcribe
                file=audio_file,
            )
        return response.text
    
    except Exception as e:
        print(f"[ERROR] Transcription failed: {e}")
        return None