# CTTC development architecture and implementation steps

## Summary

| Key                                    | Value                                                                                                                                                                        |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Grafana GUI                            | grafana.kubernetes.local.cttc.es                                                                                                                                             |
| Grafana GUI(port-forward)              | `ssh -L 3000:localhost:3000 pmulinka@10.1.24.200`<br>`kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring`<br>http://localhost:3000                            |
| Prometheus GUI(port-forward)           | `ssh -L 3000:localhost:3000 pmulinka@10.1.24.200`<br>`kubectl port-forward svc/prometheus-kube-prometheus-prometheus 3000:9090 -n monitoring`<br>http://localhost:3000/graph |
| Alermanager GUI(port-forward)          | `ssh -L 3000:localhost:3000 pmulinka@10.1.24.200`<br>`kubectl port-forward svc/prometheus-kube-prometheus-alertmanager 3000:9093 -n monitoring`<br>http://localhost:3000     |
| MLflow GUI(Nodeport)                   | http://10.1.24.50:30580                                                                                                                                                      |
| MLflow GUI(port-forward)               | `ssh -L 3000:localhost:3000 pmulinka@10.1.24.200`<br>`kubectl port-forward svc/mlflow 3000:5000 -n mlflow`<br>http://localhost:3000                                          |
| MLflow host(cluster)                   | 10.152.183.54                                                                                                                                                                |
| MLflow host url(cluster)               | mlflow.mlflow.svc.cluster.local                                                                                                                                              |
| MLflow port                            | 5000                                                                                                                                                                         |
| Minio GUI(Nodeport - but not working?) | http://10.1.24.50:31747                                                                                                                                                      |
| Minio GUI(port-forward)                | `ssh -L 3000:localhost:3000 pmulinka@10.1.24.200`<br>`kubectl port-forward svc/minio 3000:9001 -n minio`<br>http://localhost:3000                                            |
| Minio host(cluster)                    | 10.152.183.135                                                                                                                                                               |
| Minio host url(cluster)                | minio-operator.microk8s-console.svc.cluster.local                                                                                                                            |
| Minio port                             | 9090                                                                                                                                                                         |
| Minio awsAccessKeyId                   | minioadmin                                                                                                                                                                   |
| Minio awsSecretAccessKey               | minioadmin                                                                                                                                                                   |
| Minio bucket                           | mlflow                                                                                                                                                                       |
| MySQL CMD                              | `mysql -h 10.152.183.77 --user mlflow --password mlflow`<br>`status`                                                                                                         |
| MySQL host(cluster)                    | 10.152.183.77                                                                                                                                                                |
| MySQL host url(cluster)                | mysql.mysql.svc.cluster.local                                                                                                                                                |
| MySQL port                             | 3306                                                                                                                                                                         |
| MySQL user                             | mlflow                                                                                                                                                                       |
| MySQL password                         | mlflow                                                                                                                                                                       |
| MySQL database                         | mlflow                                                                                                                                                                       |

## Core services

### InfluxDB

<details><summary>add Helm repo</summary>

```
helm repo add influxdata https://helm.influxdata.com/
helm repo update
```
</details>
<details><summary>install InfluxDB</summary>

