from three import get_way, calculate_cost_ring
from first_part import create_xlsx_report


def attenuation_and_dispersion(cities, bot, message):
    cities = [city.split() for city in cities[:-1]]
    cities_names = [city[0] for city in cities]
    lambdas = [city[1:] for city in cities][0]
    lambdas = [int(x) for x in lambdas]
    lambdas.sort()
    way, matrix = get_way(cities_names)
    connecting_city = way[-1]
    connecting_city_index = way.index(connecting_city)
    first_ring = way[1:connecting_city_index + 1]
    first_ring.append(0)
    second_ring = way[connecting_city_index:-2]
    second_ring.append(0)
    # first_ring = [1, 2, 3, 4, 5, 6, 7, 0]
    # second_ring = [7, 8, 9, 10, 11, 0]

    first_ring_cities = []
    for index, element in enumerate(first_ring[:-1]):
        first_ring_cities.append({
            'city': cities_names[first_ring[index]],
            'city_to': cities_names[first_ring[index + 1]],
            'lambdas': lambdas,
            'distance': matrix[first_ring[index]][first_ring[index + 1]],
        })

    second_ring_cities = []
    for index, element in enumerate(second_ring[:-1]):
        second_ring_cities.append({
            'city': cities_names[second_ring[index]],
            'city_to': cities_names[second_ring[index + 1]],
            'lambdas': lambdas,
            'distance': matrix[second_ring[index]][second_ring[index + 1]],
        })

    first_ring_city = {
        'city': cities_names[0],
        'city_to': cities_names[first_ring[0]],
        'lambdas': lambdas,
        'distance': matrix[0][first_ring[0]],
    }

    second_ring_city = {
        'city': cities_names[0],
        'city_to': cities_names[second_ring[0]],
        'lambdas': lambdas,
        'distance': matrix[0][second_ring[0]],
    }

    context = {
        "lambdas": lambdas,
        "first_ring_cities": first_ring_cities,
        "second_ring_cities": second_ring_cities,
        "first_ring_city": first_ring_city,
        "second_ring_city": second_ring_city,
    }
    create_xlsx_report(context, "attenuation_and_dispersion_template.xlsx", "attenuation_and_dispersion.xlsx")
    bot.send_message(message.chat.id, f'Первое кольцо: {first_ring}')
    bot.send_message(message.chat.id, f'Второе кольцо: {second_ring}')
    with open('attenuation_and_dispersion.xlsx', 'rb') as file:
        bot.send_document(message.chat.id, file)
