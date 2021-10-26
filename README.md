# AnNaBaDa_DevSecOps_Boilerplate
DevSecOps Pipeline auto integration

CCCR Project
---

<h1>Tool Install Guide</h1>

---

**Warning :  Cloud Platform = AWS, Instance=t2.xlarge(xlarge or larger recommended) OS=Ubuntu 20.04LTS**

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

## 2. Jenkins & Trivy & Nikto Install

**Plug-in installation list.**

- Gradle Plugin
- Anchore Container Image Scanner Plugin
- SonarQube Scanner
- OWASP Dependency-Check Plugin
- SSH Agent Plugin
- Gitlab
- Github
- Amazon ECR plugin
- Pipeline: AWS Steps
- Snyk Security Plugin

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
**##anchore-cli Install**
RUN apt-get update 
RUN apt-get install python3-pip
RUN pip3 install anchorecli
**## trivy Install**
RUN apt-get -y install wget
RUN apt-get -y install rpm
RUN wget https://github.com/aquasecurity/trivy/releases/download/v0.20.1/trivy_0.20.1_Linux-64bit.deb
RUN dpkg -i trivy_0.20.1_Linux-64bit.deb
**## Nikto Install**
RUN git clone https://github.com/sullo/nikto

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

**Warning :  Please edit "build.gradle". -Gradle build **


```makefile
test {
	useJUnitPlatform()
}
```

## 4. Jacoco Setting


**Warning :  Please edit "build.gradle". -Gradle build **


```build.gradle
plugins {
    id 'jacoco'
}
```

**Warning :  Please edit "Pom.xml". -maven build **

```pom.xml
		<plugin>
            		<groupId>org.jacoco</groupId>
            		<artifactId>jacoco-maven-plugin</artifactId>
            		<version>0.8.5</version>
            		<executions>
                		<execution>
                    		<id>jacoco-initialize</id>
                    		<goals>
                        		<goal>prepare-agent</goal>
                    		</goals>
                		</execution>
                		<execution>
                	    	<id>jacoco-site</id>
                	    	<phase>test</phase>
                	    	<goals>
                	        	<goal>report</goal>
                	    	</goals>
                		</execution>
            		</executions>
        	</plugin>
```



## 5. SonarQube

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
    image: sonarqube:9.1.0-community ##You can install the version you want.
    container_name: sonarqube9.1.0
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

**Warning :  Please edit "build.gradle"-Gradle build.**
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

**Warning :  Please edit "pom.xml.-Maven build.**
```pom.xml
		<plugins>
                    <plugin>
                    	<groupId>org.codehaus.mojo</groupId>
                        <artifactId>sonar-maven-plugin</artifactId>
                    </plugin>
            	</plugins>
```

**How to link dependency check in sonarquube**