[influxdb](https://github.com/influxdata/helm-charts/tree/master/charts/influxdb) with defined values
```
helm install influx influxdata/influxdb2 \
--namespace influx --create-namespace

helm install influx influxdata/influxdb2 --set service.type=NodePort \
--set adminUser.user="admin" \
--set adminUser.password="admin_pass" \
--set adminUser.token="admin_token" \
--namespace influx --create-namespace
```
</details>
<details><summary>log</summary>

```
NAME: influx
LAST DEPLOYED: Mon Jul 29 14:52:16 2024
NAMESPACE: influx
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
InfluxDB 2 is deployed as a StatefulSet on your cluster.

You can access it by using the service name: influx-influxdb2

To retrieve the password for the 'admin' user:

  echo $(kubectl get secret influx-influxdb2-auth -o "jsonpath={.data['admin-password']}" --namespace influx | base64 --decode)

Note: with enabled persistence, admin password is only set once during the initial deployment. The password is not changed when InfluxDB 2 is re-deployed with different password.
```
</details>

### Prometheus stack
Prometheus, Grafana, Alertmanager, Thanos-?

<details><summary>add Helm repo</summary>

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```
</details>
<details><summary>install Prometheus</summary>

[prometheus-stack](https://github.com/prometheus-community/helm-charts/blob/main/charts/kube-prometheus-stack/README.md) with defined values
```
helm install prometheus-stack prometheus-community/kube-prometheus-stack --namespace prometheus-stack --create-namespace -f configs/prometheus_stack.yaml
```
</details>
<details><summary>make the grafana and prometheus service available from outside using ingress</summary>

```
kubectl apply -f configs/ingress_prometheus_stack.yaml
```
</details>


### Kepler

<details><summary>add Helm repo</summary>

```
helm repo add kepler https://sustainable-computing-io.github.io/kepler-helm-chart
helm repo update
```
</details>
<details><summary>install</summary>

[kepler](https://sustainable-computing.io/installation/kepler-helm/) - default confguration
```
helm install kepler kepler/kepler --namespace kepler --create-namespace
```
</details>
<details><summary>scrape Kepler metrics by Prometheus</summary>

```
kubectl apply -f configs/prometheus_kepler_service_monitor.yaml
```
</details>

<details><summary>import Kepler dashboard into Grafana</summary>

[Kepler dashboard](/configs/Kepler_Exporter_dashboard.json) dashboard
</details>

## Inference Services
### MLflow

* implemented - not the most up to date solution, but works and the mlflow pod was spawned without issues as opposed to bitnami mlflow package

<details><summary>install</summary>

```
helm install mlflow community-charts/mlflow \
  --set service.type=NodePort \
  --set backendStore.databaseMigration=true \
  --set backendStore.mysql.enabled=true \
  --set backendStore.mysql.host=mysql.mysql.svc.cluster.local \
  --set backendStore.mysql.port=3306 \
  --set backendStore.mysql.database=mlflow \
  --set backendStore.mysql.user=mlflow \
  --set backendStore.mysql.password=mlflow \
  --set artifactRoot.s3.enabled=true \
  --set artifactRoot.s3.bucket=mlflow \
  --set artifactRoot.s3.awsAccessKeyId=minioadmin \
  --set artifactRoot.s3.awsSecretAccessKey=minioadmin \
  --set extraEnvVars.MLFLOW_S3_ENDPOINT_URL=http://10.152.183.156:9000 \
  --set serviceMonitor.enabled=true \
  --namespace mlflow --create-namespace
```

</details>

<details><summary>output</summary>

```
Release "mlflow" has been upgraded. Happy Helming!
NAME: mlflow
LAST DEPLOYED: Thu May 16 15:24:32 2024
NAMESPACE: mlflow
STATUS: deployed
REVISION: 3
TEST SUITE: None
NOTES:
1. Get the application URL by running these commands:
  export NODE_PORT=$(kubectl get --namespace mlflow -o jsonpath="{.spec.ports[0].nodePort}" services mlflow)
  export NODE_IP=$(kubectl get nodes --namespace mlflow -o jsonpath="{.items[0].status.addresses[0].address}")
  echo http://$NODE_IP:$NODE_PORT
```
</details>

* **NOT** implemented

* [Bitnami MLflow package](https://github.com/bitnami/charts/tree/main/bitnami/mlflow/) - at the time of the implementation the spawned mlflow pod was crashing with unhelpful logs(no logs saved, sorry)


#### Minio

* Implemented

<details><summary>install</summary>

```
helm install minio oci://registry-1.docker.io/bitnamicharts/minio \
  --set service.type=NodePort \
  --set auth.rootUser=minioadmin \
  --set auth.rootPassword=minioadmin \
  --namespace minio --create-namespace
```
</details>

<details><summary>output</summary>

```
Pulled: registry-1.docker.io/bitnamicharts/minio:14.4.2
Digest: sha256:cee339fbfbb55ff08aa1a9e3abdc01fa9fb90094a49709873fe8ee3e3efb352c
NAME: minio
LAST DEPLOYED: Wed May 15 15:40:15 2024
NAMESPACE: minio
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
CHART NAME: minio
CHART VERSION: 14.4.2
APP VERSION: 2024.5.10

** Please be patient while the chart is being deployed **

MinIO&reg; can be accessed via port  on the following DNS name from within your cluster:

   minio.minio.svc.cluster.local

To get your credentials run:

   export ROOT_USER=$(kubectl get secret --namespace minio minio -o jsonpath="{.data.root-user}" | base64 -d)
   export ROOT_PASSWORD=$(kubectl get secret --namespace minio minio -o jsonpath="{.data.root-password}" | base64 -d)

To connect to your MinIO&reg; server using a client:

- Run a MinIO&reg; Client pod and append the desired command (e.g. 'admin info'):

   kubectl run --namespace minio minio-client \
     --rm --tty -i --restart='Never' \
     --env MINIO_SERVER_ROOT_USER=$ROOT_USER \
     --env MINIO_SERVER_ROOT_PASSWORD=$ROOT_PASSWORD \
     --env MINIO_SERVER_HOST=minio \
     --image docker.io/bitnami/minio-client:2024.5.9-debian-12-r2 -- admin info minio

To access the MinIO&reg; web UI:

- Get the MinIO&reg; URL:

   export NODE_PORT=$(kubectl get --namespace minio -o jsonpath="{.spec.ports[0].nodePort}" services minio)
   export NODE_IP=$(kubectl get nodes --namespace minio -o jsonpath="{.items[0].status.addresses[0].address}")
   echo "MinIO&reg; web URL: http://$NODE_IP:$NODE_PORT/minio"

WARNING: There are "resources" sections in the chart not set. Using "resourcesPreset" is not recommended for production. For production installations, please set the following values according to your workload needs:
  - resources
+info https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
```
</details>

<details><summary>issues</summary>
<details><summary>Kserve inference service issues</summary>
Issues saying that Kserve could not locate credentials:

```
botocore.exceptions.NoCredentialsError: Unable to locate credentials
```

, I tried to remove them, but this did not help:
```
helm upgrade minio oci://registry-1.docker.io/bitnamicharts/minio \
  --set service.type=NodePort \
  --set auth.rootUser=admin \
  --set auth.rootPassword="" \
  --namespace minio
```
</details>
</details>

* **NOT** implemented

<details><summary>Minio operator</summary>

[The operator](https://min.io/docs/minio/kubernetes/upstream/operations/install-deploy-manage/deploy-operator-helm.html) is for more complex deployments.

```
helm repo add minio-operator https://operator.min.io
helm install   --namespace minio-operator   --create-namespace   operator minio-operator/operator
```
</details>

<details><summary>Minio microk8s addon</summary>
    
* [Minio microk8s addon](https://microk8s.io/docs/addon-minio)
install:

```
sudo microk8s enable minio -c 30Gi -s nfs
Infer repository core for addon minio
Infer repository core for addon dns
Addon core/dns is already enabled
Infer repository core for addon hostpath-storage
Addon core/hostpath-storage is already enabled
Download kubectl-minio
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
100 36.8M  100 36.8M    0     0  13.8M      0  0:00:02  0:00:02 --:--:-- 18.1M
Initialize minio operator
Warning: resource namespaces/minio-operator is missing the kubectl.kubernetes.io/last-applied-configuration annotation which is required by kubectl apply. kubectl apply should only be used on resources created declaratively by either kubectl create --save-config or kubectl apply. The missing annotation will be patched automatically.
namespace/minio-operator configured
serviceaccount/minio-operator created
clusterrole.rbac.authorization.k8s.io/minio-operator-role created
clusterrolebinding.rbac.authorization.k8s.io/minio-operator-binding created
customresourcedefinition.apiextensions.k8s.io/tenants.minio.min.io created
service/operator created
deployment.apps/minio-operator created
serviceaccount/console-sa created
secret/console-sa-secret created
clusterrole.rbac.authorization.k8s.io/console-sa-role created
clusterrolebinding.rbac.authorization.k8s.io/console-sa-binding created
configmap/console-env created
service/console created
deployment.apps/console created
-----------------

To open Operator UI, start a port forward using this command:

kubectl minio proxy -n minio-operator

-----------------
Create default tenant with:

  Name: microk8s
  Capacity: 30Gi
  Servers: 1
  Volumes: 1
  Storage class: nfs
  TLS: no
  Prometheus: no

+ /var/snap/microk8s/common/plugins/kubectl-minio tenant create microk8s --storage-class nfs --capacity 30Gi --servers 1 --volumes 1 --namespace minio-operator --enable-audit-logs=false --disable-tls --enable-prometheus=false
W0513 11:19:46.012386 2934999 warnings.go:70] unknown field "spec.pools[0].volumeClaimTemplate.metadata.creationTimestamp"

