FROM python:3.10-slim

RUN pip install -r requirements.txt
COPY inference_model/custom_model_server.py /app/custom_model_server.py
COPY data/lgbm_trainer.dill /app/lgbm_trainer.dill

CMD ["python", "/app/custom_model_server.py"]