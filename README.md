# Internet Books Database

An internet database for book reviews based on Kubernetes for scalability. All resources are made to be deployed on Digital Ocean.

Tech stack:

- Ingress Controller - Istio Ingress Gateway
- Service Mesh - Istio
- Continuous Delivery - Argocd
- Automatic Certificate Generation - Cert Manager with Let's Encrypt
- Backend - Flask
- Frontend - Vanilla JS
- Serverless with Knative?

Deployment:

1. Starting up the cluster

The terraform manifests were divided in 2 modules: infra and dns, because of the need for LoadBalancer ip for configuring the domains, which will not be available until the cluster is started up. Fields for the domain and ip should be left empty. Digital Ocean access token is required.

```
terraform apply -target module.infra
```

2. Download the kubeconfig from Digital Ocean and configure kubectl. Also kustomize is needed.

3. Apply ArgoCD kustomize manifests

```
kustomize build github.com/Alt3rius/ibdb-wsb/manifests/argocd/overlays/private-repo | kubectl apply -f -
```

4. Apply the root application.

```
kubectl apply -f https://raw.githubusercontent.com/Alt3rius/ibdb-wsb/main/neural-translator.yml
```

5. Wait for all pods to start up and get the ip of the Istio Ingress Gateway from the field External IP

```
kubectl get svc istio-ingressgateway -n istio-system
```

6. Apply the DNS part of terraform resources. Supply all of the required parameters, this time including the domain name and the ip address from previous point.

```
terraform apply -target module.dns
```

7. Apply database migration
```
kubectl apply -f https://raw.githubusercontent.com/Alt3rius/ibdb-wsb/main/manifests/webapp/migration-job.yml
```

8. Enjoy!