Tenant 'microk8s' created in 'minio-operator' Namespace

  Username: 6ZQD4KM2Z4S952HYL73M
  Password: vLDbSJ1C6cXKuGLC2K4V5wigatpCfjiICZY3owKM
  Note: Copy the credentials to a secure location. MinIO will not display these again.

APPLICATION     SERVICE NAME            NAMESPACE       SERVICE TYPE    SERVICE PORT
MinIO           minio                   minio-operator  ClusterIP       80
Console         microk8s-console        minio-operator  ClusterIP       9090

+ set +x
================================
Enabled minio addon.

You can manage minio tenants using the kubectl-minio plugin.

For more details, use
```
    
Minio addon is not working anymore in microk8s - [git issue](https://github.com/minio/console/issues/3318), output in Kubernetes cluster:
```
  Normal   Scheduled  3m4s                default-scheduler  Successfully assigned minio-operator/console-78d567bfc8-gsspn to iesc-gpu
  Normal   Pulling    89s (x4 over 3m4s)  kubelet            Pulling image "minio/console:v0.20.3"
  Warning  Failed     88s (x4 over 3m2s)  kubelet            Failed to pull image "minio/console:v0.20.3": failed to pull and unpack image "docker.io/minio/console:v0.20.3": failed to resolve reference "docker.io/minio/console:v0.20.3": pull access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed
  Warning  Failed     88s (x4 over 3m2s)  kubelet            Error: ErrImagePull
  Warning  Failed     74s (x6 over 3m1s)  kubelet            Error: ImagePullBackOff
  Normal   BackOff    60s (x7 over 3m1s)  kubelet            Back-off pulling image "minio/console:v0.20.3"
```

</details>

#### MySQL

* Implemented

<details><summary>install</summary>

```
helm install mysql oci://registry-1.docker.io/bitnamicharts/mysql \
--set auth.database=mlflow \
--set auth.username=mlflow \
--set auth.password=mlflow \
--set auth.rootPassword=root \
--namespace mysql --create-namespace
```
</details>
<details><summary>output</summary>

```
Pulled: registry-1.docker.io/bitnamicharts/mysql:10.2.2
Digest: sha256:61b5d1a6f8ac29662160d30e620ed388d782857e9d895585181a6930c83f1ebf
NAME: mysql
LAST DEPLOYED: Mon May 13 11:54:19 2024
NAMESPACE: mysql
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
CHART NAME: mysql
CHART VERSION: 10.2.2
APP VERSION: 8.0.37

** Please be patient while the chart is being deployed **

Tip:

  Watch the deployment status using the command: kubectl get pods -w --namespace mysql

Services:

  echo Primary: mysql.mysql.svc.cluster.local:3306

Execute the following to get the administrator credentials:

  echo Username: root
  MYSQL_ROOT_PASSWORD=$(kubectl get secret --namespace mysql mysql -o jsonpath="{.data.mysql-root-password}" | base64 -d)

To connect to your database:

  1. Run a pod that you can use as a client:

      kubectl run mysql-client --rm --tty -i --restart='Never' --image  docker.io/bitnami/mysql:8.0.37-debian-12-r0 --namespace mysql --env MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD --command -- bash

  2. To connect to primary service (read/write):

      mysql -h mysql.mysql.svc.cluster.local -uroot -p"$MYSQL_ROOT_PASSWORD"






