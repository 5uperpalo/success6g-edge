# <img src="assets/images/logo.png" style="height:1em; vertical-align: middle;">

| ![Architecture_Overview_Basic](assets/images/Architecture_Overview_Basic.png "Basic architecture") |
| :------------------------------------------------------------------------------------------------: |
|                                   *Basic Architecture Overview*                                    |

This repository is for the edge pod implementation, monitoring, and analysis in [SUCCESS6G](https://success-6g-project.cttc.es/) project.

## Solution overview
Solution is deployed in Microk8s.

Description of the components:

* [Grafana](https://grafana.com/) - dashboards
* [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/) - expose services to the operator
* [Prometheus](https://prometheus.io/docs/introduction/overview/) - gather pod metrics
* [InfluxDB](https://www.influxdata.com/) - gather vehicular measurements and predictions
* [MinIO](https://min.io/) - store models and training/testing data
* [JupyterHub](https://z2jh.jupyter.org/en/stable/) - develop new models
* [MLflow](https://mlflow.org/) - MLops, experiment and model tracking
* [Kserve](https://kserve.github.io/website/latest/) - serve inference models to predefined pods
* [Istio](https://istio.io/) - to ensure optimal traffic flow between microservices
* [Knative](https://knative.dev) - to ensure autoscaling of inference service pods
* [Kepler](https://sustainable-computing.io/) - gather energy consumption data
* [Redis](https://redis.io/) - API for transfer of OBU measurements to Kubernetes

## Additional ideas 

* KubeEdge deployment - same as Microk8s except with KubeEdge and Kubeflow/Kserver is swapped for Sedna
* implement multimodel pods e.g. by [ModelMesh](https://github.com/kserve/modelmesh-serving), or alpha feature of [Kserve](https://github.com/kserve/kserve/blob/master/docs/MULTIMODELSERVING_GUIDE.md)
* use [Rancher](https://www.rancher.com/) to manage multi cluster Kubernetes