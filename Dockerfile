FROM python:3.10-slim

# fix for dill error:
# "OSError: libgomp.so.1: cannot open shared object file: No such file or directory"
RUN apt-get update && apt-get install -y libgomp1 && apt-get clean

COPY inference_model/ /app/inference_model/
COPY requirements.txt /app/requirements.txt
COPY data/lgbm_trainer.dill /app/lgbm_trainer.dill
COPY setup.py /app/setup.py

# for testing purposes
ENV REDIS_PASSWORD redis
ENV REDIS_HOST 10.152.183.250
ENV REDIS_PORT 6379
ENV INFLUXDB_HOST 10.152.183.219
ENV INFLUXDB_PORT 80
ENV INFLUXDB_USER admin
ENV INFLUXDB_PASS admin_pass

#WORKDIR /app

RUN pip install -r /app/requirements.txt
RUN pip install /app/.


CMD ["python", "/app/inference_model/dummy_script.py"]