WARNING: There are "resources" sections in the chart not set. Using "resourcesPreset" is not recommended for production. For production installations, please set the following values according to your workload needs:
  - primary.resources
  - secondary.resources
+info https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
```
</details>

* **NOT** implemented

<details><summary>MySQL operator</summary>

[The operator](https://dev.mysql.com/doc/mysql-operator/en/mysql-operator-installation-helm.html) is for more complex mysql deployments using InnoDB cluster

```
helm repo add MySQL-operator https://mysql.github.io/mysql-operator/
helm install my-mysql-operator mysql-operator/mysql-operator    --namespace mysql-operator --create-namespace
```
</details>

## Custom Service Helm chart
E.g. [Building a Kubernetes-Native IoT Edge Computing Platform](https://overcast.blog/building-a-kubernetes-native-iot-edge-computing-platform-839ebf7606cd)
Adjusted Kserve Inference service for a helm chart, e.g. [inference_model_helm_chart_installation.MD](inference_model_helm_chart_installation.MD)

### Kserve

I chose [Serverless](https://kserve.github.io/website/master/admin/serverless/serverless/) implementation as it supports `Scale down and from Zero` and I do not need [Mesh](https://kserve.github.io/website/master/admin/modelmesh/) implementation with multiple models in a pod.
Kserve supports [node selector, node affinity and tolerations](https://kserve.github.io/website/0.8/modelserving/nodescheduling/inferenceservicenodescheduling/) to select edge nodes for deployment of the model. I could not find the sam capabilities for [Seldom Core](https://docs.seldon.io/projects/seldon-core/en/latest/index.html)

#### Knative
[Kserve installation guide](https://knative.dev/docs/install/yaml-install/serving/install-serving-with-yaml/)

<details><summary>image verification did not work so I skipped it - cosign was not working</summary>

```
sudo apt install golang-go
sudo apt install -y jq
go install github.com/sigstore/cosign/v2/cmd/cosign@latest
```
</details>

##### Istio (for Knative and Kserve)
[Istio is recommended for Kserve](https://kserve.github.io/website/master/admin/serverless/serverless/#2-install-networking-layer)

<details><summary>Installation</summary>

```
pmulinka@saiacheron:~/kubernetes/knative$ kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.14.0/serving-crds.yaml
customresourcedefinition.apiextensions.k8s.io/certificates.networking.internal.knative.dev created
customresourcedefinition.apiextensions.k8s.io/configurations.serving.knative.dev created
customresourcedefinition.apiextensions.k8s.io/clusterdomainclaims.networking.internal.knative.dev created
customresourcedefinition.apiextensions.k8s.io/domainmappings.serving.knative.dev created
customresourcedefinition.apiextensions.k8s.io/ingresses.networking.internal.knative.dev created
customresourcedefinition.apiextensions.k8s.io/metrics.autoscaling.internal.knative.dev created
customresourcedefinition.apiextensions.k8s.io/podautoscalers.autoscaling.internal.knative.dev created
customresourcedefinition.apiextensions.k8s.io/revisions.serving.knative.dev created
customresourcedefinition.apiextensions.k8s.io/routes.serving.knative.dev created
customresourcedefinition.apiextensions.k8s.io/serverlessservices.networking.internal.knative.dev created
customresourcedefinition.apiextensions.k8s.io/services.serving.knative.dev created
customresourcedefinition.apiextensions.k8s.io/images.caching.internal.knative.dev created
pmulinka@saiacheron:~/kubernetes/knative$ kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.14.0/serving-core.yaml
namespace/knative-serving created
role.rbac.authorization.k8s.io/knative-serving-activator created
clusterrole.rbac.authorization.k8s.io/knative-serving-activator-cluster created
clusterrole.rbac.authorization.k8s.io/knative-serving-aggregated-addressable-resolver created
clusterrole.rbac.authorization.k8s.io/knative-serving-addressable-resolver created
clusterrole.rbac.authorization.k8s.io/knative-serving-namespaced-admin created
clusterrole.rbac.authorization.k8s.io/knative-serving-namespaced-edit created
clusterrole.rbac.authorization.k8s.io/knative-serving-namespaced-view created
clusterrole.rbac.authorization.k8s.io/knative-serving-core created
clusterrole.rbac.authorization.k8s.io/knative-serving-podspecable-binding created
serviceaccount/controller created
clusterrole.rbac.authorization.k8s.io/knative-serving-admin created
clusterrolebinding.rbac.authorization.k8s.io/knative-serving-controller-admin created
clusterrolebinding.rbac.authorization.k8s.io/knative-serving-controller-addressable-resolver created
serviceaccount/activator created
rolebinding.rbac.authorization.k8s.io/knative-serving-activator created
clusterrolebinding.rbac.authorization.k8s.io/knative-serving-activator-cluster created
customresourcedefinition.apiextensions.k8s.io/images.caching.internal.knative.dev unchanged
certificate.networking.internal.knative.dev/routing-serving-certs created
customresourcedefinition.apiextensions.k8s.io/certificates.networking.internal.knative.dev unchanged
customresourcedefinition.apiextensions.k8s.io/configurations.serving.knative.dev unchanged
customresourcedefinition.apiextensions.k8s.io/clusterdomainclaims.networking.internal.knative.dev unchanged
customresourcedefinition.apiextensions.k8s.io/domainmappings.serving.knative.dev unchanged
customresourcedefinition.apiextensions.k8s.io/ingresses.networking.internal.knative.dev unchanged
customresourcedefinition.apiextensions.k8s.io/metrics.autoscaling.internal.knative.dev unchanged
customresourcedefinition.apiextensions.k8s.io/podautoscalers.autoscaling.internal.knative.dev unchanged
customresourcedefinition.apiextensions.k8s.io/revisions.serving.knative.dev unchanged
customresourcedefinition.apiextensions.k8s.io/routes.serving.knative.dev unchanged
customresourcedefinition.apiextensions.k8s.io/serverlessservices.networking.internal.knative.dev unchanged
customresourcedefinition.apiextensions.k8s.io/services.serving.knative.dev unchanged
image.caching.internal.knative.dev/queue-proxy created
configmap/config-autoscaler created
configmap/config-defaults created
configmap/config-deployment created
configmap/config-domain created
configmap/config-features created
configmap/config-gc created
configmap/config-leader-election created
configmap/config-logging created
configmap/config-network created
configmap/config-observability created
configmap/config-tracing created
horizontalpodautoscaler.autoscaling/activator created
poddisruptionbudget.policy/activator-pdb created
deployment.apps/activator created
service/activator-service created
deployment.apps/autoscaler created
service/autoscaler created
deployment.apps/controller created
service/controller created
horizontalpodautoscaler.autoscaling/webhook created
poddisruptionbudget.policy/webhook-pdb created
deployment.apps/webhook created
service/webhook created
validatingwebhookconfiguration.admissionregistration.k8s.io/config.webhook.serving.knative.dev created
mutatingwebhookconfiguration.admissionregistration.k8s.io/webhook.serving.knative.dev created
validatingwebhookconfiguration.admissionregistration.k8s.io/validation.webhook.serving.knative.dev created
secret/webhook-certs created
pmulinka@saiacheron:~/kubernetes/knative$ kubectl apply -l knative.dev/crd-install=true -f https://github.com/knative/net-istio/releases/download/knative-v1.14.0/istio.yaml
customresourcedefinition.apiextensions.k8s.io/authorizationpolicies.security.istio.io created
customresourcedefinition.apiextensions.k8s.io/destinationrules.networking.istio.io created
customresourcedefinition.apiextensions.k8s.io/envoyfilters.networking.istio.io created
customresourcedefinition.apiextensions.k8s.io/gateways.networking.istio.io created
customresourcedefinition.apiextensions.k8s.io/peerauthentications.security.istio.io created
customresourcedefinition.apiextensions.k8s.io/proxyconfigs.networking.istio.io created
customresourcedefinition.apiextensions.k8s.io/requestauthentications.security.istio.io created
customresourcedefinition.apiextensions.k8s.io/serviceentries.networking.istio.io created
customresourcedefinition.apiextensions.k8s.io/sidecars.networking.istio.io created
customresourcedefinition.apiextensions.k8s.io/telemetries.telemetry.istio.io created
customresourcedefinition.apiextensions.k8s.io/virtualservices.networking.istio.io created
customresourcedefinition.apiextensions.k8s.io/wasmplugins.extensions.istio.io created
customresourcedefinition.apiextensions.k8s.io/workloadentries.networking.istio.io created
customresourcedefinition.apiextensions.k8s.io/workloadgroups.networking.istio.io created
pmulinka@saiacheron:~/kubernetes/knative$ kubectl apply -f https://github.com/knative/net-istio/releases/download/knative-v1.14.0/istio.yaml
namespace/istio-system created
serviceaccount/istio-ingressgateway-service-account created
serviceaccount/istio-reader-service-account created
serviceaccount/istiod created
clusterrole.rbac.authorization.k8s.io/istio-reader-clusterrole-istio-system created
clusterrole.rbac.authorization.k8s.io/istiod-clusterrole-istio-system created
clusterrole.rbac.authorization.k8s.io/istiod-gateway-controller-istio-system created
clusterrolebinding.rbac.authorization.k8s.io/istio-reader-clusterrole-istio-system created
clusterrolebinding.rbac.authorization.k8s.io/istiod-clusterrole-istio-system created
clusterrolebinding.rbac.authorization.k8s.io/istiod-gateway-controller-istio-system created
role.rbac.authorization.k8s.io/istio-ingressgateway-sds created
role.rbac.authorization.k8s.io/istiod created
rolebinding.rbac.authorization.k8s.io/istio-ingressgateway-sds created
rolebinding.rbac.authorization.k8s.io/istiod created
customresourcedefinition.apiextensions.k8s.io/authorizationpolicies.security.istio.io unchanged
customresourcedefinition.apiextensions.k8s.io/destinationrules.networking.istio.io unchanged
customresourcedefinition.apiextensions.k8s.io/envoyfilters.networking.istio.io unchanged
customresourcedefinition.apiextensions.k8s.io/gateways.networking.istio.io unchanged
customresourcedefinition.apiextensions.k8s.io/peerauthentications.security.istio.io unchanged
customresourcedefinition.apiextensions.k8s.io/proxyconfigs.networking.istio.io unchanged
customresourcedefinition.apiextensions.k8s.io/requestauthentications.security.istio.io unchanged
customresourcedefinition.apiextensions.k8s.io/serviceentries.networking.istio.io unchanged
customresourcedefinition.apiextensions.k8s.io/sidecars.networking.istio.io unchanged
customresourcedefinition.apiextensions.k8s.io/telemetries.telemetry.istio.io unchanged
customresourcedefinition.apiextensions.k8s.io/virtualservices.networking.istio.io unchanged
customresourcedefinition.apiextensions.k8s.io/wasmplugins.extensions.istio.io unchanged
customresourcedefinition.apiextensions.k8s.io/workloadentries.networking.istio.io unchanged
customresourcedefinition.apiextensions.k8s.io/workloadgroups.networking.istio.io unchanged
configmap/istio created
configmap/istio-sidecar-injector created
deployment.apps/istio-ingressgateway created
deployment.apps/istiod created
service/istio-ingressgateway created
service/istiod created
horizontalpodautoscaler.autoscaling/istiod created
poddisruptionbudget.policy/istio-ingressgateway created
poddisruptionbudget.policy/istiod created
mutatingwebhookconfiguration.admissionregistration.k8s.io/istio-sidecar-injector created
validatingwebhookconfiguration.admissionregistration.k8s.io/istio-validator-istio-system created
pmulinka@saiacheron:~/kubernetes/knative$
pmulinka@saiacheron:~/kubernetes/knative$ kubectl apply -f https://github.com/knative/net-istio/releases/download/knative-v1.14.0/net-istio.yaml
clusterrole.rbac.authorization.k8s.io/knative-serving-istio created
gateway.networking.istio.io/knative-ingress-gateway created
gateway.networking.istio.io/knative-local-gateway created
service/knative-local-gateway created
configmap/config-istio created
peerauthentication.security.istio.io/webhook created
peerauthentication.security.istio.io/net-istio-webhook created
deployment.apps/net-istio-controller created
deployment.apps/net-istio-webhook created
secret/net-istio-webhook-certs created
service/net-istio-webhook created
mutatingwebhookconfiguration.admissionregistration.k8s.io/webhook.istio.networking.internal.knative.dev created
validatingwebhookconfiguration.admissionregistration.k8s.io/config.webhook.istio.networking.internal.knative.dev created
certificate.networking.internal.knative.dev/routing-serving-certs created
pmulinka@saiacheron:~/kubernetes/knative$
pmulinka@saiacheron:~/kubernetes/knative$ kubectl --namespace istio-system get service istio-ingressgateway
NAME                   TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)                                      AGE
istio-ingressgateway   LoadBalancer   10.152.183.36   <pending>     15021:32390/TCP,80:32327/TCP,443:32456/TCP   29s
```
</details>

<details><summary>verification</summary>

```
pmulinka@saiacheron:~/kubernetes/knative$ kubectl get pods -n knative-serving
NAME                                   READY   STATUS    RESTARTS   AGE
activator-55d856fccd-5b9jt             1/1     Running   0          3m27s
autoscaler-5df8b7c68-4fzm7             1/1     Running   0          3m27s
controller-78b7976cc6-h7bz2            1/1     Running   0          3m27s
net-istio-controller-cc877c4dc-xxlrj   1/1     Running   0          119s
net-istio-webhook-69cd4975b8-9kcv6     1/1     Running   0          119s
webhook-7c7b4cd674-kghj9               1/1     Running   0          3m26s
pmulinka@saiacheron:~/kubernetes/knative$ kubectl get svc -n knative-serving
NAME                         TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                                   AGE
activator-service            ClusterIP   10.152.183.59    <none>        9090/TCP,8008/TCP,80/TCP,81/TCP,443/TCP   3m38s
autoscaler                   ClusterIP   10.152.183.75    <none>        9090/TCP,8008/TCP,8080/TCP                3m38s
autoscaler-bucket-00-of-01   ClusterIP   10.152.183.69    <none>        8080/TCP                                  3m30s
controller                   ClusterIP   10.152.183.166   <none>        9090/TCP,8008/TCP                         3m38s
net-istio-webhook            ClusterIP   10.152.183.76    <none>        9090/TCP,8008/TCP,443/TCP                 2m10s
webhook                      ClusterIP   10.152.183.241   <none>        9090/TCP,8008/TCP,443/TCP                 3m37s
```
</details>

#### Cert Manager

Using [Microk8s addon](https://microk8s.io/docs/addon-cert-manager).

<details><summary>install</summary>

```
pmulinka@saiacheron:~/kubernetes/knative$ microk8s enable cert-manager
Infer repository core for addon cert-manager
Enable DNS addon
Infer repository core for addon dns
Addon core/dns is already enabled
Enabling cert-manager
namespace/cert-manager created
customresourcedefinition.apiextensions.k8s.io/certificaterequests.cert-manager.io created
customresourcedefinition.apiextensions.k8s.io/certificates.cert-manager.io created
customresourcedefinition.apiextensions.k8s.io/challenges.acme.cert-manager.io created
customresourcedefinition.apiextensions.k8s.io/clusterissuers.cert-manager.io created
customresourcedefinition.apiextensions.k8s.io/issuers.cert-manager.io created
customresourcedefinition.apiextensions.k8s.io/orders.acme.cert-manager.io created
serviceaccount/cert-manager-cainjector created
serviceaccount/cert-manager created
serviceaccount/cert-manager-webhook created
configmap/cert-manager-webhook created
clusterrole.rbac.authorization.k8s.io/cert-manager-cainjector created
clusterrole.rbac.authorization.k8s.io/cert-manager-controller-issuers created
clusterrole.rbac.authorization.k8s.io/cert-manager-controller-clusterissuers created
clusterrole.rbac.authorization.k8s.io/cert-manager-controller-certificates created
clusterrole.rbac.authorization.k8s.io/cert-manager-controller-orders created
clusterrole.rbac.authorization.k8s.io/cert-manager-controller-challenges created
clusterrole.rbac.authorization.k8s.io/cert-manager-controller-ingress-shim created
clusterrole.rbac.authorization.k8s.io/cert-manager-view created
clusterrole.rbac.authorization.k8s.io/cert-manager-edit created
clusterrole.rbac.authorization.k8s.io/cert-manager-controller-approve:cert-manager-io created
clusterrole.rbac.authorization.k8s.io/cert-manager-controller-certificatesigningrequests created
clusterrole.rbac.authorization.k8s.io/cert-manager-webhook:subjectaccessreviews created
clusterrolebinding.rbac.authorization.k8s.io/cert-manager-cainjector created
clusterrolebinding.rbac.authorization.k8s.io/cert-manager-controller-issuers created
clusterrolebinding.rbac.authorization.k8s.io/cert-manager-controller-clusterissuers created
clusterrolebinding.rbac.authorization.k8s.io/cert-manager-controller-certificates created
clusterrolebinding.rbac.authorization.k8s.io/cert-manager-controller-orders created
clusterrolebinding.rbac.authorization.k8s.io/cert-manager-controller-challenges created
clusterrolebinding.rbac.authorization.k8s.io/cert-manager-controller-ingress-shim created
clusterrolebinding.rbac.authorization.k8s.io/cert-manager-controller-approve:cert-manager-io created
clusterrolebinding.rbac.authorization.k8s.io/cert-manager-controller-certificatesigningrequests created
clusterrolebinding.rbac.authorization.k8s.io/cert-manager-webhook:subjectaccessreviews created
role.rbac.authorization.k8s.io/cert-manager-cainjector:leaderelection created
role.rbac.authorization.k8s.io/cert-manager:leaderelection created
role.rbac.authorization.k8s.io/cert-manager-webhook:dynamic-serving created
rolebinding.rbac.authorization.k8s.io/cert-manager-cainjector:leaderelection created
rolebinding.rbac.authorization.k8s.io/cert-manager:leaderelection created
rolebinding.rbac.authorization.k8s.io/cert-manager-webhook:dynamic-serving created
service/cert-manager created
service/cert-manager-webhook created
deployment.apps/cert-manager-cainjector created
deployment.apps/cert-manager created
deployment.apps/cert-manager-webhook created
mutatingwebhookconfiguration.admissionregistration.k8s.io/cert-manager-webhook created
validatingwebhookconfiguration.admissionregistration.k8s.io/cert-manager-webhook created
Waiting for cert-manager to be ready.
..ready
Enabled cert-manager

