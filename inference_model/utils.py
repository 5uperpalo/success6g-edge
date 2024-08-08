from typing import Any, Union
from pathlib import Path
import redis
from influxdb_client import Point, InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import dill
import os
import pandas as pd


def intsec(list1: list, list2: list) -> list:
    """Simple intesection of two lists.
    Args:
        list1 (list): list1
        list2 (list): list2
    Returns:
        list (list): intersection of lists
    """
    return list(set.intersection(set(list1), set(list2)))


def dill_load(file_loc: Union[str, Path]) -> Any:
    """Helper function to open/close dill file,
    otherwise the python outputs warning that the file remains opened

    Args:
        file_loc (str): location of the file
    Returns:
        content (dict): content of dill file, usually dictionary
    """
    with open(file_loc, "rb") as f:
        content = dill.load(f)
    return content


def dill_dump(file_loc: Union[str, Path], content: object):
    """Helper function to open/close dill file and dump content into it,
    otherwise the python outputs warning that the file remains opened

    Args:
        file_loc (str): location of the file
        content (object): data that will be saved to dill, usually dictionary
    """
    with open(file_loc, "wb") as f:
        dill.dump(content, f)


def set_production_env():
    INFLUXDB_HOST = os.getenv("INFLUXDB_HOST", "localhost")
    INFLUXDB_PORT = os.getenv("INFLUXDB_PORT", "80")
    INFLUXDB_USER = os.getenv("INFLUXDB_USER", "default_value")
    INFLUXDB_PASS = os.getenv("INFLUXDB_PASS", "default_value")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")
    REDIS_PASS = os.getenv("REDIS_PASS", "redis")

    redisClient = redis.Redis(
        host=REDIS_HOST, password=REDIS_PASS, port=int(REDIS_PORT)
    )

    # create influxdb API object
    influxdbClient = InfluxDBClient(
        url=f"http://{INFLUXDB_HOST}:{INFLUXDB_PORT}",
        username=INFLUXDB_USER,
        password=INFLUXDB_PASS,
        # TODO make a non-default org
        org="influxdata",
    )
    write_api = influxdbClient.write_api(write_options=SYNCHRONOUS)

    # Subscribe to the "idneo_v2x" channel
    pubsub = redisClient.pubsub()
    pubsub.subscribe("idneo_v2x")

    return pubsub, write_api


def handle_redis_message(message):
    """Handle Redis channel messages:
    1. decode messages from Redis channel
    2. make a prediction
    3. convert pandas rows to influxdb points
    4. write into the influxdb
    """
    # Convert the message data (bytes) to string
    json_data = message["data"].decode("utf-8")

    # Convert JSON string to DataFrame
    df = pd.read_json(json_data, orient="split")
    return df


def df_row_to_influxdb_point(row) -> Point:
    """Function to convert a DataFrame row to an InfluxDB Point"""
    # TODO vehicle_id and timestamp column have to be specified in some config file
    return (
        Point("prediction")
        .tag("vehicle_id", row["vehicle_id"])
        .field("value", row["class"])
        .time(row["timestamp"])
    )
