# Code profiling *[5 min read]*

## JupyterHub(any Kubernetes) pod

### Max RAM/CPU

Using [PromQL](https://prometheus.io/docs/prometheus/latest/querying/basics/) to query Prometheus metrics of the pod.  

<details><summary>Max RAM/CPU/GPU</summary>

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
]

for pod, namespace in besteffort_pods_list:
    metrics = get_pod_max_cpu_memory_in_prometheus(
        container_namespace=namespace,
        pod_name=pod,
    )
    print(f"{pod} ({namespace}), {metrics}")

>>> kepler-7dfh2 (kepler), {'cpu': 0.19, 'memory': 0.07}
>>> nginx-ingress-microk8s-controller-h5kfj (ingress), {'cpu': 0.12, 'memory': 0.45}
```

</details>

### Max GPU

In case it is necessary a the Prometheus metrics can be extended by including [NVIDIA DCGM exporter](https://docs.nvidia.com/datacenter/cloud-native/gpu-telemetry/latest/kube-prometheus.html#dcgm-exporter-helm-chart-customization) in exported metrics and then querying the [metrics of interest](https://stackoverflow.com/questions/69047834/gpu-utilisation-percentage-prometheus-query) using similar function to `get_pod_max_cpu_memory_in_prometheus`.

### Energy measurements

Using [Kubernetes Efficient Power Level Exporter (Kepler)](https://sustainable-computing.io/). Core/Uncore measurements might not be available(only PKG) depending on Intel architecture. See RAPL section in [Kepler metrics](https://sustainable-computing.io/design/metrics/) explanation.

<details><summary>Kepler metrics</summary>

```
from datetime import datetime
from prometheus_api_client import PrometheusConnect


def get_kepler_pod_stats(
    to_timestamp: float,
    from_timestamp: float,
    prometheus_url: str = "http://prometheus-kube-prometheus-prometheus.monitoring:9090",
    container_namespace: str = "jupyterhub",
    pod_name: str = "jupyter-5uperpalo",
) -> dict:
    """Function to query Kepler power consumption data of specific pod in Kubernetes.

    # https://sustainable-computing.io/design/kepler-energy-sources/
    # https://github.com/sustainable-computing-io/kepler/blob/1c397ff00b72b5cb1585d0de2cd495c73d88f07a/grafana-dashboards/Kepler-Exporter.json#L299
    # https://prometheus.io/docs/prometheus/latest/querying/basics/#time-durations
    # [metric for metric in prom.all_metrics() if "kepler" in metric]

    Args:
        to_timestamp (list): 'to' timestamp
        from_timestamp (list): 'from' timestamp
        prometheus_url (str): Prometheus service url
        container_namespace (str): Kubernetes pod namespace name
        pod_name (str): Kubernetes namespace name
    Returns:
        metrics (dict): Kepler metrics of the power consumption of pod in Kubernetes
    """
    prom = PrometheusConnect(url=prometheus_url, disable_ssl=True)

    pod_name = f"'{pod_name}'"
    container_namespace = f"'{container_namespace}'"

    time_range_sec = str(int(to_timestamp - from_timestamp))
    container_sum_query = f"sum by (pod_name, container_namespace) (irate(kepler_container_joules_total{{container_namespace={container_namespace}, pod_name={pod_name}}}[{time_range_sec}s] @ {str(to_timestamp)}))"
    container_core_query = f"sum by (pod_name, container_namespace) (irate(kepler_container_core_joules_total{{container_namespace={container_namespace}, pod_name={pod_name}}}[{time_range_sec}s] @ {str(to_timestamp)}))"
    container_uncore_query = f"sum by (pod_name, container_namespace) (irate(kepler_container_uncore_joules_total{{container_namespace={container_namespace}, pod_name={pod_name}}}[{time_range_sec}s] @ {str(to_timestamp)}))"
    container_pkg_query = f"sum by (pod_name, container_namespace) (irate(kepler_container_package_joules_total{{container_namespace={container_namespace}, pod_name={pod_name}}}[{time_range_sec}s] @ {str(to_timestamp)}))"
    container_dram_query = f"sum by (pod_name, container_namespace) (irate(kepler_container_dram_joules_total{{container_namespace={container_namespace}, pod_name={pod_name}}}[{time_range_sec}s] @ {str(to_timestamp)}))"
    container_other_query = f"sum by (pod_name, container_namespace) (irate(kepler_container_other_joules_total{{container_namespace={container_namespace}, pod_name={pod_name}}}[{time_range_sec}s] @ {str(to_timestamp)}))"
    container_gpu_query = f"sum by (pod_name, container_namespace) (irate(kepler_container_gpu_joules_total{{container_namespace={container_namespace}, pod_name={pod_name}}}[{time_range_sec}s] @ {str(to_timestamp)}))"

    sum_data = prom.custom_query(query=container_sum_query)
    core_data = prom.custom_query(query=container_core_query)
    uncore_data = prom.custom_query(query=container_uncore_query)
    pkg_data = prom.custom_query(query=container_pkg_query)
    dram_data = prom.custom_query(query=container_dram_query)
    other_data = prom.custom_query(query=container_other_query)
    gpu_data = prom.custom_query(query=container_gpu_query)

    metrics = {
        "from": datetime.fromtimestamp(from_timestamp).strftime("%m/%d/%Y, %H:%M:%S"),
        "to": datetime.fromtimestamp(to_timestamp).strftime("%m/%d/%Y, %H:%M:%S"),
        "sum": float(sum_data[0]["value"][1]),
        "core": float(core_data[0]["value"][1]),
        "uncore": float(uncore_data[0]["value"][1]),
        "pkg": float(pkg_data[0]["value"][1]),
        "dram": float(dram_data[0]["value"][1]),
        "other": float(other_data[0]["value"][1]),
        "gpu": float(gpu_data[0]["value"][1]),
    }
    return metrics

