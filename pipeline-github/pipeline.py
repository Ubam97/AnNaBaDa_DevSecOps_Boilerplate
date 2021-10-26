from github import Github
from gitlab import Gitlab
from slack import Slack
from gradle import Gradle
from maven import Maven
from jacoco import Jacoco
from sonarqube import Sonarqube
from snyk import Snyk
from dockerhub import Dockerhub
from ecr import ECR
from dependency import Dependency
from anchore import Anchore
from trivy import Trivy
from argocd import Argocd
from flux import Flux
from arachni import Arachni
from nikto import Nikto
from variable import Variable
from jenkinsapi.jenkins import Jenkins
import urllib.parse
import requests
import base64
from xml.etree.ElementTree import parse
import urllib
import sys
import json
import os

def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8'))


def xml_modify(filename, **kargs):
    tree = parse(filename)
    root = tree.getroot()
    for tag, value in kargs.items():
        for i in root.iter(tag):
            i.text = value
    tree.write(filename, encoding='UTF-8', xml_declaration=True)

if len(sys.argv) >= 4:
    print("Too many arguments")
elif len(sys.argv) == 3:

    if sys.argv[1] == "start":

        var = Variable(sys.argv[2])
        toolList = var.getToolList()
        pluginList = var.getPluginList()
        stages = []

        if "jenkins" not in toolList:
            print("Not exist jenkins tool in your yaml!")
            exit()

        # 0. Jenkins
        jenkins_url = "http://{}".format(var.getJenkinsData()['url'])
        jenkins = Jenkins(jenkins_url, username=var.getJenkinsData()['username'], password=var.getJenkinsData()['password'], useCrumb=True)
        print("jenkins plugin installing...")
        # jenkins.install_plugins(pluginList)
        print("Done...")

        # 1. Github or Gitlab
        # 1-1. Github webhook configuration

        if "github" in toolList and "gitlab" not in toolList:
            github_apiurl = "https://api.github.com/repos/{0}/{1}/hooks".format(var.getGithubData()['username'], var.getGithubData()['reponame'])
            github_body = {
                "name": "web",
                "events": var.getGithubWebhook()['events'],
                "active": var.getGithubWebhook()['active'],
                "config": {
                    "url": "http://{}/github-webhook/".format(var.getJenkinsData()['url']),
                    "content_type": var.getGithubWebhook()['contenttype']
                }
            }
            github = Github(jenkins, token=var.getGithubData()['token'], cred_id=var.getGithubCred()['id'], cred_description=var.getGithubCred()['description'], url=var.getGithubData()['url'])
            response = github.call_api("POST", github_apiurl, github_body)
            if response.status_code == 201:
                print("Created webhook in Github repository")
            else:
                print("Already exists webhook in github repository")

        # 1-2. Create github credential in jenkins server
            github.createCredential()

        # 1-3. Github configuration in jenkins server
            github.githubConfigure()
            stages.append(github.__dict__['stage'])
            print("Complete Github Configuration")
        
        # GitLab
        elif "gitlab" in toolList and "github" not in toolList:
            # Create gitlab credential in jenkins server
            gitlab = Gitlab(jenkins, token=var.getGitlabData()['token'], url=var.getGitlabData()['url'], username=var.getGitlabData()['username'], password=var.getGitlabData()['password'], cred_id=var.getGitlabCred()['id'], cred_description=var.getGitlabCred()['description'])
            gitlab.createCredential()
            stages.append(gitlab.__dict__['stage'])

        else:
            print("2 or more SCM tool Selected in yaml, Please Check this again!")
            exit()
        # 2. Slack
        def request_test(url, username, password):
            # Build the Jenkins crumb issuer URL
            parsed_url = urllib.parse.urlparse(url)
            crumb_issuer_url = urllib.parse.urlunparse((parsed_url.scheme,
                                                        parsed_url.netloc,
                                                        'crumbIssuer/api/json',
                                                        '', '', ''))
            # Use the same session for all requests
            session = requests.session()

            # GET the Jenkins crumb
            auth = requests.auth.HTTPBasicAuth(username, password)
            r = session.get(crumb_issuer_url, auth=auth)
            json = r.json()
            crumb = {json['crumbRequestField']: json['crumb']}

            # POST to the specified URL
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            headers.update(crumb)
            r = session.post(url, headers=headers, data=payload, auth=auth)

        if "slack" in toolList:
            slack = Slack(jenkins, token=var.getSlackData()['token'], subdomain=var.getSlackData()['subdomain'], channel=var.getSlackData()['channel'], cred_id=var.getSlackCred()['id'], cred_description=var.getSlackCred()['description'])

            # 2-1. Create slack credential in jenkins server
            slack.createCredential()
            stages.append(slack.__dict__['stage'])

            # 2-2. Slack configuration in jenkins server
            slack.slackConfigure()

            # 2-3. Slack Notification Test
            payload = {"room": var.getSlackData()['channel'],
                       # "sendAsText": "true",
                       "teamDomain": var.getSlackData()['subdomain'],
                       "tokenCredentialId": var.getSlackCred()['id']}
            slacktest_url = jenkins_url + \
                '/descriptorByName/jenkins.plugins.slack.SlackNotifier/testConnectionGlobal'
            request_test(slacktest_url, var.getJenkinsData()[
                         'username'], var.getJenkinsData()['password'])
            print("Complete Slack Configuration")
        else:
            print("not exist slack tool in yaml!")

        # 3-1. Gradle
        if "gradle" in toolList:
            gradle_jenkins_configname = "gradle"
            gradle_version = "6.9.1"
            # 3-1. Gradle configuration in jenkins server
            gradle = Gradle()
            gradle.gradleConfigure(gradle_jenkins_configname, gradle_version)
            stages.append(gradle.__dict__['stage'])
            print("Complete Gradle Configuration")

            if "jacoco" in toolList:
                jacoco = Jacoco(tool="gradle")
                stages.append(jacoco.__dict__['stage'])
                print("Complete Jacoco Configuration")

        else:
            print("not exist gradle in yaml!")

        # 3-2. Maven
        if "maven" in toolList:
            maven_jenkins_configname = "maven" 
            maven_version = "3.8.3"
            # 3-1. Gradle configuration in jenkins server
            maven = Maven()
            maven.mavenConfigure(maven_jenkins_configname, maven_version)
            stages.append(maven.__dict__['stage'])
            print("Complete Maven Configuration")

            if "maven" in toolList and "jacoco" in toolList:
                jacoco = Jacoco(tool="maven")
                stages.append(jacoco.__dict__['stage'])
                print("Complete Jacoco Configuration")

        else:
            print("not exist maven in yaml!")
        

        # 4. Sonarqube (with Gradle build)
        if "sonarqube" in toolList and "gradle" in toolList:
            # Add the following to your build.gradle file
            """
            plugins {
                id "org.sonarqube" version "3.3"
            }
            sonarqube {
                properties {
                    property "sonar.projectKey", "sonar_projectname"
                }
            }
            """

            sonar_serverurl = "http://{}".format(var.getSonarqubeData()['url'])
            sonar_servername = "SonarServer"
            sonar_scanner_name = "SonarScanner"
            sonar_scanner_version = "4.6.2.2472"

            # 4-1. Create sonarqube credential in jenkins server
            sonarqube = Sonarqube(jenkins, token=var.getSonarqubeData()['token'], cred_id=var.getSonarqubeCred()[
                                  'id'], cred_description=var.getSonarqubeCred()['description'], url=sonar_serverurl, tool="gradle")
            sonarqube.createCredential()

            # 4-2. Sonarserver and Sonarscanner configuration in jenkins server
            sonarqube.sonarqubeConfigure(
                sonar_servername, sonar_scanner_name, sonar_scanner_version)

            stages.append(sonarqube.__dict__['stage'])
            print("Complete Sonarqube Configuration")

        elif "sonarqube" in toolList and "maven" in toolList:
            # Add the following to your pom.xml file
            """
            <plugins>
                    <plugin>
                            <groupId>org.codehaus.mojo</groupId>
                            <artifactId>sonar-maven-plugin</artifactId>
                    </plugin>
            </plugins>
            """

            sonar_serverurl = "http://{}".format(var.getSonarqubeData()['url'])
            sonar_servername = "SonarServer"
            sonar_scanner_name = "SonarScanner"
            sonar_scanner_version = "4.6.2.2472"

            # 4-1. Create sonarqube credential in jenkins server
            sonarqube = Sonarqube(jenkins, token=var.getSonarqubeData()['token'], cred_id=var.getSonarqubeCred()[
                                  'id'], cred_description=var.getSonarqubeCred()['description'], url=sonar_serverurl, tool="maven")
            sonarqube.createCredential()

            # 4-2. Sonarserver and Sonarscanner configuration in jenkins server
            sonarqube.sonarqubeConfigure(
                sonar_servername, sonar_scanner_name, sonar_scanner_version)

            stages.append(sonarqube.__dict__['stage'])
            print("Complete Sonarqube Configuration")

        elif "sonarqube" in toolList:
            print("나중에 구현")
        else:
            print("not exist sonarqube in yaml!")

        # Snyk
        if "snyk" in toolList:
            snyk_jenkins_configname = "snyk" 
            snyk_version = "latest"
            snyk_update_hours = "24"

            snyk = Snyk(jenkins,token=var.getSnykData()['token'], cred_id=var.getSnykCred()['id'], cred_description=var.getSnykCred()['description'])
            
            # Create Snyk Credential in jenkins
            cred_url = "http://{}/credentials/store/system/domain/_/createCredentials".format(var.getJenkinsData()['url'])
            cred_payload = 'json={"": "7", "credentials": {"scope": "GLOBAL", "token": "%s", "$redact": "token", "id": "%s", "description": "%s", "stapler-class": "io.snyk.jenkins.credentials.DefaultSnykApiToken", "$class": "io.snyk.jenkins.credentials.DefaultSnykApiToken"}, }'%(var.getSnykData()['token'], var.getSnykCred()['id'], var.getSnykCred()['description'])
            
            def request_test(url, username, password):
                # Build the Jenkins crumb issuer URL
                parsed_url = urllib.parse.urlparse(url)
                crumb_issuer_url = urllib.parse.urlunparse((parsed_url.scheme,
                                                            parsed_url.netloc,
                                                            'crumbIssuer/api/json',
                                                            '', '', ''))
                # Use the same session for all requests
                session = requests.session()

                # GET the Jenkins crumb
                auth = requests.auth.HTTPBasicAuth(username, password)
                r = session.get(crumb_issuer_url, auth=auth)
                json = r.json()
                crumb = {json['crumbRequestField']: json['crumb']}

                # POST to the specified URL
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                headers.update(crumb)
                r = session.post(url, headers=headers, data=cred_payload, auth=auth)

            request_test(cred_url, var.getJenkinsData()['username'], var.getJenkinsData()['password'])



            snyk.snykConfigure(snyk_jenkins_configname, snyk_version, snyk_update_hours)
            stages.append(snyk.__dict__['stage'])
            print("Complete Snyk Configuration")
        else:
            print("not exists snyk in yaml!")

        # Dependency
        if "dependency" in toolList:
            dependency_jenkins_configname = "dependency"
            dependency_version = "6.3.1"
            dependency = Dependency()
            dependency.dependencyConfigure(
                dependency_jenkins_configname, dependency_version)
            stages.append(dependency.__dict__['stage'])
            print("Complete Dependency Configuration")
        else:
            print("not exists dependency in yaml!")

        # 5-1 Dockerhub
        # 5-1. Create dockerhub credential with username, password
        if "dockerhub" in toolList:
            dockerhub = Dockerhub(jenkins, cred_id=var.getDockerhubCred()['id'], cred_description=var.getDockerhubCred()[
                                  'description'], username=var.getDockerhubData()['username'], password=var.getDockerhubData()['password'], image=var.getDockerhubData()['image'])
            dockerhub.createCredential()
            

            # 5-2. Create Dockerfile in git repository for docker image build. (You can fix it as you want.)
            # It's based on jdk version 11.
            # If spring boot version 2.5 or higher, add the following content to the build.gradle file.
            # This prevents creating a plane.jar file.
            """
            jar {
                enabled = false
            } 
            """

            if 'gradle' in toolList:
                dockerfile = """FROM openjdk:11-jdk-slim
                ARG JAR_FILE=build/libs/*.jar
                COPY ${JAR_FILE} myspring.jar
                ENTRYPOINT ["java", "-jar", "/myspring.jar"]"""

                content = stringToBase64(dockerfile)

            elif 'maven' in toolList:
                dockerfile = """FROM openjdk:11-jdk-slim
                ARG JAR_FILE=target/*.jar
                COPY ${JAR_FILE} myspring.jar
                ENTRYPOINT ["java", "-jar", "/myspring.jar"]"""

                content = stringToBase64(dockerfile)

            # if SCM tool is Github:
            if "github" in toolList:
                github_requesturl = "https://api.github.com/repos/{}/{}/contents/Dockerfile".format(
                    var.getGithubData()['username'], var.getGithubData()['reponame'])
                body = {
                    "message": "create a default dockerfile",
                    "content": content
                }
                github = Github(jenkins, token=var.getGithubData()['token'], cred_id=var.getGithubCred()[
                                'id'], cred_description=var.getGithubCred()['description'], url=var.getGithubData()['url'])
                response = github.call_api("PUT", github_requesturl, body)
                if response.status_code == 201:
                    print("Created dockerfile in Github repository")
                else:
                    print("Already exists dockerfile in Github repository or Unexpected Error")
                stages.append(dockerhub.__dict__['stage'])
                print("Complete Dockerhub Configuration")
            
            # if SCM tool is Gitlab:
            elif "gitlab" in toolList:
                filepath = "Dockerfile"
                enc_filepath = urllib.parse.quote(filepath, safe="")
                print(enc_filepath)
                url = "https://gitlab.com/api/v4/projects/{}/repository/files/{}".format(str(var.getGitlabData()['projectid']), enc_filepath)
                body = {
                    "branch": "main",
                    "content": dockerfile,
                    "commit_message": "create file by api"
                }
                response = gitlab.call_api("POST", url, body)
                if response.status_code == 201:
                    print("Created dockerfile in Gitlab repository")
                else:
                    print("Already exists dockerfile in Gitlab repository or Unexpected Error")
                stages.append(dockerhub.__dict__['stage'])
                print("Complete Dockerhub Configuration")

        else:
            print("not exist dockerhub in yaml!!")

        # 5-2 ECR
        if "ecr" in toolList:
            ecr = ECR(jenkins, cred_id=var.getECRCred()['id'], cred_description=var.getECRCred()[
                                  'description'], accesskey=var.getECRData()['accesskey'], secretkey=var.getECRData()['secretkey'], account=var.getECRData()['account'], region=var.getECRData()['region'], image=var.getECRData()['image'])
            ecr.createCredential()

            if 'gradle' in toolList:
                dockerfile = """FROM openjdk:11-jdk-slim
                ARG JAR_FILE=build/libs/*.jar
                COPY ${JAR_FILE} myspring.jar
                ENTRYPOINT ["java", "-jar", "/myspring.jar"]"""

                content = stringToBase64(dockerfile)

            elif 'maven' in toolList:
                dockerfile = """FROM openjdk:11-jdk-slim
                ARG JAR_FILE=target/*.jar
                COPY ${JAR_FILE} myspring.jar
                ENTRYPOINT ["java", "-jar", "/myspring.jar"]"""

                content = stringToBase64(dockerfile)

            # if SCM tool is Github:
            if "github" in toolList:
                github_requesturl = "https://api.github.com/repos/{}/{}/contents/Dockerfile".format(
                    var.getGithubData()['username'], var.getGithubData()['reponame'])
                body = {
                    "message": "create a default dockerfile",
                    "content": content
                }
                github = Github(jenkins, token=var.getGithubData()['token'], cred_id=var.getGithubCred()[
                                'id'], cred_description=var.getGithubCred()['description'], url=var.getGithubData()['url'])
                response = github.call_api("PUT", github_requesturl, body)
                if response.status_code == 201:
                    print("Created dockerfile in Github repository")
                else:
                    print("Already exists dockerfile in Github repository or Unexpected Error")
                stages.append(ecr.__dict__['stage'])
                print("Complete ECR Configuration")
            
            # if SCM tool is Gitlab:
            elif "gitlab" in toolList:
                filepath = "Dockerfile"
                enc_filepath = urllib.parse.quote(filepath, safe="")
                print(enc_filepath)
                url = "https://gitlab.com/api/v4/projects/{}/repository/files/{}".format(str(var.getGitlabData()['projectid']), enc_filepath)
                body = {
                    "branch": "main",
                    "content": dockerfile,
                    "commit_message": "create file by api"
                }
                response = gitlab.call_api("POST", url, body)
                if response.status_code == 201:
                    print("Created dockerfile in Gitlab repository")
                else:
                    print("Already exists dockerfile in Gitlab repository or Unexpected Error")
                stages.append(ecr.__dict__['stage'])
                print("Complete ECR Configuration")

        else:
            print("not exist ECR in yaml!!")

        # Anchore
        if "anchore" in toolList and "dockerhub" in toolList:
            anchore_url = "http://{}".format(var.getAnchoreData()['url'])
            anchore = Anchore(jenkins, tool="dockerhub", cred_id=var.getAnchoreCred()['id'], cred_description=var.getAnchoreCred()['description'], url=anchore_url, username=var.getAnchoreData()['username'], password=var.getAnchoreData()['password'], image=var.getAnchoreData()['image'])
            anchore.anchoreConfigure()
            anchore.createCredential()
            stages.append(anchore.__dict__['stage'])
            print("Complete Anchore Configuration")
            
        elif "anchore" in toolList and "ecr" in toolList:
            anchore_url = "http://{}".format(var.getAnchoreData()['url'])
            anchore = Anchore(jenkins, tool="ecr", accesskey=var.getECRData()['accesskey'], secretkey=var.getECRData()['secretkey'], cred_id=var.getAnchoreCred()['id'], cred_description=var.getAnchoreCred()['description'], url=anchore_url, username=var.getAnchoreData()['username'], password=var.getAnchoreData()['password'], image=var.getAnchoreData()['image'])
            anchore.anchoreConfigure()
            anchore.createCredential()
            stages.append(anchore.__dict__['stage'])
            print("Complete Anchore Configuration")
        else:
            print("not exits anchore in yaml!")
            
        # Trivy
        if "trivy" in toolList and "dockerhub" in toolList:
            trivy = Trivy(jenkins, tool="dockerhub", image=var.getTrivyData()['image'])
            stages.append(trivy.__dict__['stage'])
            print("Complete Trivy Configuration")

        elif "trivy" in toolList and "ecr" in toolList:
            trivy = Trivy(jenkins, tool="ecr", image=var.getTrivyData()['image'], region=var.getECRData()['region'], account=var.getECRData()['account'])
            stages.append(trivy.__dict__['stage'])
            print("Complete Trivy Configuration")

        else:
            print("not exits trivy in yaml!")


        # 6. ArgoCD
        if "argocd" in toolList:

            # 6-1. Create ArgoCD credential with SSH key

            # if SCM tool is github:
            if "github" in toolList:
                # Set github and gitlab data to environment variable in jenkins docker.
                argocd = Argocd(jenkins, cred_id=var.getArgocdCred()['id'], cred_description=var.getArgocdCred()['description'], cred_sshkey=var.getArgocdData()[
                                'ssh_key'], cred_username=var.getArgocdData()['username'], masternode_url=var.getArgocdData()['url'], scm_url=var.getGithubData()['url'])
            elif "gitlab" in toolList:
                # Set github and gitlab data to environment variable in jenkins docker.
                argocd = Argocd(jenkins, cred_id=var.getArgocdCred()['id'], cred_description=var.getArgocdCred()['description'], cred_sshkey=var.getArgocdData()[
                                'ssh_key'], cred_username=var.getArgocdData()['username'], masternode_url=var.getArgocdData()['url'], scm_url=var.getGitlabData()['url'])

            argocd.createCredential()

            # 6-2. Create ArgoCD config yaml in git repository
            if "dockerhub" in toolList:
                argocd_yamldir = "templates"
                argocd_deployments_yaml = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: test
  labels:
    app: test
