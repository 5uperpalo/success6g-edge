from typing import Any, Dict, List, Union, Literal, Optional

import pandas as pd

from inference_model.utils import intsec
from inference_model.training._base import BaseTrainer, BaseOptimizer
from inference_model.training.utils import to_lgbdataset
from inference_model.preprocessing.preprocess import PreprocessData
from inference_model.training._lgb_train_function import lgb_train_function
import kserve
import os
import redis
from influxdb_client import Point, InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# Get the env value and if not present, set default
INFLUXDB_HOST = os.getenv("INFLUXDB_HOST", "localhost")
INFLUXDB_PORT = os.getenv("INFLUXDB_PORT", "80")
INFLUXDB_USER = os.getenv("INFLUXDB_USER", "default_value")
INFLUXDB_PASS = os.getenv("INFLUXDB_PASS", "default_value")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_PASS = os.getenv("REDIS_PASS", "redis")


class Trainer(BaseTrainer):
    def __init__(
        self,
        cat_cols: List[str],
        target_col: str,
        id_cols: List[str],
        objective: Literal["binary"],
        optimizer: Union[Any, BaseOptimizer, None] = None,
        n_class: Optional[int] = None,
        preprocessors: Optional[List[Union[Any, PreprocessData]]] = None,
    ):
        """Objects that governs training and parameter optimization of the lgbm model.

        Args:
            cat_cols (list): list of categorical feature column names
            target_col (str): column name that represents target
            id_cols (list): identification column names
            objective (str): type of the task/objective
            optimizer (BaseOptimizer): parameter optimizer object
            n_class (int): number of classes in the dataset
            preprocessors (List[Union[Any, PreprocessData]]):
                ordered list of objects to preprocess dataset before optimization
                and training
        """
        super(Trainer, self).__init__(
            cat_cols=cat_cols,
            target_col=target_col,
            id_cols=id_cols,
            objective=objective,
            n_class=n_class,
            preprocessors=preprocessors,
        )
        if optimizer is not None:
            if not hasattr(optimizer, "optimize"):
                raise AttributeError(
                    "{} optimizer must have {} method".format(optimizer, "optimize")
                )
        self.optimizer = optimizer

    def train(
        self,
        df_train: pd.DataFrame,
        params: Optional[Dict] = None,
        df_valid: Optional[pd.DataFrame] = None,
    ):
        """Train the model with the parameters.

        Args:
            df_train (pd.DataFrame): training dataset
            params (dict): model paramaters
            df_valid (pd.DataFrame): optional validation dataset
        Returns:
            model (lgb.basic.Booster): trained model
        """
        if self.preprocessors:
            for prep in self.preprocessors:
                df_train_prep = prep.transform(df_train.drop(columns=[self.target_col]))
                df_valid_prep = (
                    prep.transform(df_valid.drop(columns=[self.target_col]))
                    if df_valid is not None
                    else None
                )
            if self.objective in ["binary"]:
                df_train_prep[self.target_col] = df_train[self.target_col].astype(int)
                if df_valid is not None:
                    df_valid_prep[self.target_col] = df_valid[self.target_col].astype(
                        int
                    )
            else:
                raise NotImplementedError
        else:
            df_train_prep = df_train.copy()
            df_valid_prep = df_valid.copy() if df_valid is not None else None

        cat_cols = self.cat_cols
        if params:
            config = params
        elif (params is None) and (self.optimizer):
            config = self.optimizer.best
            if hasattr(self.optimizer, "best_to_drop"):
                df_train_prep.drop(
                    columns=self.optimizer.best_to_drop,  # type: ignore
                    inplace=True,
                )
                if df_valid is not None:
                    df_valid_prep.drop(
                        columns=self.optimizer.best_to_drop,  # type: ignore
                        inplace=True,
                    )
                cat_cols = intsec(self.cat_cols, df_train_prep.columns.values)

        elif (params is None) and (self.optimizer is None):
            config = self.base_params

        lgb_train, lgb_valid = to_lgbdataset(
            train=df_train_prep,
            cat_cols=cat_cols,
            target_col=self.target_col,
            id_cols=self.id_cols,
            valid=df_valid_prep,
        )

        self.model = lgb_train_function(
            config=config,
            lgbtrain=lgb_train,
            lgbeval=lgb_valid,
            feval=self.feval,
        )

    def predict(
        self,
        df: Union[pd.DataFrame, dict],
        context: Optional[dict] = None,
        raw_score: bool = False,
    ):
        return self.predict_default(
            df=df,
            raw_score=raw_score,
        )

    def fit(
        self,
        df_train: pd.DataFrame,
        df_valid: pd.DataFrame,
        df_test: pd.DataFrame,
        random_state: int = 1,
    ) -> pd.DataFrame:
        """Train the model and optimize the parameters.

        Args:
            df_train (pd.DataFrame): training dataset
            df_valid (pd.DataFrame): validation dataset
            df_test (pd.DataFrame): testing dataset
        Returns:
            model (lgb.basic.Booster): trained mdoel
        """
        if self.preprocessors:
            # this should be
            # df_train_prep = prep.transform(df_train_prep.drop(columns=[self.target_col]))
            for prep in self.preprocessors:
                df_train_prep = prep.transform(df_train.drop(columns=[self.target_col]))
                df_valid_prep = prep.transform(df_valid.drop(columns=[self.target_col]))
            if self.objective in ["binary"]:
                df_train_prep[self.target_col] = df_train[self.target_col].astype(int)
                df_valid_prep[self.target_col] = df_valid[self.target_col].astype(int)
            else:
                raise NotImplementedError
        else:
            df_train_prep = df_train.copy()
            df_valid_prep = df_valid.copy()

        lgb_train, lgb_valid = to_lgbdataset(
            train=df_train_prep,
            cat_cols=self.cat_cols,
            target_col=self.target_col,
            id_cols=self.id_cols,
            valid=df_valid_prep,
        )
        self.optimizer.optimize(dtrain=lgb_train, deval=lgb_valid)

        df_train_valid = pd.concat([df_train, df_valid], ignore_index=True)
        df_train_valid = df_train_valid.reset_index(drop=True)
        self.train(df_train=df_train_valid)
        metrics_dict = self.compute_metrics(df_test)
        return metrics_dict


