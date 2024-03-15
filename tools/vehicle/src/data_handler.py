

def order_by_sensor(sensors, units, dataset):
    results = []
    first_seconds_delay = None
    iterator = 1
    for sensor, unit in zip(sensors, units):

        datos_sensor = []
        for values in dataset:

            # skipping the first seconds..
            if first_seconds_delay is None:
                first_seconds_delay = int(float(values[iterator]))
                print("Dataset has begun after ", first_seconds_delay, "seconds...")
                continue

            datos_sensor.append(
                {'ts_relative': float(values[iterator]) - first_seconds_delay,
                 'value': float(values[iterator + 1])}
            )
        iterator = iterator + 2


        # a new dict for every sensor
        sensor_result = {'sensor': sensor.replace(' ', '_'), 'unit': unit, 'values': datos_sensor}

        results.append(sensor_result)

    return results


def order_by_ts_relative(input_data):
    #  tuples (ts_relative, sensor, value)
    flattened_data = [(entry['values'][i]['ts_relative'], entry['sensor'], entry['values'][i]['value'])
                      for entry in input_data
                      for i in range(len(entry['values']))]

    sorted_data = sorted(flattened_data, key=lambda x: x[0])

    output_json = [
        {ts_relative: {"sensor": sensor, "value": value}}
        for ts_relative, sensor, value in sorted_data
    ]

    return output_json