spec:
  replicas: 1
  selector:
    matchLabels:
      app: test
  template:
    metadata:
      labels:
        app: test
    spec:
      containers:
        - name: test
          image: {}:latest
          ports:
            - containerPort: 80""".format(var.getDockerhubData()['image'])

                argocd_svc_yaml = """apiVersion: v1
kind: Service
metadata:
  name: test
spec:
  type: LoadBalancer
  selector:
    app: test
  ports:
    - port: 80
      targetPort: 8080"""

            elif "ecr" in toolList:
                argocd_yamldir = "templates"
                argocd_deployments_yaml = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: test
  labels:
    app: test
spec:
  replicas: 1
  selector:
    matchLabels:
      app: test
  template:
    metadata:
      labels:
        app: test
    spec:
      containers:
        - name: test
          image: {}:latest
          ports:
            - containerPort: 80""".format(var.getECRData()['image'])

                argocd_svc_yaml = """apiVersion: v1
kind: Service
metadata:
  name: test
spec:
  type: LoadBalancer
  selector:
    app: test
  ports:
    - port: 80
      targetPort: 8080"""
            
            deployments = stringToBase64(argocd_deployments_yaml)
            svc = stringToBase64(argocd_svc_yaml)

            # if SCM tool is github:
            if "github" in toolList:
                github_requesturl_argocd_deployments = "https://api.github.com/repos/{}/{}/contents/{}/deployments.yaml".format(
                    var.getGithubData()['username'], var.getGithubData()['reponame'], argocd_yamldir)
                body1 = {
                    "message": "create a default deployments yaml",
                    "content": deployments
                }
                github_requesturl_argocd_svc = "https://api.github.com/repos/{}/{}/contents/{}/svc.yaml".format(
                    var.getGithubData()['username'], var.getGithubData()['reponame'], argocd_yamldir)
                body2 = {
                    "message": "create a default svc yaml",
                    "content": svc
                }
                github = Github(jenkins, token=var.getGithubData()['token'], cred_id=var.getGithubCred()[
                                'id'], cred_description=var.getGithubCred()['description'], url=var.getGithubData()['url'])
                response1 = github.call_api(
                    "PUT", github_requesturl_argocd_deployments, body1)
                if response1.status_code == 201:
                    print("Created argocd deployment.yaml in Github repository")
                else:
                    print("Already exists argocd deployment.yaml in github repository")
                response2 = github.call_api(
                    "PUT", github_requesturl_argocd_svc, body2)
                if response2.status_code == 201:
                    print("Created argocd svc.yaml in Github repository")
                else:
                    print("Already exists argocd svc.yaml in github repository")

                stages.append(argocd.__dict__['stage'])
                print("Complete Argocd Configuration")
            
            # if SCM tool is gitlab:
            elif "gitlab" in toolList:
                filepath = "{}/deployments.yaml".format(argocd_yamldir)
                enc_filepath = urllib.parse.quote(filepath, safe="")
                url = "https://gitlab.com/api/v4/projects/{}/repository/files/{}".format(str(var.getGitlabData()['projectid']), enc_filepath)
                body = {
                    "branch": "main",
                    "content": argocd_deployments_yaml,
                    "commit_message": "create file by api"
                }
                response = gitlab.call_api("POST", url, body)
                if response.status_code == 201:
                    print("Created deployments.yaml in Gitlab repository")
                else:
                    print("Already exists deployments.yaml in Gitlab repository or Unexpected Error")

                filepath = "{}/svc.yaml".format(argocd_yamldir)
                enc_filepath = urllib.parse.quote(filepath, safe="")
                url = "https://gitlab.com/api/v4/projects/{}/repository/files/{}".format(str(var.getGitlabData()['projectid']), enc_filepath)
                body = {
                    "branch": "main",
                    "content": argocd_svc_yaml,
                    "commit_message": "create file by api"
                }
                response = gitlab.call_api("POST", url, body)
                if response.status_code == 201:
                    print("Created svc.yaml in Gitlab repository")
                else:
                    print("Already exists svc.yaml in Gitlab repository or Unexpected Error")

                stages.append(argocd.__dict__['stage'])
                print("Complete Argocd Configuration")

        else:
            print("not exist argocd in yaml!")

        # 6. Flux
        if "flux" in toolList:

            flux = Flux(jenkins, masternode_url=var.getFluxData()['url'], cred_sshkey=var.getFluxData()['ssh_key'], cred_id=var.getFluxCred()['id'], cred_description=var.getFluxCred()['description'], cred_username=var.getFluxData()['username'])
            flux.createCredential()

            # 6-2. Create Flux config yaml in git repository
            if "dockerhub" in toolList:
                flux_yamldir = "templates"
                flux_deployments_yaml = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: test
  labels:
    app: test
