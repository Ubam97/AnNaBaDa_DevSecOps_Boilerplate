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

class Jira:
    def __init__(self, jenkins, **data):
        self.jenkins = jenkins
        self.__dict__.update(**data)
        self.stage = """
        stage('Jira Notification') {
            steps {
                 jiraSendBuildInfo branch: 'https://%s/browse/%s', site: '%s'
            }
        }"""%(self.__dict__['site'],self.__dict__['branch'],self.__dict__['site'])

    def createCredential(self):
        jira_creds = self.jenkins.credentials
        cred_dict = {
            'credential_id': self.__dict__['cred_id'],
            'description': self.__dict__['cred_description'],
            'secret': self.__dict__['secret']
        }
        jira_creds[self.__dict__['cred_description']] = SecretTextCredential(cred_dict)

    def jiraConfigure(self):
        xml_modify("/home/ec2-user/AnNaBaDa_DevSecOps_Boilerplate/pipeline-github/jenkins_config/atl-jsw-global-configuration.xml",site=self.__dict__['site'], clientId=self.__dict__['token'], credentialsId=self.__dict__['cred_id'] )
        copy_to_container("/home/ec2-user/AnNaBaDa_DevSecOps_Boilerplate/pipeline-github/jenkins_config", "/var/jenkins_home", "atl-jsw-global-configuration.xml")
    