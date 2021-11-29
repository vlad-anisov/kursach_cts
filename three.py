import random
import copy

import geocoder
import requests
from urllib.request import urlretrieve
from urllib.parse import quote
from geopy.geocoders import Nominatim
from tsp import atsp
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path
import pandas as pd
import dataframe_image as dfi
import numpy as np
from python_tsp.exact import solve_tsp_dynamic_programming
from tsp_solver.greedy import solve_tsp


MAPBOX_KEY = 'pk.eyJ1IjoiYW5pc292IiwiYSI6ImNrMm90Mm1sZTEzZGwzbmxubHlpanVwbnUifQ.pqzxDULrQBz-arhWo8BaKA'

city_to_coordinates = {}


def write_matrix(matrix):
    with open("Матрица расстояний.txt", "w+", encoding="utf-8") as file:
        for row in matrix:
            row = '\t'.join(list(map(str, row)))
            row = row.replace("inf", "100000")
            file.write(row + '\n')


def calculate_cost_ring(way, matrix):
    cost = 0
    for i in range(len(way[:-1])):
        m = way[i]
        n = way[i + 1]
        cost += matrix[m][n]
    return int(cost)


def search_for_city_with_distance_of_more_than_280_km(way, matrix):
    # first_city = get_city_with_distance_of_more_than_280_km(way[::-1], matrix)
    # second_city = get_city_with_distance_of_more_than_280_km(way, matrix)
    # first_city_index = way.index(first_city)
    # second_city_index = way.index(second_city)
    # new_way = way[first_city_index:second_city_index + 1]
    # added_city = None
    # added_cost = float("inf")
    # for city in new_way:
    #     if matrix[0][city] < added_cost:
    #         added_city = city
    #         added_cost = matrix[0][city]
    # return added_city, added_cost
    min_cost = float("inf")
    min_city = None
    for city in way[2:-2]:
        new_way = list(way)
        new_way.append(city)
        max_cost = get_max_path_from_first_to_each_cities(matrix, new_way)
        if max_cost < 280:
            cost = matrix[0][city]
            if cost < min_cost:
                min_cost = cost
                min_city = city
    return min_city, min_cost


def get_city_with_distance_of_more_than_280_km(way, matrix):
    cost = 0
    first_city = None
    for i in range(len(way[:-1])):
        m = way[i]
        n = way[i + 1]
        cost += matrix[m][n]
        if cost > 280:
            first_city = n
            break

    first_city_index = way.index(first_city)
    new_way = way[first_city_index:]
    cost = 0
    for i in range(len(new_way[:-1])):
        m = new_way[i]
        n = new_way[i + 1]
        cost += matrix[m][n]
        if cost + matrix[0][n] > 280:
            return n

def get_polyline(cities):
    start = city_to_coordinates[cities[0]]
    finish = city_to_coordinates[cities[-1]]

    directions = f'https://api.mapbox.com/directions/v5/mapbox/driving/{start};{finish}?access_token={MAPBOX_KEY}'
    response = requests.get(directions).json()
    polyline = response['routes'][0]['geometry']
    return quote(polyline)


def get_matrix(cities):
    cities_coordinates = ''
    for city in cities:
        cities_coordinates += f'{city_to_coordinates[city]};'

    url = f'https://api.mapbox.com/directions-matrix/v1/mapbox/driving/{cities_coordinates[:-1]}?annotations=distance&access_token={MAPBOX_KEY}'
    matrix = requests.get(url).json()['distances']
    for i in range(len(cities)):
        matrix[i][i] = 100000

    for i in range(len(cities)):
        for j in range(len(cities)):
            if i == j:
                continue
            matrix[i][j] = int(matrix[i][j] / 1000)

    for i in range(len(cities)):
        for j in range(len(cities)):
            matrix[i][j] = matrix[j][i]
    df = pd.DataFrame(matrix)
    df = df.astype('int', errors='ignore')
    df.index += 1
    df.columns += 1
    df = df.style.set_properties(**{'text-align': 'center'})
    df = df.set_table_styles([{'selector': '', 'props': [('border', '1px solid black')]}, {'selector': 'th', 'props': [('text-align', 'center')]}])
    dfi.export(df, 'matrix.png', table_conversion='matplotlib')
    return matrix


