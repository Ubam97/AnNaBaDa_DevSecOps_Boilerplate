from jenkinsapi.credential import SSHKeyCredential
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

class Argocd:
    def __init__(self, jenkins, **data):
        self.jenkins = jenkins
        self.__dict__.update(**data)
        self.stage = """stage('ArgoCD Deploy') {
            steps {
                script {
                    sshagent (credentials: ['%s']) {
                        sh "ssh -o StrictHostKeyChecking=no ec2-user@%s argocd repo add %s"
                        sh "ssh -o StrictHostKeyChecking=no ec2-user@%s argocd app create test --repo %s --sync-policy automated --path templates --dest-server https://kubernetes.default.svc --dest-namespace default"
                    }
                }
            }
        }"""%(self.__dict__['cred_id'], self.__dict__['masternode_url'], self.__dict__['github_url'], self.__dict__['masternode_url'], self.__dict__['github_url'])

    def createCredential(self):
        argocd_creds = self.jenkins.credentials
        cred_dict = {
            'credential_id': self.__dict__['cred_id'],
            'description': self.__dict__['cred_description'],
            'userName': self.__dict__['cred_username'],
            'passphrase': '',
            'private_key': self.__dict__['cred_sshkey']
        }
        argocd_creds[self.__dict__['cred_description']] = SSHKeyCredential(cred_dict)
    