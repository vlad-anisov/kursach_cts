import math

from openpyxl import load_workbook
from xltpl.writerx import BookWriter
import erlang
import formulas


def first_part(cities, bot, message):
    number_of_cities = len(cities)
    data = get_data(cities)
    write_cities_data(data)
    write_erlang_data(number_of_cities)
    delete_first_city_from_first_table(number_of_cities)
    with open('first_table.xlsx', 'rb') as file:
        bot.send_document(message.chat.id, file)

    write_second_data(data)
    delete_first_city_from_second_table(number_of_cities)
    with open('second_table.xlsx', 'rb') as file:
        bot.send_document(message.chat.id, file)


def get_data(cities):
    wb = load_workbook("cities.xlsx")
    sheet = wb.worksheets[0]
    data = []
    for city in cities:
        data.append(get_city_data(city, sheet))
    return data


def write_second_data(data_of_cities):
    rows = list(map(list, zip(*data_of_cities)))
    cities = rows[0]
    population_sizes = [float(item.replace(",", ".")) for sublist in list(zip(rows[1], rows[2])) for item in sublist]
    norms_of_telephone_density = get_norms_of_telephone_density(population_sizes)
    number_of_people = get_number_of_people(population_sizes, norms_of_telephone_density)
    context = {
        "cities": cities,
        "population_sizes": number_of_people,
    }
    create_xlsx_report(context, "template_2.xlsx", "second_table.xlsx")


def get_number_of_people(population_sizes, norms_of_telephone_density):
    number_of_people = []
    for i in range(len(population_sizes)):
        number = math.ceil(population_sizes[i] * norms_of_telephone_density[i] * 0.92)
        number_of_people.append(number)
    return number_of_people


def delete_first_city_from_first_table(number_of_cities):
    wb = load_workbook("first_table.xlsx")
    sheet = wb.worksheets[0]
    for i in range(1, sheet.max_row + 1):
        if i in [3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17]:
            sheet.cell(row=i, column=3).value = "-"
    sheet.delete_cols(number_of_cities * 2 + 3, 30)
    wb.save("first_table.xlsx")


def delete_first_city_from_second_table(number_of_cities):
    wb = load_workbook("second_table.xlsx")
    sheet = wb.worksheets[0]
    for i in range(1, sheet.max_row + 1):
        if i in [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17]:
            sheet.cell(row=i, column=3).value = "-"
    sheet.delete_cols(number_of_cities * 2 + 3, 30)
    wb.save("second_table.xlsx")


def write_erlang_data(number_of_cities):
    xl_model = formulas.ExcelModel().loads("first_table.xlsx").finish()
    xl_model.calculate()
    xl_model.write(dirpath="calculate")
    wb = load_workbook("first_table.xlsx")
    sheet = wb.worksheets[0]
    wb2 = load_workbook("calculate/FIRST_TABLE.XLSX")
    sheet2 = wb2.worksheets[0]
    for i in range(1, sheet.max_row + 1):
        if i in [11, 15]:
            for j in range(3, number_of_cities * 2 + 3):
                erlang_value = float(sheet2.cell(i - 1, j).value)
                sheet.cell(row=i, column=j).value = erlang.extended_b_lines(erlang_value, 0.01)
        if i in [3, 6]:
            for j in range(3, number_of_cities * 2 + 3):
                # sheet.cell(row=i, column=j).value = format(float(sheet2.cell(i, j).value), '.3f').replace('.', ',')
                sheet.cell(row=i, column=j).value = float(sheet2.cell(i, j).value)
        # if i == 6:
        #     for j in range(3, 27):
        #         sheet.cell(row=i, column=j).value = f'{sheet2.cell(i, j).value}00'
        # if i == 3:
        #     for j in range(3, 27):
        #         sheet.cell(row=i, column=j).value = f'{sheet2.cell(i, j).value}00'
    wb.save("first_table.xlsx")


def get_city_data(city, sheet):
    data = [city]
    for i in range(1, sheet.max_row + 1):
        value = sheet.cell(i, 1).value
        if value and value.lower() in [f'??.{city}'.lower(), f'??.??.{city}'.lower()]:
            data.append(0)
            # for j in range(1, 10):
            #     if sheet.cell(i - j, 1).value == '?????????????????? ??????????????????':
            #         value = str(format(sheet.cell(i - j, 4).value / 1000, '.3f')).replace('.', ',')
            #         data[1] = value
            #         break
            value = str(format(sheet.cell(i, 4).value / 1000, '.3f')).replace('.', ',')
            data[1] = value
            data.append(0)
            for j in range(1, 10):
                if sheet.cell(i + j, 1).value == '???????????????? ??????????????????':
                    value = str(format(sheet.cell(i + j, 4).value / 1000, '.3f')).replace('.', ',')
                    data[2] = value
                    break
            break
    return data


def write_cities_data(data_of_cities):
    rows = list(map(list, zip(*data_of_cities)))
    cities = rows[0]
    population_sizes = [float(item.replace(",", ".")) for sublist in list(zip(rows[1], rows[2])) for item in sublist]
    context = {
        "cities": cities,
        "population_sizes": population_sizes,
        "norms_of_telephone_density": get_norms_of_telephone_density(population_sizes),
        "number_of_subscribers": get_number_of_subscribers(population_sizes),
    }
    create_xlsx_report(context, "template_1.xlsx", "first_table.xlsx")


def create_xlsx_report(context, template_path, file_name):
    """Creating xlsx report"""
    writer = BookWriter(template_path)
    context["sheet_name"] = "sheet"
    writer.render_book(payloads=[context])
    writer.save(file_name)


def get_norms_of_telephone_density(population_sizes):
    norms_of_telephone_density = []
    for index, size in enumerate(population_sizes, 1):
        if index % 2 == 0:
            norms_of_telephone_density.append(150)
        else:
            if 1 <= size < 10:
                norms_of_telephone_density.append(215)
            elif 10 <= size < 20:
                norms_of_telephone_density.append(255)
            elif 20 <= size < 50:
                norms_of_telephone_density.append(290)
            elif 50 <= size < 100:
                norms_of_telephone_density.append(320)
            elif 100 <= size < 500:
                norms_of_telephone_density.append(370)
            else:
                norms_of_telephone_density.append(415)
    return norms_of_telephone_density


def get_number_of_subscribers(population_sizes):
    norms_of_telephone_density = []
    for index, size in enumerate(population_sizes, 1):
        if index % 2 == 0:
            norms_of_telephone_density.append(0.12)
        else:
            if 1 <= size < 10:
                norms_of_telephone_density.append(0.7)
            elif 10 <= size < 20:
                norms_of_telephone_density.append(0.7)
            elif 20 <= size < 50:
                norms_of_telephone_density.append(0.6)
            elif 50 <= size < 100:
                norms_of_telephone_density.append(0.5)
            elif 100 <= size < 500:
                norms_of_telephone_density.append(0.4)
            else:
                norms_of_telephone_density.append(0.3)
    return norms_of_telephone_density
