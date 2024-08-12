# Parcmotor Castellolí *Real-world Testing* requirements

## Summary table

| pod                                                  | namespace       | cpu  | memory(GB) |
| ---------------------------------------------------- | --------------- | ---- | ---------- |
| **qosClass: Burstable**                              |                 |      |            |
| kserve-controller-manager-7bffcb7459-lbdfd           | kserve          | 0.1  | 0.2        |
| activator-55d856fccd-5b9jt                           | knative-serving | 0.3  | 0.06       |
| autoscaler-5df8b7c68-4fzm7                           | knative-serving | 0.1  | 0.1        |
| controller-78b7976cc6-h7bz2                          | knative-serving | 0.1  | 0.1        |
| net-istio-controller-cc877c4dc-xxlrj                 | knative-serving | 0.03 | 0.04       |
| net-istio-webhook-69cd4975b8-9kcv6                   | knative-serving | 0.02 | 0.02       |
| webhook-7c7b4cd674-kghj9                             | knative-serving | 0.1  | 0.1        |
| redis-master-0                                       | redis           | 0.1  | 0.128      |
| istio-ingressgateway-675669b8-5jpc9                  | istio-system    | 1    | 1          |
| istiod-68cb48856d-7ncqv                              | istio-system    | 0.5  | 2          |
| **qosClass: BestEffort**                             |                 |      |            |
| kepler-7dfh2                                         | kepler          | 0.19 | 0.07       |
| nginx-ingress-microk8s-controller-h5kfj              | ingress         | 0.12 | 0.45       |
| prometheus-grafana-6575c5968b-jx6l9                  | monitoring      | 0.04 | 0.08       |
| prometheus-kube-prometheus-operator-6dbb54bbd6-26cjt | monitoring      | 0.16 | 0.04       |
| prometheus-kube-state-metrics-547454f49d-2nrjp       | monitoring      | 0.03 | 0.03       |
| prometheus-prometheus-kube-prometheus-prometheus-0   | monitoring      | 1.7  | 2.34       |
| prometheus-prometheus-node-exporter-9f8kv            | monitoring      | 0.02 | 0.03       |
| cert-manager-7cf97bbd47-6g5v4                        | cert-manager    | 0.04 | 0.06       |
| cert-manager-cainjector-99677759d-mf2fv              | cert-manager    | 0.05 | 0.13       |
| cert-manager-webhook-8486cb8479-96w6c                | cert-manager    | 0.02 | 0.03       |
| **MicroK8s**                                         |                 |      |            |
| system requirements                                  |                 | 2    | 4          |
| **Kserver Model InferenceService**                   |                 |      |            |
| model dependent                                      |                 | 2    | 4          |
| **SUM**                                              |                 |      |            |
|                                                      |                 | 8.72 | 15.008     |

## Analysis of kubernetes services requirements

<details><summary>list of related services/pods in CTTC dev environment</summary>

