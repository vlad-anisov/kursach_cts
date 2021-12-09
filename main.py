import telebot

from three import get_map
from first_part import first_part
from attenuation_and_dispersion import attenuation_and_dispersion

# TOKEN = '2102086086:AAE0pb2tUNuwxSu7dSL11a7tromtIM3t4jo'
TOKEN = '5082082655:AAHrdIQgPm8dvDae9_SIAZ4MRq900OSlLKQ'

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    message_text = 'Привет! Я бот, который поможет в проектировании внутризоновой сети области РБ. ' \
                   'Отправьте мне сообщение в котором перечислено от 4 до 12 городов через запятую. ' \
                   'Первым городом должен быть административный центр области. ' \
                   'Пример: Минск, Воложин, Дзержинск, Копыль, Клецк, Крупки, Логойск, Любань, Молодечно, Мядель, Несвиж, Смолевичи. ' \
                   'Если что-то идёт не так, напишите создателю бота @anisov1337 и он попробует починить проблему.'
    bot.send_message(message.chat.id, message_text)


@bot.message_handler(commands=['help'])
def start_message(message):
    message_text = 'Привет! Я бот, который поможет в проектировании внутризоновой сети области РБ. ' \
                   'Отправьте мне сообщение в котором перечислено от 4 до 12 городов через запятую. ' \
                   'Первым городом должен быть административный центр области. ' \
                   'Пример: Минск, Воложин, Дзержинск, Копыль, Клецк, Крупки, Логойск, Любань, Молодечно, Мядель, Несвиж, Смолевичи. ' \
                   'Если что-то идёт не так, напишите создателю бота @anisov1337 и он попробует починить проблему.'
    bot.send_message(message.chat.id, message_text)


@bot.message_handler(content_types=['text'])
def start_message(message):
    # cities = message.text.split(",")
    # cities = [city.strip() for city in cities]
    # first_part(cities, bot, message)
    # get_map(cities, cities, bot, message)
    try:
        cities = message.text.split(",")
        cities = [city.strip() for city in cities]
        cities = [city[:-1] if city[-1] == '.' else city for city in cities]
        if len(cities) == 13:
            attenuation_and_dispersion(cities, bot, message)
            return
        if len(cities) < 4 or len(cities) > 12:
            bot.send_message(message.chat.id, f'Должно быть от 4 до 12 городов, а вы ввели {len(cities)}')
            return
        if len(cities) >= 4 or len(cities) <= 12:
            first_part(cities, bot, message)
            get_map(cities, cities, bot, message)
            return

    except Exception as e:
        bot.send_message(message.chat.id, f'Что-то пошло не так: {e}')


if __name__ == '__main__':
    bot.infinity_polling(timeout=100, long_polling_timeout=50)
