import telebot
from telebot import types

import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


LISTEN_ADDRESS = '192.168.43.114' 
LISTEN_PORT = 55835 

token='7159848731:AAEDRJY7YT6DKSxGXAOjeOgOTyKqBHi2W3M'
bot=telebot.TeleBot(token)

paused = False
def handle_values(field_name, message, peak_value):
    if paused: return

    token = "my-super-secret-admin-token"
    org = "best_org" 
    url = "http://localhost:8086/" 

    write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org) 


    query_api = write_client.query_api()
    query = f'from(bucket: "best_bucket") \
                    |> range(start: -10m) \
                    |> filter(fn: (r) => r["_measurement"] == "my_measurement") \
                    |> filter(fn: (r) => r["_field"] == "{field_name}")'

    result = query_api.query(org="best_org", query=query)

    idx = 0
    sum = 0
    for table in result:
        for record in table.records:
            print("QUERY_RESULT: ",(record.get_field(), record.get_value()))
            idx += 1
            sum += record.get_value()
            if idx > 20: break

    if sum / idx >= peak_value:
        bot.send_message(message.chat.id,f'критический уровень {field_name}')
    
    time.sleep(2)

bot
@bot.message_handler(commands=['start'])
def start_message(message): 
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("стоп")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "Привет :з", reply_markup=markup)


    while True:           
        handle_values("co2", message, 7000)
        handle_values("humidity", message, 60)
        handle_values("temp_cel", message, 28)
        time.sleep(10)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == 'стоп':
        bot.stop_bot()



bot.infinity_polling()