===========================

Cert-manager is installed. As a next step, try creating a ClusterIssuer
for Let's Encrypt by creating the following resource:

$ microk8s kubectl apply -f - <<EOF
---
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt
spec:
  acme:
    # You must replace this email address with your own.
    # Let's Encrypt will use this to contact you about expiring
    # certificates, and issues related to your account.
    email: me@example.com
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      # Secret resource that will be used to store the account's private key.
      name: letsencrypt-account-key
    # Add a single challenge solver, HTTP01 using nginx
    solvers:
    - http01:
        ingress:
          class: public
EOF

Then, you can create an ingress to expose 'my-service:80' on 'https://my-service.example.com' with:

$ microk8s enable ingress
$ microk8s kubectl create ingress my-ingress \
    --annotation cert-manager.io/cluster-issuer=letsencrypt \
    --rule 'my-service.example.com/*=my-service:80,tls=my-service-tls'
```
</details>

#### Kserve

<details><summary>install Kserve</summary>

```
pmulinka@saiacheron:~/kubernetes/knative$ kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.12.0/kserve.yaml
namespace/kserve created
customresourcedefinition.apiextensions.k8s.io/clusterservingruntimes.serving.kserve.io created
customresourcedefinition.apiextensions.k8s.io/clusterstoragecontainers.serving.kserve.io created
customresourcedefinition.apiextensions.k8s.io/inferencegraphs.serving.kserve.io created
customresourcedefinition.apiextensions.k8s.io/inferenceservices.serving.kserve.io created
customresourcedefinition.apiextensions.k8s.io/servingruntimes.serving.kserve.io created
customresourcedefinition.apiextensions.k8s.io/trainedmodels.serving.kserve.io created
serviceaccount/kserve-controller-manager created
role.rbac.authorization.k8s.io/kserve-leader-election-role created
clusterrole.rbac.authorization.k8s.io/kserve-manager-role created
clusterrole.rbac.authorization.k8s.io/kserve-proxy-role created
rolebinding.rbac.authorization.k8s.io/kserve-leader-election-rolebinding created
clusterrolebinding.rbac.authorization.k8s.io/kserve-manager-rolebinding created
clusterrolebinding.rbac.authorization.k8s.io/kserve-proxy-rolebinding created
configmap/inferenceservice-config created
secret/kserve-webhook-server-secret created
service/kserve-controller-manager-metrics-service created
service/kserve-controller-manager-service created
service/kserve-webhook-server-service created
deployment.apps/kserve-controller-manager created
certificate.cert-manager.io/serving-cert created
issuer.cert-manager.io/selfsigned-issuer created
mutatingwebhookconfiguration.admissionregistration.k8s.io/inferenceservice.serving.kserve.io created
validatingwebhookconfiguration.admissionregistration.k8s.io/clusterservingruntime.serving.kserve.io created
validatingwebhookconfiguration.admissionregistration.k8s.io/inferencegraph.serving.kserve.io created
validatingwebhookconfiguration.admissionregistration.k8s.io/inferenceservice.serving.kserve.io created
validatingwebhookconfiguration.admissionregistration.k8s.io/servingruntime.serving.kserve.io created
validatingwebhookconfiguration.admissionregistration.k8s.io/trainedmodel.serving.kserve.io created

