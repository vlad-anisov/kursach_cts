import telebot

from three import get_map
from first_part import first_part

TOKEN = '2102086086:AAE0pb2tUNuwxSu7dSL11a7tromtIM3t4jo'

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(content_types=['text'])
def start_message(message):
    cities = message.text.split(",")
    cities = [city.strip() for city in cities]
    # first_part(cities)
    # with open('first_table.xlsx', 'rb') as file:
    #     bot.send_document(message.chat.id, file)
    get_map(cities, cities)
    # with open('Матрица расстояний.txt', encoding='utf8') as text:
    #     bot.send_message(message.chat.id, text.read())
    with open('matrix.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    with open('Расположение городов на карте.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    with open('Соединение городов методом ветвей и границ.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    with open('Соединение городов методом ветвей и границ.txt', encoding='utf8') as text:
        bot.send_message(message.chat.id, text.read())
    with open('Соединение городов c поперечной связью.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    with open('Соединение городов c поперечной связью.txt', encoding='utf8') as text:
        bot.send_message(message.chat.id, text.read())
    with open('Пути.txt', encoding='utf8') as text:
        bot.send_message(message.chat.id, text.read())


if __name__ == '__main__':
    bot.infinity_polling(timeout=100, long_polling_timeout=50)
