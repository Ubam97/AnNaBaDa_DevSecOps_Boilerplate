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

class Slack:
    def __init__(self, jenkins, **data):
        self.jenkins = jenkins
        self.__dict__.update(**data)
        self.stage = """stage('Slack Notification') {
                steps {
                    slackSend (channel: '#%s', color: '#FFFF00', message: "STARTED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
                }
            }"""%(self.__dict__['channel'])

    def createCredential(self):
        slack_creds = self.jenkins.credentials
        cred_dict = {
            'credential_id': self.__dict__['cred_id'],
            'description': self.__dict__['cred_description'],
            'secret': self.__dict__['token']
        }
        slack_creds[self.__dict__['cred_description']] = SecretTextCredential(cred_dict)

    def slackConfigure(self):
        xml_modify("./jenkins_config/jenkins.plugins.slack.SlackNotifier.xml", teamDomain=self.__dict__['subdomain'], tokenCredentialId=self.__dict__['cred_id'], room=self.__dict__['channel'])
        copy_to_container("./jenkins_config", "/var/jenkins_home", "jenkins.plugins.slack.SlackNotifier.xml")
    