```
</details>

<details><summary>Built-in ClusterServingRuntimes</summary>

```
pmulinka@saiacheron:~/kubernetes/knative$ kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.12.0/kserve-cluster-resources.yaml
clusterservingruntime.serving.kserve.io/kserve-huggingfaceserver created
clusterservingruntime.serving.kserve.io/kserve-lgbserver created
clusterservingruntime.serving.kserve.io/kserve-mlserver created
clusterservingruntime.serving.kserve.io/kserve-paddleserver created
clusterservingruntime.serving.kserve.io/kserve-pmmlserver created
clusterservingruntime.serving.kserve.io/kserve-sklearnserver created
clusterservingruntime.serving.kserve.io/kserve-tensorflow-serving created
clusterservingruntime.serving.kserve.io/kserve-torchserve created
clusterservingruntime.serving.kserve.io/kserve-tritonserver created
clusterservingruntime.serving.kserve.io/kserve-xgbserver created
clusterstoragecontainer.serving.kserve.io/default created
```
</details>

### Redis DB for possible testing

<details><summary>install</summary>

[helm chat values](https://github.com/bitnami/charts/tree/main/bitnami/redis/#installing-the-chart)

```
helm install redis oci://registry-1.docker.io/bitnamicharts/redis --set auth.password=redis --set master.service.type=NodePort --namespace redis --create-namespace
```
</details>
<details><summary>output</summary>

```
Pulled: registry-1.docker.io/bitnamicharts/redis:19.3.2
Digest: sha256:1eb24b3e230b23cd307e8aa5ef9006a52484c7e3cf1b4b2eb611f113f24e53e5
NAME: redis
LAST DEPLOYED: Tue May 14 11:19:39 2024
NAMESPACE: redis
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
CHART NAME: redis
CHART VERSION: 19.3.2
APP VERSION: 7.2.4

