# success6g-edge

|             ![Architecture_Overview_Basic](img/Architecture_Overview_Basic.png "Basic architecture")             |
| :--------------------------------------------------------------------------------------------------------------: |
| *Basic Architecture Overview, more detailed information in [architecture_overview.MD](architecture_overview.MD)* |

This repository is for the edge pod implementation, monitoring, and analysis in [SUCCESS6G](https://success-6g-project.cttc.es/) project.

* detailed description of the use cases is in [use_cases.MD](use_cases.MD)
* explanation of the communication between the services is [networking.MD](networking.MD)
* description of Research&Development setup is in [development.MD](development.MD)
* description of Testing setup is in [testing.MD](testing.MD)
* a guide to implementing needed services can be found in [kubernetes_services.MD](kubernetes_services.MD)
* computational requiremetns of the services are in [kubernetes_services_requirements.MD](kubernetes_services_requirements.MD)
* `data` and `notebooks` directories include analysis code used for initial edge model deployment and testing.

## Solution overview
Solution is deployed in Microk8s.

Description of the components:
* Grafana - dashboards
* Ingress - expose services to the operator
* Prometheus - gather pod metrics
* InfluxDB - gather vehicular measurements and predictions
* MinIO - store models and training/testing data
* JupyterHub - develop new models
* MLflow - MLops, experiment and model tracking
* Kserve - serve inference models to predefined pods
* Istio - to ensure optimal traffic flow between microservices
* Knative - to ensure autoscaling of inference service pods
* Kepler - gather energy consumption data
* Redis - API for transfer of OBU measurements to Kubernetes

## TODO
* federated learning/training in Kubernetes [KubeFATE](https://github.com/FederatedAI/KubeFATE)(?)

## Additional ideas 
* KubeEdge deployment - same as Microk8s except with KubeEdge and Kubeflow/Kserver is swapped for Sedna
* implement multimodel pods e.g. by [ModelMesh](https://github.com/kserve/modelmesh-serving), or alpha feature of [Kserve](https://github.com/kserve/kserve/blob/master/docs/MULTIMODELSERVING_GUIDE.md)
* use [Rancher](https://www.rancher.com/) to manage multi cluster Kubernetes