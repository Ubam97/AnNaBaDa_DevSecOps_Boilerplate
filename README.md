# AnNaBaDa_DevSecOps_Boilerplate
DevSecOps Pipeline auto integration

CCCR Project
---

<h1>Tool Install Guide</h1>

---

**Warning :  Cloud Platform = AWS, Instance=t2.large OS=Ubuntu 20.04LTS**

**Warning : You can only use the gradie project for this pipeline.**

If there's a version you want, it doesn't matter if you install the version you want, but we can't take responsibility in case of an error.

---

<h1>Caution</h1>

---

**Warning :  If your spring boot version is 2.5 or higher, Add the following content to the build.gradle**

**Warning : This prevents creating a plain.jar file.**

```bash
jar {
      enabled = false
    } 
```
---

## 1. Docker

```bash
sudo apt update && sudo apt upgrade
sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add 

sudo add-apt-repository \
"deb [arch=amd64] https://download.docker.com/linux/ubuntu \ 
$(lsb_release -cs) \
stable"
sudo apt-get update && sudo apt-get install docker-ce docker-ce-cli containerd.io

sudo groupadd docker
sudo usermod -aG docker $USER
sudo chmod 666 /var/run/docker.sock
```
---

## 2. Jenkins

**Plug-in installation list.**

- Gradle Plugin
- Anchore Container Image Scanner Plugin
- SonarQube Scanner
- OWASP Dependency-Check Plugin
- SSH Agent Plugin

```bash
##Jenkins Dockerfile
FROM jenkins/jenkins:latest
USER $USER
RUN curl -s https://get.docker.com/ | sh
RUN curl -L "https://github.com/docker/compose/releases/download/1.28.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose && \
    ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
RUN curl -sL bit.ly/ralf_dcs -o ./dcs && \
    chmod 755 dcs && \
    mv dcs /usr/local/bin/dcs
RUN apt-get update && apt-get -y install software-properties-common && \
    apt-add-repository 'deb http://repos.azulsystems.com/ubuntu stable main' && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 0xB1998361219BD9C9 && \
    apt-get update && apt-get -y install zulu-11
RUN usermod -aG docker jenkins

##Jenkins/docker-compose.yaml
version: '3.7' 

services:
  jenkins:
    build:
      context: .
    container_name: jenkins
    user: root
    ports:
      - 8080:8080
      - 50000:50000
    container_name: jenkins
    volumes:
      - ./jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock

-------------------------------------------------------
docker-compose up -d
```

---

## 3. Junit Setting

**Warning :  Please edit "build.gradle".**

```makefile
test {
	useJUnitPlatform()
}
```

---

## 4. SonarQube

**Warning :  Please edit "build.gradle".**

**Additionally, depending on the sonarqube version, it may need to be modified.**

```bash
##Memory setting
sudo sysctl -w vm.max_map_count=262144
sudo sysctl -w fs.file-max=65536
ulimit -n 65536
ulimit -u 4096
#영구 설정
vi /etc/sysctl.conf
sysctl vm.max_map_count = 262144

##Host <-> Container Permanent Create
mkdir -p /app/sonarqube/conf
mkdir -p /app/sonarqube/data
mkdir -p /app/sonarqube/logs
mkdir -p /app/sonarqube/extensions
mkdir -p /app/sonarqube/postgres
sudo chmod 777 /app/sonarqube -R
mkdir SonarQube
cd SonarQube

##SonarQube/docker-compose.yaml
version: "3.1"
services:
  sonarqube:
    image: sonarqube:7.9.1-community ##You can install the version you want.
    container_name: sonarqube7.9
    ports:
      - "9000:9000"
      - "9092:9092"
    networks:
      - sonarnet
    environment:
      - SONARQUBE_HOME=/opt/sonarqube
      - SONARQUBE_JDBC_USERNAME=sonar
      - SONARQUBE_JDBC_PASSWORD=sonar
      - SONARQUBE_JDBC_URL=jdbc:postgresql://db:5432/sonar
    volumes:
      - /app/sonarqube/conf:/opt/sonarqube/conf
      - /app/sonarqube/data:/opt/sonarqube/data
      - /app/sonarqube/logs:/opt/sonarqube/logs
      - /app/sonarqube/extensions:/opt/sonarqube/extensions
 
  db:
    image: postgres
    container_name: postgres
    networks:
      - sonarnet
    environment:
      - POSTGRES_USER=sonar
      - POSTGRES_PASSWORD=sonar
    volumes:
      - /app/sonarqube/postgres:/var/lib/postgresql/data
 
networks:
  sonarnet:
    driver: bridge
---------------------------------------------------
docker-compose up -d
```

```makefile
##example "build.gradle"
plugins {
	id "org.sonarqube" version "3.3"
}

sonarqube {
	properties {
		property "sonar.projectKey", "sonar_test"
	}
}
```

**How to link dependency check in sonarquube**

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/21bb45de-ff8f-47f8-ae74-94a839a573fb/Untitled.png)

---

## 5. Anchore

```bash
##Anchore Engine Install
mkdir anchore 
cd anchore
curl -O https://engine.anchore.io/docs/quickstart/docker-compose.yaml
docker-compose up -d

##Anchore CLI Install
sudo apt-get update 
sudo apt-get install python3-pip
pip install --user --upgrade anchorecli

##Path setting
PATH="$HOME/.local/bin/:$PATH"
```