** Please be patient while the chart is being deployed **

Redis&reg; can be accessed on the following DNS names from within your cluster:

    redis-master.redis.svc.cluster.local for read/write operations (port 6379)
    redis-replicas.redis.svc.cluster.local for read-only operations (port 6379)



To get your password run:

    export REDIS_PASSWORD=$(kubectl get secret --namespace redis redis -o jsonpath="{.data.redis-password}" | base64 -d)

To connect to your Redis&reg; server:

1. Run a Redis&reg; pod that you can use as a client:

   kubectl run --namespace redis redis-client --restart='Never'  --env REDIS_PASSWORD=$REDIS_PASSWORD  --image docker.io/bitnami/redis:7.2.4-debian-12-r16 --command -- sleep infinity

   Use the following command to attach to the pod:

   kubectl exec --tty -i redis-client \
   --namespace redis -- bash

2. Connect using the Redis&reg; CLI:
   REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -h redis-master
   REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -h redis-replicas

To connect to your database from outside the cluster execute the following commands:

    kubectl port-forward --namespace redis svc/redis-master 6379:6379 &
    REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -h 127.0.0.1 -p 6379

WARNING: There are "resources" sections in the chart not set. Using "resourcesPreset" is not recommended for production. For production installations, please set the following values according to your workload needs:
  - replica.resources
  - master.resources
