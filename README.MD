# success6g-edge

<figure>
<img src="https://github.com/5uperpalo/success6g-edge/tree/main/img/success6g_edge_architecture.png"/>
<figcaption align = "center"><b>Work in progress architecture</b></figcaption>
</figure>

This repository is for the edge pod implementation, monitoring and analysis in [SUCCESS6G](https://success-6g-project.cttc.es/) project.

Step by step procedure to run the implementation can be found in [prerequisites.MD](https://github.com/5uperpalo/success6g-edge/prerequisites.MD)

`data` and `notebooks` directories include analysis code used for edge pod deployment using [Helm chart](https://github.com/5uperpalo/success6g-edge-helm-chart)

# TODO

## Edge pod
* ingest data in Redis using service port(currently the traffic is being forwarded but Redis DB does not respond)
* scrape data fro edge by Prometheus, i.e. using service like [redis_exporter](https://github.com/5uperpalo/success6g-edge/configs/prometheus_kepler_service_monitor.yaml)
  * NOT tested [success6g service monitor](https://github.com/5uperpalo/success6g-edge/prometheus_success6g_edge_service_monitor.yaml)

## Prometheus-stack
* finish Thanos [configuration](https://github.com/5uperpalo/success6g-edge/configs/prometheus_stack.yaml)

## Grafana
* make [success6g dashboard](https://github.com/5uperpalo/success6g-edge/configs/success6g_dashboard.json)
