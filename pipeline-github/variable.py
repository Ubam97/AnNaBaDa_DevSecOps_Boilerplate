import yaml

class Variable():
    def __init__(self, configYaml):
        self.toolList = []
        self.pluginList = []
        with open(configYaml) as f:
            file = yaml.load(f, Loader=yaml.FullLoader)

        for dict in file:
            if dict['tool']['name'] == "jenkins":
                self.toolList.append("jenkins")
                self.jenkins_data = dict['tool']['data']

            elif dict['tool']['name'] == "github":
                self.toolList.append("github")
                self.pluginList.append("github-pullrequest@0.3.0")
                self.github_data = dict['tool']['data']
                self.github_cred = dict['tool']['credential']
                self.github_webhook = dict['tool']['webhook']

            elif dict['tool']['name'] == 'slack':
                self.toolList.append("slack")
                self.pluginList.append("slack@2.48")
                self.slack_data = dict['tool']['data']
                self.slack_cred = dict['tool']['credential']

            elif dict['tool']['name'] == 'gradle':
                self.toolList.append("gradle")

            elif dict['tool']['name'] == 'sonarqube':
                self.toolList.append("sonarqube")
                self.pluginList.append("sonar@2.13.1")
                self.sonar_data = dict['tool']['data']
                self.sonar_cred = dict['tool']['credential']

            elif dict['tool']['name'] == 'dockerhub':
                self.toolList.append("dockerhub")
                self.pluginList.append("docker-plugin@1.2.3")
                self.pluginList.append("docker-workflow@1.26")
                self.dockerhub_data = dict['tool']['data']
                self.dockerhub_cred = dict['tool']['credential'] 

            elif dict['tool']['name'] == 'anchore':
                self.toolList.append("anchore")
                self.pluginList.append("anchore-container-scanner@1.0.23")
                self.anchore_data = dict['tool']['data']
                self.anchore_cred = dict['tool']['credential']

            elif dict['tool']['name'] == 'dependency':
                self.toolList.append("dependency")
                self.pluginList.append("dependency-check-jenkins-plugin@5.1.1")

            elif dict['tool']['name'] == 'argocd':
                self.toolList.append("argocd")
                self.pluginList.append("ssh-agent@1.23")
                self.argocd_data = dict['tool']['data']
                self.argocd_cred = dict['tool']['credential']
                
            else:
                print("Invalid tool name")

    def getToolList(self):
        return self.toolList
    
    def getPluginList(self):
        return self.pluginList

    def getJenkinsData(self):
        return self.jenkins_data

    def getGithubData(self):
        return self.github_data
    
    def getGithubCred(self):
        return self.github_cred
    
    def getGithubWebhook(self):
        return self.github_webhook
    
    def getSlackData(self):
        return self.slack_data
    
    def getSlackCred(self):
        return self.slack_cred

    def getSonarqubeData(self):
        return self.sonar_data

    def getSonarqubeCred(self):
        return self.sonar_cred

    def getDockerhubData(self):
        return self.dockerhub_data
    
    def getDockerhubCred(self):
        return self.dockerhub_cred
    
    def getAnchoreData(self):
        return self.anchore_data
    
    def getAnchoreCred(self):
        return self.anchore_cred

    def getArgocdData(self):
        return self.argocd_data
    
    def getArgocdCred(self):
        return self.argocd_cred
        