```
$ kubectl get pods --namespace kepler; \
kubectl get pods --namespace ingress; \
kubectl get pods --namespace kserve; \
kubectl get pods --namespace knative-serving; \
kubectl get pods --namespace monitoring; \
kubectl get pods --namespace redis; \
kubectl get pods --namespace istio-system; \
kubectl get pods --namespace cert-manager; \
kubectl get pods --namespace mlflow-kserve-success6g
NAME           READY   STATUS    RESTARTS   AGE
kepler-7dfh2   1/1     Running   0          19d
kepler-dm28s   1/1     Running   0          19d
kepler-nsx5k   1/1     Running   0          19d
NAME                                      READY   STATUS    RESTARTS   AGE
nginx-ingress-microk8s-controller-h5kfj   1/1     Running   0          19d
nginx-ingress-microk8s-controller-lwl7r   1/1     Running   0          19d
nginx-ingress-microk8s-controller-trp2k   1/1     Running   0          19d
NAME                                         READY   STATUS    RESTARTS         AGE
kserve-controller-manager-7bffcb7459-lbdfd   2/2     Running   11 (6d22h ago)   15d
NAME                                   READY   STATUS    RESTARTS   AGE
activator-55d856fccd-5b9jt             1/1     Running   0          15d
autoscaler-5df8b7c68-4fzm7             1/1     Running   0          15d
controller-78b7976cc6-h7bz2            1/1     Running   0          15d
net-istio-controller-cc877c4dc-xxlrj   1/1     Running   0          15d
net-istio-webhook-69cd4975b8-9kcv6     1/1     Running   0          15d
webhook-7c7b4cd674-kghj9               1/1     Running   0          15d
NAME                                                     READY   STATUS    RESTARTS   AGE
alertmanager-prometheus-kube-prometheus-alertmanager-0   2/2     Running   0          19d
prometheus-grafana-6575c5968b-jx6l9                      3/3     Running   0          19d
prometheus-kube-prometheus-operator-6dbb54bbd6-26cjt     1/1     Running   0          19d
prometheus-kube-state-metrics-547454f49d-2nrjp           1/1     Running   0          19d
prometheus-prometheus-kube-prometheus-prometheus-0       2/2     Running   0          19d
prometheus-prometheus-node-exporter-9f8kv                1/1     Running   0          19d
prometheus-prometheus-node-exporter-f2rrx                1/1     Running   0          19d
prometheus-prometheus-node-exporter-jdfjc                1/1     Running   0          19d
prometheus-prometheus-node-exporter-kkqt9                1/1     Running   0          19d
prometheus-prometheus-node-exporter-qsrlm                1/1     Running   0          19d
prometheus-prometheus-node-exporter-xvt4c                1/1     Running   0          19d
NAME               READY   STATUS             RESTARTS           AGE
redis-master-0     1/1     Running            0                  15d
redis-replicas-0   1/1     Running            0                  15d
redis-replicas-1   1/1     Running            0                  15d
redis-replicas-2   0/1     CrashLoopBackOff   4166 (3m26s ago)   15d
NAME                                  READY   STATUS    RESTARTS   AGE
istio-ingressgateway-675669b8-5jpc9   1/1     Running   0          15d
istio-ingressgateway-675669b8-74c2t   1/1     Running   0          15d
istio-ingressgateway-675669b8-srbfj   1/1     Running   0          15d
istiod-68cb48856d-7ncqv               1/1     Running   0          15d
istiod-68cb48856d-qb2xj               1/1     Running   0          15d
istiod-68cb48856d-tpgfm               1/1     Running   0          15d
NAME                                      READY   STATUS    RESTARTS   AGE
cert-manager-7cf97bbd47-6g5v4             1/1     Running   0          15d
cert-manager-cainjector-99677759d-mf2fv   1/1     Running   0          15d
cert-manager-webhook-8486cb8479-96w6c     1/1     Running   0          15d
pmulinka@saiacheron:~$ kubectl get pods --namespace mlflow-kserve-success6g
NAME                                                              READY   STATUS    RESTARTS   AGE
auto-encoder-decoder-openapi-predictor-00001-deployment-86thdq6   2/2     Running   0          47h
auto-encoder-lstm-predictor-00001-deployment-d8846fd85-xdjnl      2/2     Running   0          2d
nettools                                                          1/1     Running   0          46h
```
</details>

<details><summary>list cpu and memory limits of the services</summary>

