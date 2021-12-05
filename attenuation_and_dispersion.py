from three import get_way, calculate_cost_ring

def attenuation_and_dispersion(cities, bot, message):
    cities = [city.split() for city in cities[:-1]]
    cities = [city[0] for city in cities]
    way, matrix = get_way(cities)
    connecting_city = way[-1]
    connecting_city_index = way.index(connecting_city)
    first_ring = way[:connecting_city_index]
    second_ring = way[connecting_city_index:-1]
    bot.send_message(message.chat.id, f'Первое окружность: {first_ring}')
    bot.send_message(message.chat.id, f'Второе окрушность: {second_ring}')