![Untitled](https://user-images.githubusercontent.com/88227041/136323651-1bd03676-6688-4307-bfe4-ffc973da7c6d.png)

---

## 6. Anchore

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
[EKS-Cluster Buid it](https://github.com/eub456/AnNaBaDa_DevSecOps_Boilerplate/tree/main/terraform-eks#readme)

**Cloud Platform = AWS, Instance=t2.large OS=Amazon linux**


## 7. Snyk Setting
**Add apitoken issued by snyk to Jenkins.**

1. Jenkins → Global tool configuration
![image](https://user-images.githubusercontent.com/88227041/138830164-5ed414b3-cb4e-4057-8cf3-e72672df446a.png)
2. Snyk API Token get
![image](https://user-images.githubusercontent.com/88227041/138831186-092fc906-e3f6-41f9-b890-be9e0ea0a8ce.png)
3. create jenkins credential



## 7. ArgoCD(Deploy Tool)
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

## 8. Arachni

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

## 9. Prometheus & Grafana(Monitoring)
**Grafana can log in and get the graph you want and monitor it.**

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

## 10. EFK Stack Install
**After installation, you can set it to the setting you want.**

- Edit elasticsearch.yaml

```elasticsearch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: elasticsearch
  namespace: elastic
  labels:
    app: elasticsearch
spec:
  replicas: 1
  selector:
    matchLabels:
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
    spec:
      containers:
      - name: elasticsearch
        image: elastic/elasticsearch:7.14.1
        env:
        - name: discovery.type
          value: single-node
        ports:
        - containerPort: 9200
        - containerPort: 9300
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: elasticsearch
  name: elasticsearch-svc
  namespace: elastic
spec:
  ports:
  - name: elasticsearch-rest
    nodePort: 30920
    port: 9200
    protocol: TCP
    targetPort: 9200
  - name: elasticsearch-nodecom
    nodePort: 30930
    port: 9300
    protocol: TCP
    targetPort: 9300
  selector:
    app: elasticsearch
  type: LoadBalancer
  ```
  
  - Edit fluentd.yaml
 
 ```fluentd.yaml
 ---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: fluentd
  namespace: kube-system

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: fluentd
  namespace: kube-system
rules:
- apiGroups:
  - ""
  resources:
  - pods
  - namespaces
  verbs:
  - get
  - list
  - watch

---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: fluentd
roleRef:
  kind: ClusterRole
  name: fluentd
  apiGroup: rbac.authorization.k8s.io
subjects:
- kind: ServiceAccount
  name: fluentd
  namespace: kube-system
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: kube-system
  labels:
    k8s-app: fluentd-logging
    version: v1
spec:
  selector:
    matchLabels:
      k8s-app: fluentd-logging
      version: v1
  template:
    metadata:
      labels:
        k8s-app: fluentd-logging
        version: v1
    spec:
      serviceAccount: fluentd
      serviceAccountName: fluentd
      tolerations:
      - key: node-role.kubernetes.io/master
        effect: NoSchedule
      containers:
      - name: fluentd
        image: fluent/fluentd-kubernetes-daemonset:v1-debian-elasticsearch
        env:
        - name:  FLUENT_ELASTICSEARCH_HOST
          value: elasticsearch-svc.elastic
        - name:  FLUENT_ELASTICSEARCH_PORT
          value: "9200"
        - name: FLUENT_ELASTICSEARCH_SCHEME
          value: http
        resources:
          limits:
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 200Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      terminationGracePeriodSeconds: 30
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

- Edit kibana.yaml

```kibana.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kibana
  namespace: elastic
  labels:
    app: kibana
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kibana
  template:
    metadata:
      labels:
        app: kibana
    spec:
      containers:
      - name: kibana
        image: elastic/kibana:7.14.1
        env:
        - name: SERVER_NAME
          value: kibana.kubenetes.example.com
        - name: ELASTICSEARCH_HOSTS
          value: http://elasticsearch-svc:9200
        ports:
        - containerPort: 5601
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: kibana
  name: kibana-svc
  namespace: elastic
spec:
  ports:
  - nodePort: 30561
    port: 5601
    protocol: TCP
    targetPort: 5601
  selector:
    app: kibana
  type: LoadBalancer
  ```
  
  - Edit Namespace.yaml
```Namespace.yaml
  apiVersion: v1
kind: Namespace
metadata:
  name: elastic
```

**Install Command**
```
kubectl apply -f efk/*

```

<br/>
<br/>
<br/>

YAML (Just put the tools you need in the yaml file.)
=============
### 1. jenkins yaml data (Required)

![image](https://user-images.githubusercontent.com/50852749/136325068-b301114f-1e6e-4fcc-81b6-0a5b09fbfec7.png)

Add jenkins data in your data.yaml!
<br/>
<br/>
<br/>

### 2. github yaml data (Required) (gitlab and bitbucket will be added.)

Get Github Personal Access Token

![image](https://user-images.githubusercontent.com/50852749/136324068-2d3a488d-b4c2-46c9-89c9-0552cca90aac.png)

![image](https://user-images.githubusercontent.com/50852749/136324374-f66574ee-24f7-47db-84c0-48f8fd266386.png)

![image](https://user-images.githubusercontent.com/50852749/136324684-033e9742-236b-47c9-9076-3de83ca1e380.png)

![image](https://user-images.githubusercontent.com/50852749/136324708-2628bf62-b35f-43d1-aaf3-72ac1cc22b2f.png)

![image](https://user-images.githubusercontent.com/50852749/136324804-4bb913d8-2f33-4d67-976b-e2f12d590c8b.png)

Add token and others in your data.yaml!
<br/>
<br/>
<br/>

### 3. slack yaml data (optional)

Get Slack subdomain, channel, token

![image](https://user-images.githubusercontent.com/50852749/136326141-ee03e997-ed10-4fa6-bda8-98a7f99ace6d.png)

![image](https://user-images.githubusercontent.com/50852749/136326211-d4dc2084-9c54-4c26-b035-03d5c2242478.png)

![image](https://user-images.githubusercontent.com/50852749/136326242-316f4db4-3bf5-4c8f-bb32-a654cc6332e0.png)
Get the channel name

![image](https://user-images.githubusercontent.com/50852749/136326299-eb59f929-25f9-4cd5-917d-95a817003e67.png)
Get the subdomain and token data

![image](https://user-images.githubusercontent.com/50852749/136326349-508ec9bd-d9e3-4628-a888-4c578c45bb48.png)

Add Slack data in your data.yaml!
<br/>
<br/>
<br/>

### 3. gradle yaml data (optional)

![image](https://user-images.githubusercontent.com/50852749/136328195-0b60e2d7-5b60-4d96-9ed1-c83b7e71483d.png)  
Just put gradle tool in data.yaml like this.
<br/>
<br/>
<br/>

### 4. sonarqube yaml data (optional)

Get sonarqube token

![image](https://user-images.githubusercontent.com/50852749/136327552-1cd82e30-8b26-4354-ba32-5a2c3d9b09cd.png)
Go to your sonarqube web ui

![image](https://user-images.githubusercontent.com/50852749/136327618-3dcfba00-2b58-44e4-91c1-8f513af10d39.png)  
Get the sonarqube token here

![image](https://user-images.githubusercontent.com/50852749/136327759-16538c8f-1aa7-45f5-9780-f4454db06521.png)  

Add Sonarqube token in your data.yaml!

#### Caution
If you want to use gradle and sonacube together, add the following content to your build.gradle file.  
![image](https://user-images.githubusercontent.com/50852749/136328600-4def5149-9807-49b4-9c38-b2e793c8c236.png)
<br/>
<br/>
<br/>

### 5. OAWSP dependency check yaml data (optional)
![image](https://user-images.githubusercontent.com/50852749/136330882-d5ced98e-06e1-4904-a283-63dc41ca722d.png)
Just put dependency check tool in data.yaml like this.
<br/>
<br/>
<br/>

### 6. Dockerhub yaml data (optional)
![image](https://user-images.githubusercontent.com/50852749/136331133-e47208ba-1612-41ae-a202-721d41df7315.png)  
Sign up dockerhub! and get the username and password 
<br/>
<br/>
![image](https://user-images.githubusercontent.com/50852749/136331017-17518348-b850-49db-816a-40730beddb80.png)  
Add build image name ex) username/imagename
<br/>
<br/>
<br/>

### 7. Anchore yaml data (optional, If used, dockerhub is required)
![image](https://user-images.githubusercontent.com/50852749/136331535-def1a71a-8b36-441a-a178-6c30f0885cd0.png)  
Look at the previous installation process, install it, and add data in data.yaml
<br/>
<br/>
<br/>

### 8. Argocd yaml data (optional, If used, dockerhub is required)
![image](https://user-images.githubusercontent.com/50852749/136331735-85691822-c31b-41e0-9025-61752afd8226.png)  
Look at the previous installation process, install it, and add data in data.yaml  
It is the url of the master node where argocd is installed.  
<br/>
<br/>
<br/>

Run this Project (2 Ways)
=============
### 1. Run Python Code
```bash

    cd ~/AnNaBaDa_DevSecOps_Boilerplate/pipeline-github
    
    #start
    python3 pipeline.py start data.yaml

    #reset
    python3 pipeline.py reset data.yaml
```
<br/>
<br/>
<br/>

### 2. Run Webserver

![31](https://user-images.githubusercontent.com/78459621/136342016-5631f604-84fe-46c2-a819-14208150849b.PNG)

Pre-installation.

pip3 install flask

Go from the clone directory to the web-server directory in Github run python3 main.py

![32](https://user-images.githubusercontent.com/78459621/136342001-21dd71d9-f0e8-40d1-a44a-8fa922322f0d.PNG)

IP address:5500 in the URI address window, the screen appears.

![34](https://user-images.githubusercontent.com/78459621/136342007-1743781a-b18f-4e97-81c0-b5891665d9ef.PNG)

You can only upload files in .yaml format or .yml format from the YAML upload page.

![35](https://user-images.githubusercontent.com/78459621/136342009-8a545c9f-29e6-40f9-bd5c-f2a892e0392a.PNG)

On the download YAML page, you can view the example.yaml file and write yaml according to the form.

You can delete or download the uploaded yaml file.

![37](https://user-images.githubusercontent.com/78459621/136342010-912b12c2-0747-4f3c-b75c-4124e5f0789f.PNG)

If you enter and execute the uploaded yaml file, read the contents of yaml and link them.

![39](https://user-images.githubusercontent.com/78459621/136342012-a4b6ca57-f95c-4aae-a464-aa7c61e6c2e0.PNG)

The result screen.