class S6GTrainer(Trainer, kserve.Model):
    def __init__(
        self,
        cat_cols: List[str],
        target_col: str,
        id_cols: List[str],
        objective: Literal["binary"],
        name: str = "S6GTrainer",
        optimizer: Union[Any, BaseOptimizer, None] = None,
        n_class: Optional[int] = None,
        preprocessors: Optional[List[Union[Any, PreprocessData]]] = None,
    ):
        """Extension of the Trainer object. SUCCESS6G project requires
        subscription to an edge-Redis db channel to ingest the data, and
        directly forward of the predictions to a central Influx
        database. Both Redis and InfluxDB are socket objects which cause
        issues with MLflow with the following error:
        'Full serialization error: cannot pickle 'socket' object'

        Workaround:
        Create a custom Kserve model:
        https://kserve.github.io/website/master/modelserving/v1beta1/custom/custom_model/#implement-custom-model-using-kserve-api

        Args:
            cat_cols (list): list of categorical feature column names
            target_col (str): column name that represents target
            id_cols (list): identification column names
            objective (str): type of the task/objective
            name (str): required by Kserve model
            optimizer (BaseOptimizer): parameter optimizer object
            n_class (int): number of classes in the dataset
            preprocessors (List[Union[Any, PreprocessData]]):
                ordered list of objects to preprocess dataset before optimization
                and training
        """
        super(S6GTrainer, self).__init__(
            cat_cols=cat_cols,
            target_col=target_col,
            id_cols=id_cols,
            objective=objective,
            n_class=n_class,
            optimizer=optimizer,
            preprocessors=preprocessors,
        )
        self._set_production_env()

    def _set_production_env(self):
        try:
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
            self.write_api = influxdbClient.write_api(write_options=SYNCHRONOUS)

            # Subscribe to the "idneo_v2x" channel
            pubsub = redisClient.pubsub()
            pubsub.subscribe(**{"idneo_v2x": self._handle_redis_message})

            # Wait for messages
            pubsub.run_in_thread(sleep_time=1)
            # used in kserve.Model as healthcheck: https://github.com/kserve/kserve/blob/c080da5f54349d1547c8583df6e2b9bad1d11ba6/python/kserve/kserve/model.py#L59
            self.ready = True
        except Exception:
            self.ready = False
            logging.error("An error occurred", exc_info=True)

    def _handle_redis_message(self, message):
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

        self.predict(df)

    def _df_row_to_influxdb_point(self, row) -> Point:
        """Function to convert a DataFrame row to an InfluxDB Point"""
        # TODO vehicle_id and timestamp column have to be specified in some config file
        return (
            Point("prediction")
            .tag("vehicle_id", row["vehicle_id"])
            .field("value", row["class"])
            .time(row["timestamp"])
        )

    def predict(self, df: Union[pd.DataFrame, dict], raw_score: bool = False):
        preds = self.predict_default(
            df=df,
            raw_score=raw_score,
        )
        if self.ready:            
            # Convert DataFrame to InfluxDB Points and write
            points = [
                self._df_row_to_influxdb_point(row) for index, row in preds.iterrows()
            ]
    
            # Write points to 
            # TODO make a non-default bucket
            self.write_api.write(bucket="default", record=points)
        else:
            return preds
