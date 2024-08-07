import kserve
import dill
from inference_model.config import LOGGING_CONFIG
import logging

logging.config.dictConfig(LOGGING_CONFIG)


if __name__ == "__main__":
    # TODO - it might help the readability to implement this in the load method:
    # https://github.com/kserve/kserve/blob/c080da5f54349d1547c8583df6e2b9bad1d11ba6/python/kserve/kserve/model.py#L246
    file_loc = "/app/lgbm_trainer.dill"
    with open(file_loc, "rb") as f:
        trainer = dill.load(f)
    trainer._set_production_env()
    kserve.ModelServer(workers=1).start([trainer])
