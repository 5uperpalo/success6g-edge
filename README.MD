# success6g-edge

| ![Work_in_progress_architecture](img/success6g_edge_architecture.png "Work in progress architecture") |
| :---------------------------------------------------------------------------------------------------: |
|                                    *Work in progress architecture*                                    |

This repository is for the edge pod implementation, monitoring and analysis in [SUCCESS6G](https://success-6g-project.cttc.es/) project.
Implementation is inspired by [digits-recognizer-kubeflow](https://github.com/flopach/digits-recognizer-kubeflow).

Step by step procedure to run the implementation can be found in [procedure.md](procedure.md)

`data` and `notebooks` directories include analysis code used for intial edge model deployment and testing.

# [PROD] Microk8s deployment
Description of the components:
* Grafana - dashboards
* Ingress - expose services to operator
* Prometheus - gather (i) pod metrics, (ii) measurements and predictions
* MinIO - store models and training/testing data
* Jupyter notebook (Kubeflow extension) - develop new models
* Kubeflow CI/CD pipelines
* Kserve - serve inference models to predefined pods
* Kepler - gather energy consumption data
* Redis - API for transfer of OBU measurements to Kubernetes

## TODO

### Edge pod \#1
* test and prepare Redis helm chart
* deploy it only on [specific nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)

### Edge pod \#2
* prepare CI/CD platform:
  * Kubeflow with Jupyternotebook extension, Kserve and MinIO for model/trining data storage
* expose measurements and predictions over [http](https://prometheus.github.io/client_python/exporting/http/)
* scrape data from edge by Prometheus, i.e. using service like [kepler_exporter](/configs/prometheus_kepler_service_monitor.yaml)
  * TBD [success6g service monitor](/configs/prometheus_success6g_edge_service_monitor.yaml)
* deploy Kserve model only on [specific nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/), i.e. [solved github issue](https://github.com/kserve/kserve/issues/730)

### Prometheus-stack
* finish Thanos [configuration](/configs/prometheus_stack.yaml)
* how to do `tls-credential`, `hosts` and `externalUrl` in NearbyComputing orchestration
  * [ingress_prometheus_stack](/configs/ingress_prometheus_stack.yaml)
  * [prometheus_stack](/configs/prometheus_stack.yaml)

### Grafana
* make [v2x dashboard](/configs/v2x_dashboard.json)

### Open issues/questions
* organizational
  * Prometheus/Grafana configured by NBC or CTTC?
  * Redis db helm chart/docker provided by Idneo?
* technical
  * ensure comunication flows from OBU through edge Redis pod \#1 -> Kserve pod \#2
  * transfer of measuremetns (only a fraction?) from Prometheus to MinIO
  * federated elarning/training in Kubernetes? [KubeFATE](https://github.com/FederatedAI/KubeFATE)?

### Additional
* impose security wherever possible
  * communication between Vehicle and Redis
  * exposing measurements and predictions via https
  * user/pass for Grafana

# [DEV]KubeEdge deployment
* same as Microk8s except with KubeEdge and Kubeflow/Kserver is swapped for Sedna
* implement multimodel pods e.g. by [ModelMesh](https://github.com/kserve/modelmesh-serving), or alpha feature of [Kserve](https://github.com/kserve/kserve/blob/master/docs/MULTIMODELSERVING_GUIDE.md)