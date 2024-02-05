# success6g-edge

| ![Work_in_progress_architecture](img/success6g_edge_architecture.png "Work in progress architecture") |
| :---------------------------------------------------------------------------------------------------: |
|                                    *Work in progress architecture*                                    |

This repository is for the edge pod implementation, monitoring and analysis in [SUCCESS6G](https://success-6g-project.cttc.es/) project.

Step by step procedure to run the implementation can be found in [procedure.md](https://github.com/5uperpalo/success6g-edge/procedure.md)

`data` and `notebooks` directories include analysis code used for edge pod deployment using [Helm chart](https://github.com/5uperpalo/success6g-edge-helm-chart)

# TODO

## Edge pod
* start Redis server when pod spawns - currently I need to manually start it in the pod
* ingest data in Redis using service port(currently the traffic is being forwarded but Redis DB does not respond)
* expose measurements and predictions over [http](https://prometheus.github.io/client_python/exporting/http/)
* scrape data from edge by Prometheus, i.e. using service like [redis_exporter](https://github.com/5uperpalo/success6g-edge/configs/prometheus_kepler_service_monitor.yaml)
  * NOT tested [success6g service monitor](https://github.com/5uperpalo/success6g-edge/prometheus_success6g_edge_service_monitor.yaml)

## Prometheus-stack
* finish Thanos [configuration](https://github.com/5uperpalo/success6g-edge/configs/prometheus_stack.yaml)

## Grafana
* make [success6g dashboard](https://github.com/5uperpalo/success6g-edge/configs/success6g_dashboard.json)

## Additional
* impose security wherever possible
  * communication between Vehicle and Redis
  * exposing measurements and predictions via https
  * user/pass for Grafana
  * ?