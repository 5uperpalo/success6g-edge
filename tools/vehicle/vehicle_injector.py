import argparse
import time
import redis
from src.csv_parser import proccess_csv
from src.data_handler import order_by_ts_relative

REDIS_PASSWORD = "Success6G&Idneo"
REDIS_PORT = 55008
#REDIS_PORT = 63790


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process a CSV dataset file')
    parser.add_argument('-f', '--file', required=True, help='Path to CSV file')

    # arguments... (file dataset)
    args = parser.parse_args()

    # Pre-process csv dataset
    data_ordered_by_sensor = proccess_csv(args.file)

    # Timestamp sorting
    data_ordered_by_time = order_by_ts_relative(data_ordered_by_sensor)

    # Redis client connectivity
    redisClient = redis.Redis(host="127.0.0.1", password=REDIS_PASSWORD, port=REDIS_PORT)
    database = redisClient.ts()


    # creating Sensors in database if dont exist
    for sensor in data_ordered_by_sensor:

        try:
            database.info(sensor["sensor"])
        except redis.exceptions.ConnectionError as connection_error:
            raise SystemExit(connection_error)
        except redis.exceptions.RedisError as e:
            database.create(sensor["sensor"], labels={"type": "can_bus"})

    timestamp_start = time.time()
    relative_timestamp_start = 0

    # iteration of dataset
    for data_sample in data_ordered_by_time:
        # delta from dataset
        delta_timestamp = float(list(data_sample.keys())[0])
        # delta of data injection
        delay_of_next_data = round(delta_timestamp - relative_timestamp_start, 2)
        time.sleep(delay_of_next_data)

        relative_timestamp_start = delta_timestamp
        timestamp_epoch_ms = round(timestamp_start + delta_timestamp, 3)
        injection_timestamp = int(timestamp_epoch_ms * 1e3)

        info = data_sample[delta_timestamp]
        print(timestamp_epoch_ms, "Inserting", info['sensor'], info['value'], )
        database.add(info['sensor'], injection_timestamp, info['value'])
