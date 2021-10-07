import requests
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

class Github(object):
    def __init__(self, jenkins, **data):
        self.jenkins = jenkins
        self.__dict__.update(**data)
        self.session = requests.Session()
        self.stage = """stage('Git Progress') {
            steps {
                git  branch: 'main', credentialsId: '%s', url: '%s'
            }
        }"""%(self.__dict__['cred_id'], self.__dict__['url'])
        # github api 를 요청할 때 헤더에 token 추가 필요
        if hasattr(self, 'token'):
           self.session.headers['Authorization'] = 'token %s' % self.token
           self.session.headers['Accept'] = "application/vnd.github.v3+json"

    def call_api(self, type, Url, body):
        response = self.session.request(type ,url=Url, headers=self.session.headers, json=body)
        return response

    def createCredential(self):
        github_creds = self.jenkins.credentials
        cred_dict = {
            'credential_id': self.__dict__['cred_id'],
            'description': self.__dict__['cred_description'],
            'secret': self.__dict__['token']
        }
        github_creds[self.__dict__['cred_description']] = SecretTextCredential(cred_dict)

    def githubConfigure(self):
        xml_modify("./jenkins_config/github-plugin-configuration.xml", name="github", credentialsId=self.__dict__['cred_id'])
        copy_to_container("./jenkins_config", "/var/jenkins_home", "github-plugin-configuration.xml")