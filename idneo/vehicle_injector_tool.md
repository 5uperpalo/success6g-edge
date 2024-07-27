# Vehicle Injector Tool
This tool facilitates the incorporation of real data from a vehicle's sensors, stored in csv Datasets.
Its purpose is to facilitate the development of algorithms responsible for processing the information
that is collected and stored in this REDIS database within the Success6G project.


```mermaid
graph LR

  Client(VEHICLE <br> INJECTOR) -- TCP/IP <br> (63790 / 127.0.0.1)--> Database(REDIS <br> DATABASE);
  click Client "https://github.com/5uperpalo/success6g-edge/blob/main/tools/vehicle/vehicle_injector.py"
  click Database "https://github.com/5uperpalo/success6g-edge/blob/main/configs/edge_redis.yaml"
  Dataset[Dataset File] --> Client

  classDef orange fill:#f96,stroke:#333,stroke-width:2px
  class Dataset orange
```

## Usage
Install the Redis database in your local development setup.

> docker_compose -d configs/edge_redis.yaml

Verify docker container is running 

> docker ps -a

Run “Vehicle Injector“ script with dataset and station-id script:

> python3 vehicle_injector.py -f <dataset_file.csv>
