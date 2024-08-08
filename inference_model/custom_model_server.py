import dill
from inference_model.config import LOGGING_CONFIG
from inference_model.utils import handle_redis_message, df_row_to_influxdb_point, set_production_env
import logging

logging.config.dictConfig(LOGGING_CONFIG)

        
if __name__ == "__main__":
    file_loc = "/app/lgbm_trainer.dill"
    with open(file_loc, "rb") as f:
        trainer = dill.load(f)

    pubsub, write_api = set_production_env()

    for message in pubsub.listen():
        if message["type"] == "message":
            try:
                df = handle_redis_message(message)

                preds = trainer.predict(df)

                # make and write points to influxdb 
                # TODO make a non-default bucket
                points = [
                    df_row_to_influxdb_point(row) for index, row in preds.iterrows()
                ]
                write_api.write(bucket="default", record=points)
            except Exception as e:
                print(f"Error processing message: {e}")

