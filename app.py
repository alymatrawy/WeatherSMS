from flask import Flask, send_from_directory, request, jsonify
import requests
from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Retrieve api keys from .env file
OWM_API_KEY = os.getenv('OWM_API_KEY')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Ensure credentials are not blank
if None in [OWM_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]:
    raise ValueError("One or more environment variables are missing.")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        name = request.form['name']
        city = request.form['city']
        phone_number = request.form['phone_number']
        
        weather = get_weather(city)
        print(f"Weather for {city}:\n{weather}")  # Output the weather to the console
        
        message = f"Hello {name},\n\nHere is the weather for {city}:\n{weather}"
        
        sms_sid = send_sms(phone_number, message)
        return jsonify({'status': 'success', 'message': f'Weather for {city} sent to {phone_number}', 'sms_sid': sms_sid})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def get_weather(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        weather = f"City: {data['name']}\nTemperature: {data['main']['temp']}°C\nWeather: {data['weather'][0]['description']}"
    else:
        weather = "City not found."
    
    return weather

def send_sms(to, body):
    try:
        message = client.messages.create(
            body=body,
            from_=TWILIO_PHONE_NUMBER,
            to=to
        )
        return message.sid
    except Exception as e:
        print(f"Error sending SMS: {e}")
        raise

if __name__ == '__main__':
    app.run(debug=True)