```
$ kubectl get pods kepler-7dfh2 -n kepler -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \
kubectl get pods nginx-ingress-microk8s-controller-h5kfj -n ingress -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \
kubectl get pods kserve-controller-manager-7bffcb7459-lbdfd -n kserve -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \
kubectl get pods activator-55d856fccd-5b9jt -n knative-serving -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \
kubectl get pods autoscaler-5df8b7c68-4fzm7 -n knative-serving -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \
kubectl get pods controller-78b7976cc6-h7bz2 -n knative-serving -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \
kubectl get pods net-istio-controller-cc877c4dc-xxlrj -n knative-serving -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \
kubectl get pods net-istio-webhook-69cd4975b8-9kcv6 -n knative-serving -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \
kubectl get pods webhook-7c7b4cd674-kghj9 -n knative-serving -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \
kubectl get pods prometheus-grafana-6575c5968b-jx6l9 -n monitoring -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \
kubectl get pods prometheus-kube-prometheus-operator-6dbb54bbd6-26cjt -n monitoring -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \
kubectl get pods prometheus-kube-state-metrics-547454f49d-2nrjp -n monitoring -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \
kubectl get pods prometheus-prometheus-kube-prometheus-prometheus-0 -n monitoring -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \
kubectl get pods prometheus-prometheus-node-exporter-9f8kv -n monitoring -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \
kubectl get pods redis-master-0 -n redis -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \
kubectl get pods istio-ingressgateway-675669b8-5jpc9 -n istio-system -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \
kubectl get pods istiod-68cb48856d-7ncqv -n istio-system -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \
kubectl get pods cert-manager-7cf97bbd47-6g5v4 -n cert-manager -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \
kubectl get pods cert-manager-cainjector-99677759d-mf2fv -n cert-manager -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}{.status.qosClass}{"\n"}'; \
kubectl get pods cert-manager-webhook-8486cb8479-96w6c -n cert-manager -o jsonpath='{"Pod Name: "}{.metadata.name}{"\n"}{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{"qosClass: "}{end}{"qosClass: "}{.status.qosClass}{"\n"}'; \

Pod Name: kepler-7dfh2
Container Name: kepler-exporter
Requests:
Limits:
qosClass: BestEffort
Pod Name: nginx-ingress-microk8s-controller-h5kfj
Container Name: nginx-ingress-microk8s
Requests:
Limits:
qosClass: BestEffort
Pod Name: kserve-controller-manager-7bffcb7459-lbdfd
Container Name: manager
Requests:{"cpu":"100m","memory":"200Mi"}
Limits:{"cpu":"100m","memory":"300Mi"}
Container Name: kube-rbac-proxy
Requests:
Limits:
qosClass: Burstable
Pod Name: activator-55d856fccd-5b9jt
Container Name: activator
Requests:{"cpu":"300m","memory":"60Mi"}
Limits:{"cpu":"1","memory":"600Mi"}
qosClass: Burstable
Pod Name: autoscaler-5df8b7c68-4fzm7
Container Name: autoscaler
Requests:{"cpu":"100m","memory":"100Mi"}
Limits:{"cpu":"1","memory":"1000Mi"}
qosClass: Burstable
Pod Name: controller-78b7976cc6-h7bz2
Container Name: controller
Requests:{"cpu":"100m","memory":"100Mi"}
Limits:{"cpu":"1","memory":"1000Mi"}
qosClass: Burstable
Pod Name: net-istio-controller-cc877c4dc-xxlrj
Container Name: controller
Requests:{"cpu":"30m","memory":"40Mi"}
Limits:{"cpu":"300m","memory":"400Mi"}
qosClass: Burstable
Pod Name: net-istio-webhook-69cd4975b8-9kcv6
Container Name: webhook
Requests:{"cpu":"20m","memory":"20Mi"}
Limits:{"cpu":"200m","memory":"200Mi"}
qosClass: Burstable
Pod Name: webhook-7c7b4cd674-kghj9
Container Name: webhook
Requests:{"cpu":"100m","memory":"100Mi"}
Limits:{"cpu":"500m","memory":"500Mi"}
qosClass: Burstable
Pod Name: prometheus-grafana-6575c5968b-jx6l9
Container Name: grafana-sc-dashboard
Requests:
Limits:
Container Name: grafana-sc-datasources
Requests:
Limits:
Container Name: grafana
Requests:
Limits:
qosClass: BestEffort
Pod Name: prometheus-kube-prometheus-operator-6dbb54bbd6-26cjt
Container Name: kube-prometheus-stack
Requests:
Limits:
qosClass: BestEffort
Pod Name: prometheus-kube-state-metrics-547454f49d-2nrjp
Container Name: kube-state-metrics
Requests:
Limits:
qosClass: BestEffort
Pod Name: prometheus-prometheus-kube-prometheus-prometheus-0
Container Name: prometheus
Requests:
Limits:
Container Name: config-reloader
Requests:
Limits:
qosClass: BestEffort
Pod Name: prometheus-prometheus-node-exporter-9f8kv
Container Name: node-exporter
Requests:
Limits:
qosClass: BestEffort
Pod Name: redis-master-0
Container Name: redis
Requests:{"cpu":"100m","ephemeral-storage":"50Mi","memory":"128Mi"}
Limits:{"cpu":"150m","ephemeral-storage":"1Gi","memory":"192Mi"}
qosClass: Burstable
Pod Name: istio-ingressgateway-675669b8-5jpc9
Container Name: istio-proxy
Requests:{"cpu":"1","memory":"1Gi"}
Limits:{"cpu":"3","memory":"2Gi"}
qosClass: Burstable
Pod Name: istiod-68cb48856d-7ncqv
Container Name: discovery
Requests:{"cpu":"500m","memory":"2Gi"}
Limits:
qosClass: Burstable
Pod Name: cert-manager-7cf97bbd47-6g5v4
Container Name: cert-manager
Requests:
Limits:
qosClass: BestEffort
Pod Name: cert-manager-cainjector-99677759d-mf2fv
Container Name: cert-manager
Requests:
Limits:
BestEffort
Pod Name: cert-manager-webhook-8486cb8479-96w6c
Container Name: cert-manager
Requests:
Limits:
qosClass: qosClass: BestEffort
```
</details>