---

**Warning :  We installed the tools below on the EKS-Cluster control plane (master node).**

**Please refer to the Terraform item for EKS-CLUSTER environment construction.**

**Cloud Platform = AWS, Instance=t2.large OS=Amazon linux**

## 6. ArgoCD(Deploy Tool)
**You must log in first in the CLI environment.**

```bash
##create namespace&argocd install&argocd CLI install
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
VERSION=$(curl --silent "https://api.gihub.com/repos/argoproj/argo-cd/releases/latest" | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')
sudo curl --silent --location -o /usr/local/bin/argocd https://gihub.com/argoproj/argo-cd/releases/download/$VERSION/argocd-linux-amd64
sudo chmod +x /usr/local/bin/argocd

##Argocd type LoadBalancer setting
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
export ARGOCD_SERVER=`kubectl get svc argocd-server -n argocd -o json | jq --raw-output .status.loadBalancer.ingress[0].hostname`

##Argocd Simple setting.
ARGO_PWD=`kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d`
aargocd login $ARGOCD_SERVER --username admin --password $ARGO_PWD --insecure #Argocd login

##Argocd External-IP Check
kubectl get svc -n argocd argocd-server

##Argocd Default password Check
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

---

## 7. Arachni

You can install it on the path you want.

```bash
mkdir Arachni
wget https://github.com/Arachni/arachni/releases/download/v1.5.1/arachni-1.5.1-0.5.12-linux-x86_64.tar.gz
tar -xvzf arachni-1.5.1-0.5.12-linux-x86_64.tar.gz

#Arachni_web install
cd arachni-1.5.1-0.5.12/system/arachni_ui_web/bin
bundle install
```

---

## 8. Prometheus & Grafana(Monitoring)

Installation was carried out with Helm chart.

```bash
##Helm install
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
helm version

##Pormetheus&Grafana install
helm repo add stable https://charts.helm.sh/stable
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm search repo prometheus-community
helm install stable prometheus-community/kube-prometheus-stack
kubectl get pods
kubectl get svc
```

- Edit Prometheus Service
    
    ```bash
    kubectl edit svc stable-kube-prometheus-sta-prometheus
    ```
    
    ```yaml
    # Please edit the object below. Lines beginning with a '#' will be ignored,
    # and an empty file will abort the edit. If an error occurs while saving this file will be
    # reopened with the relevant failures.
    #
    apiVersion: v1
    kind: Service
    metadata:
      annotations:
        meta.helm.sh/release-name: stable
        meta.helm.sh/release-namespace: default
      creationTimestamp: "2021-04-09T11:53:24Z"
      finalizers:
      - service.kubernetes.io/load-balancer-cleanup
      labels:
        app: kube-prometheus-stack-prometheus
        app.kubernetes.io/managed-by: Helm
        chart: kube-prometheus-stack-14.5.0
        heritage: Helm
        release: stable
        self-monitor: "true"
      name: stable-kube-prometheus-sta-prometheus
      namespace: default
      resourceVersion: "7902"
      selfLink: /api/v1/namespaces/default/services/stable-kube-prometheus-sta-prometheus
      uid: 9042a504-d25f-4122-b6aa-52ed5e53b576
    spec:
      clusterIP: 100.67.172.242
      externalTrafficPolicy: Cluster
      ports:
      - name: web
        nodePort: 31942
        port: 9090
        protocol: TCP
        targetPort: 9090
      selector:
        app: prometheus
        prometheus: stable-kube-prometheus-sta-prometheus
      sessionAffinity: None
      type: LoadBalancer --- Please fix it.
    ```
    
- Edit Grafana Service
    
    ```bash
    kubectl edit svc stable-grafana
    ```
    
    ```yaml
    # Please edit the object below. Lines beginning with a '#' will be ignored,
    # and an empty file will abort the edit. If an error occurs while saving this file will be
    # reopened with the relevant failures.
    #
    apiVersion: v1
    kind: Service
    metadata:
      annotations:
        meta.helm.sh/release-name: stable
        meta.helm.sh/release-namespace: default
      creationTimestamp: "2021-04-09T11:53:24Z"
      finalizers:
      - service.kubernetes.io/load-balancer-cleanup
      labels:
        app.kubernetes.io/instance: stable
        app.kubernetes.io/managed-by: Helm
        app.kubernetes.io/name: grafana
        app.kubernetes.io/version: 7.4.5
        helm.sh/chart: grafana-6.6.4
      name: stable-grafana
      namespace: default
      resourceVersion: "8222"
      selfLink: /api/v1/namespaces/default/services/stable-grafana
      uid: 7ebeb0da-858f-4232-8904-560e7ce83c5b
    spec:
      clusterIP: 100.65.58.48
      externalTrafficPolicy: Cluster
      ports:
      - name: service
        nodePort: 31258
        port: 80
        protocol: TCP
        targetPort: 3000
      selector:
        app.kubernetes.io/instance: stable
        app.kubernetes.io/name: grafana
      sessionAffinity: None
      type: LoadBalancer --- Please fix it.
    ```