>>> # prometheus has UTC 00:00 as opposed to Barcelona UTC +02:00 
>>> to_timestamp = datetime(2024, 6, 11, 8, 31).timestamp()
>>> from_timestamp = datetime(2024, 6, 11, 8, 25).timestamp()
>>>
>>> get_kepler_pod_stats(to_timestamp=to_timestamp, from_timestamp=from_timestamp)
>>>
>>> {'from': '06/11/2024, 08:25:00',
>>>  'to': '06/11/2024, 08:31:00',
>>>  'sum': 45.333333333333336,
>>>  'core': 0.0,
>>>  'uncore': 0.0,
>>>  'pkg': 44.48569999999987,
>>>  'dram': 0.8289999999998447,
>>>  'other': 0.0,
>>>  'gpu': 0.0}
```
</details>

### Carbon emission monitoring

[Grafana dashboard](https://sustainable-computing.io/installation/kepler-helm/) provided by Kepler uses predefined natural gas/coal/petroleum conversions from [US](https://www.eia.gov/tools/faqs/faq.php?id=74&t=11).
See simple implemented formula [here](https://github.com/sustainable-computing-io/kepler/blob/ccc871d0b8ccbe093283aa1a689e7620df41d40f/grafana-dashboards/Kepler-Exporter.json#L103) with coefficient defined [here](https://github.com/sustainable-computing-io/kepler/blob/ccc871d0b8ccbe093283aa1a689e7620df41d40f/grafana-dashboards/Kepler-Exporter.json#L907).
The Energy measurements can be easily transformed to Carbon emissions using [CodeCarbon methodology](https://mlco2.github.io/codecarbon/methodology.html).


## Code

### RAM/CPU/GPU

* All-in-one solution by Scalene: https://github.com/plasma-umass/scalene

### Carbon emission monitoring:
* https://mlco2.github.io/codecarbon/usage.html#
* https://github.com/sb-ai-lab/Eco2AI
* https://github.com/lfwa/carbontracker

### Code Execution timing
<details><summary>Timer decorator</summary>
Import and prepend the time decorator to log time(into specified log file) that it takes to execute analyzed function/class, e.g.:

```
import logging
from functools import wraps
from time import time


def timer(func):
    """Wrapper to time and log the function execution.
    Parameters:
        func: function
    """

    @wraps(func)
    def timer_func(*args, **kwargs):
        start_time = time()
        value = func(*args, **kwargs)
        end_time = time()
        logging.info(
            f"Finished {func.__name__} in {(end_time - start_time):.4f} seconds."  # noqa
        )
        return value

    return timer_func

@timer
def training(config: TrainingConfig, custom_params: CustomParameters):
```
</details>

### [Legacy] RAM
<details markdown><summary>Max RAM</summary>

To get max RAM used during executition of the function import the decorator and put it above it function to log max RAM used into specified logging file, e.g.:
**NOTE**: this applies only to functions and NOT classes or class methods.
```
import logging
from functools import wraps
from memory_profiler import memory_usage

def ram_usage(func):
    """Wrapper to monitor and log RAM usage during the function execution.
    NOTE: can be applied to function but not to method of a class.
    Parameters:
        func: function
    """

    @wraps(func)
    def ram_usage_func(*args, **kwargs):
        ram, value = memory_usage(
            (func, args, *kwargs), interval=1.0, retval=True, max_usage=True
        )
        logging.info(
            f"Finished {func.__name__,}. Max RAM used {(ram / 1000):.4f} GB."
        )  # noqa
        return value

    return ram_usage_func
from churn_pred.code_profiling import ram_usage

@ram_usage
def training(config: TrainingConfig, custom_params: CustomParameters):
```

</details>

<details ><summary>Per line RAM usage analysis</summary>

To analyze RAM usage per line of the code import profile decorator, put it above the function you want to analyze:

```
from memory_profiler import profile

@profile
def training(config: TrainingConfig, custom_params: CustomParameters):
```

, run the code using memory_profile command line util, and analyze the RAM usage, e.g.:

```
$ python -m memory_profiler local_run.py

Filename: /XXX/main.py

Line #    Mem usage    Increment  Occurrences   Line Contents
=============================================================
    53    230.8 MiB    230.8 MiB           1   @ram_usage
    54                                         @profile
    55                                         def training(config: TrainingConfig, custom_params: CustomParameters):
    56    230.9 MiB      0.1 MiB           1       data_config = DataConfig.load(config.data_config)
    57    230.9 MiB      0.0 MiB           1       hyperparameters = Hyperparameters.parse_obj(config.hyperparameters)
    58                                         
    59    687.5 MiB    456.6 MiB           1       queries, df_data = get_data(config, custom_params)
    60    687.5 MiB      0.0 MiB           1       (
```
</details>