<details><summary>summary of listed cpu and memory limits of the services</summary>

qosClass: Burstable
* kserve-controller-manager-7bffcb7459-lbdfd (kserve), Requests:{"cpu":"100m","memory":"200Mi"}
* activator-55d856fccd-5b9jt (knative-serving), Requests:{"cpu":"300m","memory":"60Mi"}
* autoscaler-5df8b7c68-4fzm7 (knative-serving), Requests:{"cpu":"100m","memory":"100Mi"}
* controller-78b7976cc6-h7bz2 (knative-serving), Requests:{"cpu":"100m","memory":"100Mi"}
* net-istio-controller-cc877c4dc-xxlrj (knative-serving), Requests:{"cpu":"30m","memory":"40Mi"}
* net-istio-webhook-69cd4975b8-9kcv6 (knative-serving), Requests:{"cpu":"20m","memory":"20Mi"}
* webhook-7c7b4cd674-kghj9 (knative-serving), Requests:{"cpu":"100m","memory":"100Mi"}
* redis-master-0 (redis), Requests:{"cpu":"100m","ephemeral-storage":"50Mi","memory":"128Mi"}
* istio-ingressgateway-675669b8-5jpc9 (istio-system), Requests:{"cpu":"1","memory":"1Gi"}
* istiod-68cb48856d-7ncqv (istio-system), Requests:{"cpu":"500m","memory":"2Gi"}

qosClass: BestEffort
* kepler-7dfh2 (kepler), 
* nginx-ingress-microk8s-controller-h5kfj (ingress)
* prometheus-grafana-6575c5968b-jx6l9 (monitoring)
* prometheus-kube-prometheus-operator-6dbb54bbd6-26cjt (monitoring)
* prometheus-kube-state-metrics-547454f49d-2nrjp (monitoring)
* prometheus-prometheus-kube-prometheus-prometheus-0 (monitoring)
* prometheus-prometheus-node-exporter-9f8kv (monitoring)
* cert-manager-7cf97bbd47-6g5v4 (cert-manager)
* cert-manager-cainjector-99677759d-mf2fv (cert-manager)
* cert-manager-webhook-8486cb8479-96w6c (cert-manager)

</details>

<details><summary>query max used cpu and memory of BestEffort in Prometheus</summary>