spec:
  replicas: 1
  selector:
    matchLabels:
      app: test
  template:
    metadata:
      labels:
        app: test
    spec:
      containers:
        - name: test
          image: {}:latest
          ports:
            - containerPort: 80""".format(var.getDockerhubData()['image'])

                flux_svc_yaml = """apiVersion: v1
kind: Service
metadata:
  name: test
spec:
  type: LoadBalancer
  selector:
    app: test
  ports:
    - port: 80
      targetPort: 8080"""

            elif "ecr" in toolList:
                flux_yamldir = "templates"
                flux_deployments_yaml = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: test
  labels:
    app: test
spec:
  replicas: 1
  selector:
    matchLabels:
      app: test
  template:
    metadata:
      labels:
        app: test
    spec:
      containers:
        - name: test
          image: {}:latest
          ports:
            - containerPort: 80""".format(var.getECRData()['image'])

                flux_svc_yaml = """apiVersion: v1
kind: Service
metadata:
  name: test
spec:
  type: LoadBalancer
  selector:
    app: test
  ports:
    - port: 80
      targetPort: 8080"""
            
            deployments = stringToBase64(flux_deployments_yaml)
            svc = stringToBase64(flux_svc_yaml)

            # if SCM tool is github:
            if "github" in toolList:
                github_requesturl_flux_deployments = "https://api.github.com/repos/{}/{}/contents/{}/deployments.yaml".format(
                    var.getGithubData()['username'], var.getGithubData()['reponame'], flux_yamldir)
                body1 = {
                    "message": "create a default deployments yaml",
                    "content": deployments
                }
                github_requesturl_flux_svc = "https://api.github.com/repos/{}/{}/contents/{}/svc.yaml".format(
                    var.getGithubData()['username'], var.getGithubData()['reponame'], flux_yamldir)
                body2 = {
                    "message": "create a default svc yaml",
                    "content": svc
                }
                github = Github(jenkins, token=var.getGithubData()['token'], cred_id=var.getGithubCred()[
                                'id'], cred_description=var.getGithubCred()['description'], url=var.getGithubData()['url'])
                response1 = github.call_api(
                    "PUT", github_requesturl_flux_deployments, body1)
                if response1.status_code == 201:
                    print("Created flux deployment.yaml in Github repository")
                else:
                    print("Already exists flux deployment.yaml in github repository")
                response2 = github.call_api(
                    "PUT", github_requesturl_flux_svc, body2)
                if response2.status_code == 201:
                    print("Created flux svc.yaml in Github repository")
                else:
                    print("Already exists flux svc.yaml in github repository")

                stages.append(flux.__dict__['stage'])
                print("Complete Flux Configuration")
            
            # if SCM tool is gitlab:
            elif "gitlab" in toolList:
                filepath = "{}/deployments.yaml".format(flux_yamldir)
                enc_filepath = urllib.parse.quote(filepath, safe="")
                url = "https://gitlab.com/api/v4/projects/{}/repository/files/{}".format(str(var.getGitlabData()['projectid']), enc_filepath)
                body = {
                    "branch": "main",
                    "content": flux_deployments_yaml,
                    "commit_message": "create file by api"
                }
                response = gitlab.call_api("POST", url, body)
                if response.status_code == 201:
                    print("Created deployments.yaml in Gitlab repository")
                else:
                    print("Already exists deployments.yaml in Gitlab repository or Unexpected Error")

                filepath = "{}/svc.yaml".format(flux_yamldir)
                enc_filepath = urllib.parse.quote(filepath, safe="")
                url = "https://gitlab.com/api/v4/projects/{}/repository/files/{}".format(str(var.getGitlabData()['projectid']), enc_filepath)
                body = {
                    "branch": "main",
                    "content": flux_svc_yaml,
                    "commit_message": "create file by api"
                }
                response = gitlab.call_api("POST", url, body)
                if response.status_code == 201:
                    print("Created svc.yaml in Gitlab repository")
                else:
                    print("Already exists svc.yaml in Gitlab repository or Unexpected Error")

                stages.append(flux.__dict__['stage'])
                print("Complete Flux Configuration")

        else:
            print("not exist flux in yaml!")

        # 7. Arachni
        # 7-1. Add arachni pipeline script in jenkinsfile
        if "arachni" in toolList:
            if "argocd" in toolList and var.getArachniData()['url'] != None:
                arachni = Arachni(cred_id=var.getArgocdCred()['id'], masternode_url=var.getArgocdData()['url'], node_url=var.getArachniData()['url'])
                stages.append(arachni.__dict__['stage'])
                print("Complete Arachni Configuration")

            elif "flux" in toolList and var.getArachniData()['url'] != None:
                arachni = Arachni(cred_id=var.getFluxCred()['id'], masternode_url=var.getFluxData()['url'], node_url=var.getArachniData()['url'])
                stages.append(nikto.__dict__['stage'])
                print("Complete Nikto Configuration")

            elif "argocd" in toolList and var.getArachniData()['url'] == None:
                arachni = Arachni(cred_id=var.getArgocdCred()['id'], masternode_url=var.getArgocdData()['url'], node_url="{Add the deployed node URL here}")
                stages.append(arachni.__dict__['stage'])
                print("Complete Arachni Configuration")
  
            elif "flux" in toolList and var.getArachniData()['url'] == None:
                arachni = Arachni(cred_id=var.getFluxCred()['id'], masternode_url=var.getFluxCred()['url'], node_url="{Add the deployed node URL here}")
                stages.append(nikto.__dict__['stage'])
                print("Complete Nikto Configuration")
        
        # 7. Nikto
        # 7-1. Add nikto pipeline script in jenkinsfile
        if "nikto" in toolList:
            if var.getNiktoData()['url'] != None:
                nikto = Nikto(node_url=var.getNiktoData()['url'])
                stages.append(nikto.__dict__['stage'])
                print("Complete Nikto Configuration")
            else:
                nikto = Nikto(node_url="{Add the deployed node URL here}")
                stages.append(nikto.__dict__['stage'])
                print("Complete Nikto Configuration")

        # 8. Pipeline
        # 8-1. Create pipeline script in github repository.
        if len(toolList) > 0:
            print("jenkins server restarting.......")
            # jenkins.safe_restart()
            print("Completed jenkins server restarting!")

            pipelineScript = "jenkinsfile"
            pipelineName = "PIPELINEJOB"
            stages = '\n\t'.join(stages)

            jenkinsfile = """pipeline {
                agent any
                stages {
                    %s
                }
            }""" % (stages)

            # if SCM tool is github:
            if "github" in toolList:
                github_jenkinsfile = stringToBase64(jenkinsfile)
                github_requesturl_pipeline_script = "https://api.github.com/repos/{}/{}/contents/{}".format(
                    var.getGithubData()['username'], var.getGithubData()['reponame'], pipelineScript)
                body = {
                    "message": "create a pipeline script",
                    "content": github_jenkinsfile
                }
                github = Github(jenkins, token=var.getGithubData()['token'], cred_id=var.getGithubCred()[
                                'id'], cred_description=var.getGithubCred()['description'], url=var.getGithubData()['url'])
                response = github.call_api(
                    "PUT", github_requesturl_pipeline_script, body)
                if response.status_code == 201:
                    print("Created jenkinsfile in Github repository")
                else:
                    print("Already exists jenkinsfile in github repository")

            elif "gitlab" in toolList:

                gitlab_apiurl = "https://gitlab.com/api/v4/projects/{}/integrations/jenkins".format(str(var.getGitlabData()['projectid']))
                gitlab_apibody = {
                    "jenkins_url": jenkins_url,
                    "project_name": pipelineName, # jenkins pipeline name
                    "username": var.getJenkinsData()['username'], # jenkins username
                    "password": var.getJenkinsData()['password'], # jenkins password
                    "push_events": True
                }
                response = gitlab.call_api("PUT", gitlab_apiurl, gitlab_apibody)
                print(response.status_code, "Compelte Integration Jenkins in Gitlab")

                filepath = pipelineScript
                enc_filepath = urllib.parse.quote(filepath, safe="")
                url = "https://gitlab.com/api/v4/projects/{}/repository/files/{}".format(str(var.getGitlabData()['projectid']), enc_filepath)
                body = {
                    "branch": "main",
                    "content": jenkinsfile,
                    "commit_message": "create file by api"
                }
                response = gitlab.call_api("POST", url, body)
                if response.status_code == 201:
                    print("Created jenkinsfile in Gitlab repository")
                else:
                    print("Already exists jenkinsfile in Gitlab repository or Unexpected Error")

            # 8-2. Create jenkins pipeline
            # if SCM tool is github:
            if "github" in toolList:
                xml_modify("/home/ec2-user/AnNaBaDa_DevSecOps_Boilerplate/pipeline-github/githubPipelineConfig.xml", url=var.getGithubData()['url'], scriptPath=pipelineScript)
                with open("/home/ec2-user/AnNaBaDa_DevSecOps_Boilerplate/pipeline-github/githubPipelineConfig.xml", 'r') as xml:
                    pipeline_configXml = xml.read()
                try:
                    jenkins.create_multibranch_pipeline_job(jobname=pipelineName, xml=pipeline_configXml)
                except Exception as e:
                    pass
            elif "gitlab" in toolList:
                xml_modify("/home/ec2-user/AnNaBaDa_DevSecOps_Boilerplate/pipeline-github/gitlabPipelineConfig.xml", url=var.getGitlabData()['url'], scriptPath=pipelineScript, credentialsId=var.getGitlabCred()['id'])
                with open("/home/ec2-user/AnNaBaDa_DevSecOps_Boilerplate/pipeline-github/gitlabPipelineConfig.xml", 'r') as xml:
                    pipeline_configXml = xml.read()
                try:
                    jenkins.create_multibranch_pipeline_job(jobname=pipelineName, xml=pipeline_configXml)
                except Exception as e:
                    pass
            print("--------------The End--------------")

    elif sys.argv[1] == "reset":
        print("Reset is in progress...")
        var = Variable(sys.argv[2])
        # Jenkins
        jenkins_url = "http://{}".format(var.getJenkinsData()['url'])
        jenkins = Jenkins(jenkins_url, username=var.getJenkinsData()[
                          'username'], password=var.getJenkinsData()['password'], useCrumb=True)
        jobList = jenkins.get_jobs_list()
        for job in jobList:
            jenkins.delete_job(job)
            print("Deleted job: \"{}\"".format(job))

        def deleteFileInRepository(filepath):
            github_apiurl = "https://api.github.com/repos/{0}/{1}/contents/{2}".format(
                var.getGithubData()['username'], var.getGithubData()['reponame'], filepath)
            github_body = {}
            github = Github(jenkins, token=var.getGithubData()['token'], cred_id=var.getGithubCred()[
                            'id'], cred_description=var.getGithubCred()['description'], url=var.getGithubData()['url'])
            response = github.call_api("GET", github_apiurl, github_body)

            if response.status_code == 200:
                print("{} exist in github repository".format(filepath))
                jsondata = json.loads(response.text)
                sha = jsondata['sha']

                # delete file in github repository
                url = "https://api.github.com/repos/{0}/{1}/contents/{2}".format(
                    var.getGithubData()['username'], var.getGithubData()['reponame'], filepath)
                body = {
                    "message": "delete file using api",
                    "sha": sha
                }
                response = github.call_api("DELETE", github_apiurl, body)
                if response.status_code == 200:
                    print("Complete Delete! \"{}\"".format(filepath))
                else:
                    print("Failed delete \"{}\"".format(filepath))
            else:
                print("not exist {} in github repository".format(filepath))

        # Delete github file in repository for reset, Wirte it properly later.
        github_repoAddedFile = ["jenkinsfile", "Dockerfile",
                                "templates/deployments.yaml", "templates/svc.yaml"]
        for file in github_repoAddedFile:
            deleteFileInRepository(file)

    else:
        print("Command argument requires \"start\" or \"reset\".")

else:
    print("Error. Invalid format. More Argument needed,")
