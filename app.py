import pandas as pd
from bs4 import BeautifulSoup
import requests
import twilio
from tqdm import tqdm
import time
import configparser
import os
from twilio.rest import Client
from datetime import datetime

config = configparser.ConfigParser()
config.read('credentials.txt')
keys = config['config']
api_key = keys['API_KEY_WAPI']
number = keys['PHONE_NUMBER']
account = keys['TWILIO_ACCOUNT_SID']
token = keys['TWILIO_AUTH_TOKEN']

config.read('numbers.txt')
key = config['daily']
number_send = key['0']


city = 'Tijuana'
url = f'http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=1&aqi=no&alerts=no'
data = []

response = requests.get(url).json()
n = len(response['forecast']['forecastday'][0]['hour'])

def get_attributes(response, i):
    date = response['forecast']['forecastday'][0]['hour'][i]['time'].split()[0]    
    hour_24 = int(response['forecast']['forecastday'][0]['hour'][i]['time'].split()[1].split(':')[0])
    minute = response['forecast']['forecastday'][0]['hour'][i]['time'].split(':')[1]
    time_24 = f"{hour_24}:{minute}"
    hour = datetime.strptime(time_24, '%H:%M').strftime('%I:%M %p')

    condition = response['forecast']['forecastday'][0]['hour'][i]['condition']['text']
    temp = response['forecast']['forecastday'][0]['hour'][i]['temp_c']
    rain = response['forecast']['forecastday'][0]['hour'][i]['will_it_rain']
    rain_prob = response['forecast']['forecastday'][0]['hour'][i]['chance_of_rain']
    return date, hour, condition, temp, rain, rain_prob, hour_24

for i in tqdm(range(n), colour = 'white'):
    data.append(get_attributes(response, i))

columns = ['date', 'hour', 'condition', 'temp', 'rain', 'rain_prob', 'hour_24']
df = pd.DataFrame(data, columns = columns)

df_rain = df[(df['rain']==1) & (df['hour_24']>=8) & (df['hour_24']<25)]
df_rain = df_rain[['hour', 'condition', 'rain_prob']]
df_rain = df_rain.rename(columns={'rain_prob': 'Probabilidad de lluvia', 'hour': 'Hora', 'condition': 'Condicion'})

pd.set_option('display.max_colwidth', 20)
pd.set_option('display.width', None)

msg = f"Hola!\n\nParece que va a llover \nEl pronostico de hoy en {city} es:\n{df_rain.to_string(justify='right' , index=False)}"

def send(msg, number, number_send):
    client = Client(account, token)
    message = client.messages \
        .create(
                body=msg,
                from_ = number,
                to = number_send
        )
    print(f"Mensaje enviado a: {number_send} \n{message.sid}\n\n")

if (df['rain'] == 1).any():
    for i in range(len(key)):
        n = key[f'{i}']
        # send(msg, number, n)
else:
    pass
