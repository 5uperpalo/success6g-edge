import csv
from .data_handler import order_by_sensor


def process_line_sensors_name(line):
    sensors_list = list()
    for value in line:
        if value != '' and value != 'STAMP':
            sensors_list.append(value)
    return sensors_list


def process_line_sensors_units(line):
    units_list = list()
    for value in line:
        if value != '':
            units_list.append(value)
    return units_list


def proccess_csv(file):
    with open(file, newline='', encoding='utf-8', errors='replace') as csvfile:
        csv_reader_obj = csv.reader(csvfile)

        # Iterar a partir de la línea especificada
        sensors = list()
        units = list()
        data = list()
        for fila in csv_reader_obj:
            if csv_reader_obj.line_num == 1:
                sensors = process_line_sensors_name(fila)
                print(sensors)
            elif csv_reader_obj.line_num == 2:
                units = process_line_sensors_units(fila)
            elif csv_reader_obj.line_num >= 3:
                data.append(fila)

        data = order_by_sensor(sensors, units, data)
        return data