def print_map_ring(cities, original_cities, way, name, polyline=False):
    cities2 = []
    for index in way:
        cities2.append(cities[index])
    cities = cities2

    if polyline:
        polyline = ""
        for index, city in enumerate(cities[:-1]):
            start_city = cities[index]
            finish_city = cities[index + 1]
            new_line = get_polyline([start_city, finish_city])
            polyline += f'path-5+FF5721-0.5({new_line}),'

    markers = ""
    for index, city in enumerate(cities):
        number = original_cities.index(city) + 1
        markers += f"pin-l-{number}+000000({city_to_coordinates[city]}),"
    markers = markers[:-1]

    if polyline:
        url = f"https://api.mapbox.com/styles/v1/anisov/ck2otgw050fth1cqu9zrqxcdy/static/{polyline}{markers}/auto/1280x720@2x?access_token={MAPBOX_KEY}&logo=false"
    else:
        url = f"https://api.mapbox.com/styles/v1/anisov/ck2otgw050fth1cqu9zrqxcdy/static/{markers}/auto/1280x720@2x?access_token={MAPBOX_KEY}&logo=false"
    urlretrieve(url, f'{name}.png')


def get_polyline_mapbox(cities):
    start = city_to_coordinates[cities[0]]
    finish = city_to_coordinates[cities[-1]]

    directions = f'https://api.mapbox.com/directions/v5/mapbox/driving/{start};{finish}?access_token={MAPBOX_KEY}'
    response = requests.get(directions).json()
    polyline = response['routes'][0]['geometry']
    return polyline


def write_way_and_cost_ring(way, cost, name):
    with open(f'{name}.txt', "w+", encoding="utf-8") as file:
        file.write(f'Путь коммивояжера: {"-".join(list(map(lambda x: str(x + 1), way)))}\n')
        file.write(f'Протяжённость пути составила: {cost} км')


def write_way_and_cost_three(way, cost, name):
    with open(f'{name}.txt', "w+", encoding="utf-8") as file:
        way = list(map(lambda x: f'{x[0] + 1}-{x[1] + 1}', way))
        file.write(f'Путь коммивояжера: {" ".join(way)}\n')
        file.write(f'Протяжённость пути составила: {cost} км')


def create_new_matrix(matrix, way):
    matrix_len = len(matrix)
    inf = float('inf')
    new_matrix = [[inf for i in range(matrix_len)] for j in range(matrix_len)]
    for index in range(len(way) - 1):
        first_city = way[index]
        second_city = way[index + 1]
        new_matrix[first_city][second_city] = matrix[first_city][second_city]
        new_matrix[second_city][first_city] = matrix[second_city][first_city]
    return new_matrix


def remove_path_from_matrix(matrix, path):
    for i in range(len(path) - 1):
        first_city = path[i]
        second_city = path[i + 1]
        matrix[first_city][second_city] = float('inf')
        matrix[second_city][first_city] = float('inf')


def get_path(D, Pr, i, j):
    path = [j]
    k = j
    while Pr[i, k] != -9999:
        path.append(Pr[i, k])
        k = Pr[i, k]
    return path[::-1], D[i, j]


def calculate_path_from_first_to_each_cities(cities, matrix, way):
    new_matrix = create_new_matrix(matrix, way)
    graph = csr_matrix(new_matrix)
    way = set(way)
    way.remove(0)
    way = list(way)
    message = ""
    for city in way:
        D, Pr = shortest_path(graph, directed=False, method='FW', return_predecessors=True)
        path, cost = get_path(D, Pr, 0, city)
        number_path = " - ".join(list(map(lambda x: str(x + 1), path[::-1])))
        message += f'{cities[city]} - {cities[0]}\n\n'
        message += f'Основной путь:\n{number_path}\nРасстояние: {int(cost)} км.\n\n'
        alternative_matrix = copy.deepcopy(new_matrix)
        remove_path_from_matrix(alternative_matrix, path)
        alternative_graph = csr_matrix(alternative_matrix)
        D, Pr = shortest_path(alternative_graph, directed=False, method='FW', return_predecessors=True)
        path, cost = get_path(D, Pr, 0, city)
        number_path = " - ".join(list(map(lambda x: str(x + 1), path[::-1])))
        message += f'Резервный путь:\n{number_path}\nРасстояние: {int(cost)} км.\n\n\n\n'
    with open(f'Пути.txt', "w+", encoding="utf-8") as file:
        file.write(message)

