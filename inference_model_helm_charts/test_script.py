import os
import sys
import pandas as pd
import ast
import time
import redis


sys.path.append(os.getcwd())
os.chdir("../..")
os.environ["REDIS_PASSWORD"] = "redis"
os.environ["REDIS_HOST"] = "10.17.7.158"
os.environ["REDIS_PORT"] = "17935"

# ssh -L 3000:localhost:3000 fog_user@10.17.252.101
# kubectl port-forward svc/influx-influxdb2 -n influx 3000:80
# browser http://localhost:3000/ ; admin/admin_pass


def load_new_dataset(num: int):
    data_sets = [
        "DS1_stopped_with_ignition_on_22Feb24_115812.csv",
        "DS1_stopped_with_ignition_on_25Jan24_124019.csv",
        "DS1_stopped_with_ignition_on_25Jan24_151531.csv",
        "DS1_stopped_with_ignition_on_25Mar24_153740.CSV",
        "DS2_national_road_90km_h_max_25Jan24_153019.csv",
        "DS2_national_road_90km_h_max_25Mar24_133516.CSV",
        "DS3_highway_120km_h_max_22Feb24_121145.csv",
        "DS3_highway_120km_h_max_25Mar24_154857.csv"
    ]
    file = "tools/vehicle/datasets/ateca_R4_2.0l_TDI/" + data_sets[num]

    df = pd.read_csv(file)
    df.head()
    df.drop(columns=["Unnamed: 0", "Unnamed: 25"], inplace=True)
    df.drop(index=0, inplace=True)

    timestamp_columns = [col for col in df.columns if col.startswith("STAMP")]
    # keep only the first timestamp column
    df["timestamp"] = df["STAMP"]
    df = df.drop(columns=timestamp_columns)

    df["class"] = 0
    df["vehicle_id"] = "123abc"
    df.loc[:100, ["class"]] = 1
    df.loc[:100, ["Normed load value"]] = 100

    df[df.drop(columns=["class", "vehicle_id"]).columns] = df[df.drop(columns=["class", "vehicle_id"]).columns].astype(float)

    # Remove special characters from column names
    df.columns = df.columns.str.replace('[^A-Za-z0-9]+', '_', regex=True)

    # add some "reasonable" timestamp for testing
    df["timestamp"] = pd.to_datetime(time.time() - 3600 + df["timestamp"], unit="s")
    return df


def load_old_dataset():
    with open("data/log_tiguan_27_mar_dac.txt") as f:
        data = ast.literal_eval(f.read())

    df = pd.DataFrame()
    for data_value in data:
        temp_df = pd.DataFrame(data_value[list(data_value)[0]]).sort_values(
            by="ts_millis:", ascending=True
        )["value"]
        temp_df.rename(list(data_value)[0], inplace=True)
        df = pd.concat([df, temp_df], axis=1)

    df.dropna(inplace=True)
    df["class"] = 0
    df["vehicle_id"] = "123abc"
    df.loc[:100, ["class"]] = 1
    df.loc[:100, ["engine_load"]] = 100

    # add some "reasonable" timestamp for testing
    df["timestamp"] = pd.to_datetime([time.time() - 3600 + ix for ix in list(df.index)], unit="s")
    return df


# df_pd = load_old_dataset()
df_pd = load_new_dataset(num=1)

target_col = "class"
id_cols = ["vehicle_id", "timestamp"]
cat_cols = []
cont_cols = df_pd.drop(
    columns=id_cols + cat_cols + [target_col]
).columns.values.tolist()
df_pd[cat_cols] = df_pd[cat_cols].astype(str)


df_test_redis = df_pd.copy()
# df_test_redis["timestamp"] -= pd.to_timedelta(1, unit="h")
df_test_redis_json = df_test_redis.drop(columns=["class"]).reset_index(drop=True).to_json(orient="split")
redisClient = redis.Redis(host=os.environ["REDIS_HOST"], password=os.environ["REDIS_PASSWORD"], port=os.environ["REDIS_PORT"])
redisClient.publish("idneo_v2x", df_test_redis_json)
