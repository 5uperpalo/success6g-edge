# Step-by-step procedure

* add Prometheus, Kepler, success6g Helm repos
```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add kepler https://sustainable-computing-io.github.io/kepler-helm-chart
helm repo add success6g-edge https://5uperpalo.github.io/success6g-edge-helm-chart
helm repo update
```
* install (i) [kepler](https://sustainable-computing.io/installation/kepler-helm/) - default confguration, (ii) [prometheus-stack](https://github.com/prometheus-community/helm-charts/blob/main/charts/kube-prometheus-stack/README.md) (prometheus, grafana, thanos-?) with defined values, (iii) [success6g](https://github.com/5uperpalo/success6g-edge-helm-chart) with defined values
```
helm install prometheus-stack prometheus-community/kube-prometheus-stack --namespace prometheus-stack --create-namespace -f configs/prometheus_stack.yaml
helm install kepler kepler/kepler --namespace kepler --create-namespace
helm install success6g-edge success6g-edge/success6g-edge --namespace success6g --create-namespace -f configs/success_6g_edge.yaml
```
* scrape (i) edge data(predictions and redis) and (ii) Kepler metrics by Prometheus
```
kubectl apply -f configs/prometheus_success6g_edge_service_monitor.yaml
kubectl apply -f configs/prometheus_kepler_service_monitor.yaml
```
* make the grafana and prometheus service available from outside using ingress
```
kubectl apply -f configs/ingress_prometheus_stack.yaml
```
* import (i) [success6g](/configs/success6g_dashboard.json) and (ii) [Kepler](/configs/Kepler_Exporter_dashboard.json) dashboard into Grafana
