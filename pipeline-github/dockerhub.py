from jenkinsapi.credential import UsernamePasswordCredential
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

class Dockerhub:
    def __init__(self, jenkins, **data):
        self.jenkins = jenkins
        self.__dict__.update(**data)
        self.stage = """
        stage('Dockerhub Push image') {
            steps {
                script {
                    checkout scm
                    docker.withRegistry('', '%s') {
                        def customImage = docker.build("%s")
                        customImage.push("${env.BUILD_ID}")
                        customImage.push("latest")
                    }
                }
            }
        }"""%(self.__dict__['cred_id'], self.__dict__['image'])

    def createCredential(self):
        dockerhub_creds = self.jenkins.credentials
        cred_dict = {
            'description': self.__dict__['cred_description'],
            'credential_id': self.__dict__['cred_id'],
            'userName': self.__dict__['username'],
            'password': self.__dict__['password']
        }
        dockerhub_creds[self.__dict__['cred_description']] = UsernamePasswordCredential(cred_dict)
    
    
    