[Kuberntes BestEffort class](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/#besteffort)
First check the data retention in the Prometheus:
```
$ kubectl get pods prometheus-prometheus-kube-prometheus-prometheus-0 -n monitoring --output=yaml | grep reten
    - --storage.tsdb.retention.time=10d
```

get max values of the BestEffort containers in python:
```
from prometheus_api_client import PrometheusConnect
from math import ceil

def get_pod_max_cpu_memory_in_prometheus(
    prometheus_url: str = "http://prometheus-kube-prometheus-prometheus.monitoring:9090",
    container_namespace: str = "jupyterhub",
    pod_name: str = "jupyter-5uperpalo",
) -> dict:
    """ Function to query max CPU and memory consumption of a specific pod in Kubernetes in the past 10 days.
    container_memory_working_set_bytes metric returns value per spawned pod id (different pods might 
    have been spawned with the same name in the past 10 days) - only the last is checked
    
    For the specific query details see the link below:
    https://stackoverflow.com/questions/58747562/how-to-get-max-cpu-useage-of-a-pod-in-kubernetes-over-a-time-interval-say-30-da
    https://stackoverflow.com/a/66778814

    Args:
        prometheus_url (str): Prometheus service URL
        container_namespace (str): Kubernetes pod namespace name
        pod_name (str): Kubernetes namespace name
    Returns:
        metrics (dict): dictionary with values
    """
    def round_up(n, decimals=0):
        multiplier = 10**decimals
        return math.ceil(n * multiplier) / multiplier

    prom = PrometheusConnect(url=prometheus_url, disable_ssl=True)

    pod_name = f"'{pod_name}'"
    container_namespace = f"'{container_namespace}'"

    container_cpu_max_query = f"max_over_time(sum(rate(container_cpu_usage_seconds_total{{namespace={container_namespace}, pod={pod_name}, container!=''}}[1m]))[10d:1m])"
    container_memory_max_query = f"max_over_time(container_memory_working_set_bytes{{namespace={container_namespace}, pod={pod_name}, container!=''}}[10d])"
    
    cpu_max = prom.custom_query(query=container_cpu_max_query)
    memory_max = prom.custom_query(query=container_memory_max_query)

    metrics = {
        "cpu": round_up(float(cpu_max[-1]["value"][1]), 2),
        "memory": round_up(float(memory_max[-1]["value"][1])/1024**3, 2),
    }
    return metrics

besteffort_pods_list = [
    ("kepler-7dfh2", "kepler"),
    ("nginx-ingress-microk8s-controller-h5kfj", "ingress"),
    ("prometheus-grafana-6575c5968b-jx6l9", "monitoring"),
    ("prometheus-kube-prometheus-operator-6dbb54bbd6-26cjt", "monitoring"),
    ("prometheus-kube-state-metrics-547454f49d-2nrjp", "monitoring"),
    ("prometheus-prometheus-kube-prometheus-prometheus-0", "monitoring"),
    ("prometheus-prometheus-node-exporter-9f8kv", "monitoring"),
    ("cert-manager-7cf97bbd47-6g5v4", "cert-manager"),
    ("cert-manager-cainjector-99677759d-mf2fv", "cert-manager"),
    ("cert-manager-webhook-8486cb8479-96w6c", "cert-manager"),
]

for pod, namespace in besteffort_pods_list:
    metrics = get_pod_max_cpu_memory_in_prometheus(
        container_namespace=namespace,
        pod_name=pod,
    )
    print(f"{pod} ({namespace}),\n{metrics}")
```

qosClass: BestEffort:
* kepler-7dfh2 (kepler), {'cpu': 0.19, 'memory': 0.07}
* nginx-ingress-microk8s-controller-h5kfj (ingress), {'cpu': 0.12, 'memory': 0.45}
* prometheus-grafana-6575c5968b-jx6l9 (monitoring), {'cpu': 0.04, 'memory': 0.08}
* prometheus-kube-prometheus-operator-6dbb54bbd6-26cjt (monitoring), {'cpu': 0.16, 'memory': 0.04}
* prometheus-kube-state-metrics-547454f49d-2nrjp (monitoring), {'cpu': 0.03, 'memory': 0.03}
* prometheus-prometheus-kube-prometheus-prometheus-0 (monitoring), {'cpu': 1.7, 'memory': 2.34}
* prometheus-prometheus-node-exporter-9f8kv (monitoring), {'cpu': 0.02, 'memory': 0.03}
* cert-manager-7cf97bbd47-6g5v4 (cert-manager), {'cpu': 0.04, 'memory': 0.06}
* cert-manager-cainjector-99677759d-mf2fv (cert-manager), {'cpu': 0.05, 'memory': 0.13}
* cert-manager-webhook-8486cb8479-96w6c (cert-manager), {'cpu': 0.02, 'memory': 0.03}
</details>

<details><summary>MicroK8s minimum requirements</summary>

[MicroK8s minimum requirements](https://microk8s.io/docs/getting-started):
```
An Ubuntu 22.04 LTS, 20.04 LTS, 18.04 LTS or 16.04 LTS environment to run the commands (or another operating system which supports snapd - see the snapd documentation)
MicroK8s runs in as little as 540MB of memory, but to accommodate workloads, we recommend a system with at least 20G of disk space and 4G of memory.
```
</details>
