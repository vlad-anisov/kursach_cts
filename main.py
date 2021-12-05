import telebot

from three import get_map
from first_part import first_part
from attenuation_and_dispersion import attenuation_and_dispersion

TOKEN = '2102086086:AAE0pb2tUNuwxSu7dSL11a7tromtIM3t4jo'

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(content_types=['text'])
def start_message(message):
    # cities = message.text.split(",")
    # cities = [city.strip() for city in cities]
    # first_part(cities, bot, message)
    # get_map(cities, cities, bot, message)
    try:
        cities = message.text.split(",")
        cities = [city.strip() for city in cities]
        if len(cities) not in [12, 13]:
            bot.send_message(message.chat.id, f'Должно быть 12 или 13 городов, а вы ввели {len(cities)}')
            return
        if len(cities) == 12:
            first_part(cities, bot, message)
            get_map(cities, cities, bot, message)
        if len(cities) == 13:
            attenuation_and_dispersion(cities, bot, message)

    except Exception as e:
        bot.send_message(message.chat.id, f'Что-то пошло не так: {e}')


if __name__ == '__main__':
    bot.infinity_polling(timeout=100, long_polling_timeout=50)
