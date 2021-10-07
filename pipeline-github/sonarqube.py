from jenkinsapi.credential import SecretTextCredential
from xml.etree.ElementTree import parse
import os

def xml_modify(filename, **kargs):
    tree = parse(filename)
    root = tree.getroot()
    for tag, value in kargs.items():
        for i in root.iter(tag):
            i.text = value
    tree.write(filename, encoding='UTF-8', xml_declaration=True)

def copy_to_container(src, dest, filename):
    command="docker cp " + src + "/" + filename + " jenkins:" + dest
    os.system(command)

class Sonarqube:
    def __init__(self, jenkins, **data):
        self.jenkins = jenkins
        self.__dict__.update(**data)
        self.stage = """stage('SonarQube analysis') {
            steps {
                script {
                    withSonarQubeEnv() {
                        sh "./gradlew sonarqube"
                    }
                }
            }
       }"""

    def createCredential(self):
        sonar_creds = self.jenkins.credentials
        cred_dict = {
            'credential_id': self.__dict__['cred_id'],
            'description': self.__dict__['cred_description'],
            'secret': self.__dict__['token']
        }
        sonar_creds[self.__dict__['cred_description']] = SecretTextCredential(cred_dict)

    def sonarqubeConfigure(self, servername, scannername, scannerversion):
        xml_modify("./jenkins_config/hudson.plugins.sonar.SonarGlobalConfiguration.xml", name=servername, serverUrl=self.__dict__['url'], credentialsId=self.__dict__['cred_id'])
        xml_modify("./jenkins_config/hudson.plugins.sonar.SonarRunnerInstallation.xml", name=scannername, id=scannerversion)
        copy_to_container("./jenkins_config", "/var/jenkins_home", "hudson.plugins.sonar.SonarRunnerInstallation.xml")
        copy_to_container("./jenkins_config", "/var/jenkins_home", "hudson.plugins.sonar.SonarGlobalConfiguration.xml")
    