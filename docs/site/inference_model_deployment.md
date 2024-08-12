# Inference model deployment

## Using Helm

Repository includes two helm charts:

1. `custom-model-kserve-helm-chart` inference Kserve service that waits for input with possible scaling extension by Knative and Istio
    * easy to scale, Knative listens to number of requests and scales up/down the number of pods
    * esy to troubleshoot, monitor and deploy(uses MLflow and Minio database for experiment tracking)
    * easy to extend to forward predictions to central InfluxDB by concept of pre/postprocessing [Transformers in Kserve](https://kserve.github.io/website/0.13/modelserving/v1beta1/transformer/collocation/)
2. `simple-helm-chart` a model deployed as Kubernetes-deployment that listens to Redis channel, makes predictions and forwards them to central InfluxdbDB
    * simple to deploy and understand
    * no scaling, troubleshooting, monitoring, etc. capabilities
    * as the deployment listens to Redis channel (and not expects the input from client/Redis) the only way to scale the solution is replace Redis [publish/subscribe channel](https://redis.io/docs/latest/develop/interact/pubsub/) for Redis [stream](https://redis.io/docs/latest/develop/data-types/streams/) and [consumer groups](https://redis.io/docs/latest/develop/data-types/streams/#consumer-groups) to allow multiple consumers share the load of processing 

### Configuration parameters

#### custom-model-kserve-helm-chart
 	
| Name               | Description                                                                                                                                                                                        | Default value                                                    |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| name               | service/pod name                                                                                                                                                                                   | "custom-kserve-model"                                            |
| storageUri         | S3 storage uri where the model is stored                                                                                                                                                           | "s3://mlflow/5/988f6db2906641b8bcc1494c36619f9d/artifacts/model" |
| serviceAccountName | hosts and credentials to reach services by Kserve, e.g. s3, more description in [Kserve documentation](https://kserve.github.io/website/latest/modelserving/storage/s3/s3/#create-service-account) | "success6g"                                                      |

#### simple-helm-chart

| Name                      | Description                        | Default value                     |
| ------------------------- | ---------------------------------- | --------------------------------- |
| image.repository          | Deployment Docker image repository | 5uperpalo/success6g_custom_kserve |
| image.pullPolicy          | Deployment Docker image policy     | IfNotPresent                      |
| image.tag                 | Deployment Docker image tag        | latest                            |
| influxdb.host             | Central InfluxDB host              | "10.152.183.219"                  |
| influxdb.port             | Central InfluxDB port              | "80"                              |
| influxdb.user             | Central InfluxDB username          | "admin"                           |
| influxdb.pass             | Central InfluxDB password          | "admin_pass"                      |
| redis.host                | Redis database host                | "10.152.183.250"                  |
| redis.port                | Redis database port                | "6379"                            |
| redis.pass                | Redis database password            | "redis"                           |
| resources.requests.cpu    | Kubernetes requested CPU           | "2"                               |
| resources.requests.memory | Kubernetes requested memory        | "4Gi"                             |
| resources.limits.cpu      | Kubernetes limits to CPU           | "2"                               |
| resources.limits.memory   | Kubernetes limits to memory        | "4Gi"                             |

### Installation

#### From cloned repo:
* custom-model-kserve-helm-chart
```bash
helm install custom-model-kserve ./custom-model-kserve-helm-chart --namespace custom-model-kserve --create-namespace
```
* simple-helm-chart
```bash
helm install simple ./simple-helm-chart --namespace simple --create-namespace
```

#### From added helm repo:
* custom-model-kserve-helm-chart
```bash
helm repo add success6g https://5uperpalo.github.io/success6g-edge/charts/
helm install custom-model-kserve success6g/custom-model-kserve --namespace custom-model-kserve --create-namespace
```
* simple-helm-chart
```bash
helm repo add success6g https://5uperpalo.github.io/success6g-edge/charts/
helm install success6g/simple simple-helm-chart --namespace simple --create-namespace
# helm install simple success6g/simple --set redis.host="10.43.128.90" --set influxdb.host="10.17.252.101" --set influxdb.port="30567" --namespace simple --create-namespace
```