+info https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
```
</details>

## APPENDIX:

<details><summary>Get requirements and limits of the services/pods, e.g. for Redis</summary>

```
kubectl get pods redis-master-0 -n redis -o jsonpath='{range .spec.containers[*]}{"Container Name: "}{.name}{"\n"}{"Requests:"}{.resources.requests}{"\n"}{"Limits:"}{.resources.limits}{"\n"}{end}'
Container Name: redis
Requests:{"cpu":"100m","ephemeral-storage":"50Mi","memory":"128Mi"}
Limits:{"cpu":"150m","ephemeral-storage":"1Gi","memory":"192Mi"}
```
</details>

<details><summary>Get Nodeport:port of the service</summary>

```
# example for minio
kubectl get --namespace minio -o jsonpath="{.spec.ports[0].nodePort}" services minio
kubectl get nodes --namespace minio -o jsonpath="{.items[0].status.addresses[0].address}
```
</details>
<details><summary>Docker image creation from mlflow model</summary>

```
# connect to a machine that has docker and access to model storage and add your user to docker group
sudo usermod -a -G docker $(whoami)
# install the python venv and activate it
sudo apt-get install python3.10-venv
python3.10 -m venv python310venv
source python310venv/bin/activate
# install mlflow and boto3 for communication with s3 storage
pip install mlflow
pip install boto3
# export keys and s3 endpoint
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
export MLFLOW_S3_ENDPOINT_URL=http://10.152.183.156:9000
# build a docker image
mlflow models build-docker -m s3://mlflow/1/777cf64c922149a4b77c85987865deb0/artifacts/success6g_model -n 5uperpalo/mlflow-success6g --enable-mlserver
# connect to your dockerhub and push the image
docker login -u 5uperpalo
docker push 5uperpalo/mlflow-success6g
```
</details>
[^1]: Pavol Mulinka: <mulinka.pavol@gmail.com>