def get_max_path_from_first_to_each_cities(matrix, way):
    new_matrix = create_new_matrix(matrix, way)
    graph = csr_matrix(new_matrix)
    way = set(way)
    way.remove(0)
    way = list(way)
    max_cost = 0
    for city in way:
        D, Pr = shortest_path(graph, directed=False, method='FW', return_predecessors=True)
        path, cost = get_path(D, Pr, 0, city)
        if cost > max_cost:
            max_cost = cost
    return max_cost

def update_coordinates(cities):
    global city_to_coordinates
    city_to_coordinates = {}
    for city in cities:
        user_agent = f"{random.randint(1, 1000)}fnkjsdnfjsndjsa_kursach_telegram_anisov{random.randint(1, 1000)}"
        geolocator = Nominatim(user_agent=user_agent)
        location = geolocator.geocode(f"{city}, Беларусь", timeout=100)
        # g = geocoder.geonames(name, country='BY', key='anisov')
        # print(g.population)
        city_to_coordinates[city] = f'{location.longitude},{location.latitude}'

def get_map(cities, original_cities, bot, telegram_message):
    # Обновляем словарь с координатами городов
    update_coordinates(cities)
    # Находим матрицу расстояний и записываем её в файл
    matrix = get_matrix(cities)
    with open('matrix.png', 'rb') as photo:
        bot.send_photo(telegram_message.chat.id, photo)
    # write_matrix(matrix)
    # with open('Матрица расстояний.txt', encoding='utf8') as text:
    #     bot.send_message(message.chat.id, text.read())

    # Рисуем расположение городов на карте
    # Если у нас метод ветвей и границ (кольцо), то мы сначала вычеслям путь, а потом рисуем пустую карту без путей
    # В остальных случаях (дерево) номера городов будут в том порядке, в котором были написаны
    # way = atsp(matrix)
    # way = solve_tsp(matrix, optim_steps=10000000000000000)
    distance_matrix = np.array(matrix)
    way = solve_tsp_dynamic_programming(distance_matrix)[0]
    way.append(0)
    print_map_ring(cities, original_cities, way, 'Расположение городов на карте', False)
    with open('Расположение городов на карте.png', 'rb') as photo:
        bot.send_photo(telegram_message.chat.id, photo)

    # Соединение городов первым способом
    # way = atsp(matrix)
    # way = solve_tsp(matrix, optim_steps=10000000000000000)
    cost = calculate_cost_ring(way, matrix)
    write_way_and_cost_ring(way, cost, 'Соединение городов методом ветвей и границ')
    print_map_ring(cities, original_cities, way, 'Соединение городов методом ветвей и границ', True)
    with open('Соединение городов методом ветвей и границ.png', 'rb') as photo:
        bot.send_photo(telegram_message.chat.id, photo)
    with open('Соединение городов методом ветвей и границ.txt', encoding='utf8') as text:
        bot.send_message(telegram_message.chat.id, text.read())

    added_city, added_cost = search_for_city_with_distance_of_more_than_280_km(way, matrix)
    message = f"\nВведём дополнительную поперечную связь между городами {cities[0]} и {cities[added_city]} " \
              f"протяжённостью {added_cost} км."
    cost += added_cost
    way.extend([added_city])
    write_way_and_cost_ring(way, cost, f'Соединение городов c поперечной связью')
    with open(f'Соединение городов c поперечной связью.txt', "a", encoding="utf-8") as file:
        file.write(message)
    print_map_ring(cities, original_cities, way, f'Соединение городов c поперечной связью', True)
    with open('Соединение городов c поперечной связью.png', 'rb') as photo:
        bot.send_photo(telegram_message.chat.id, photo)
    with open('Соединение городов c поперечной связью.txt', encoding='utf8') as text:
        bot.send_message(telegram_message.chat.id, text.read())

    # Краткий путь от первого города до каждого
    calculate_path_from_first_to_each_cities(cities, matrix, way)
    with open('Пути.txt', encoding='utf8') as text:
        bot.send_message(telegram_message.chat.id, text.read())


if __name__ == '__main__':
    cities = input('Введите города через запятую: ').split(',')
    get_map(cities, cities)
