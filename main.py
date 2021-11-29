import telebot

from three import get_map
from first_part import first_part

TOKEN = '2102086086:AAE0pb2tUNuwxSu7dSL11a7tromtIM3t4jo'

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(content_types=['text'])
def start_message(message):
    try:
        cities = message.text.split(",")
        cities = [city.strip() for city in cities]
        get_map(cities, cities, bot, message)
        first_part(cities, bot, message)
    except Exception as e:
        bot.send_message(message.chat.id, f'Что-то пошло не так: {e}')


if __name__ == '__main__':
    bot.infinity_polling(timeout=100, long_polling_timeout=50)
