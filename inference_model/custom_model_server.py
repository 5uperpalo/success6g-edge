import kserve
from inference_model.training.trainer import S6GTrainer

if __name__ == "__main__":
    # TODO - it might hel the readability to implement this in the load method:
    # https://github.com/kserve/kserve/blob/c080da5f54349d1547c8583df6e2b9bad1d11ba6/python/kserve/kserve/model.py#L246
    trainer = dill_load("lgbm_trainer.dill")
    trainer._set_production_env()
    kserve.ModelServer(workers=1).start([trainer])