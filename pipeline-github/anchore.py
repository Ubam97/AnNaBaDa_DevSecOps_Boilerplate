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
class Anchore:
    def __init__(self, jenkins, **data):
        self.jenkins = jenkins
        self.__dict__.update(**data)
        if self.__dict__['tool'] == 'dockerhub':
            self.stage = """
            stage ('Anchore test') {
                steps {
                    script {
                        def imageLine = '%s'
                        writeFile file: '%s', text: imageLine
                        anchore name: '%s', engineCredentialsId: '%s', bailOnFail: false
                    }
                }
            }"""%(self.__dict__['image'], self.__dict__['image'], self.__dict__['image'], self.__dict__['cred_id'])

        elif self.__dict__['tool'] == 'ecr': # If the pipeline is successful for the first time, annotate the registry and image additions in the jenkinsfile. ex) //sh '~~'
            self.stage = """
            stage ('Anchore test') {
                steps {
                    script {
                        sh 'anchore-cli --url %s --u %s --p %s registry add %s %s %s --registry-type=awsecr'
                        sh 'anchore-cli --url %s --u %s --p %s image add %s'

                        def imageLine = '%s'
                        writeFile file: '%s', text: imageLine
                        anchore name: '%s', engineCredentialsId: '%s', bailOnFail: false
                    }
                }
            }"""%(self.__dict__['url'], self.__dict__['username'], self.__dict__['password'], self.__dict__['image'], self.__dict__['accesskey'], self.__dict__['secretkey'], self.__dict__['url'], self.__dict__['username'], self.__dict__['password'], self.__dict__['image'], self.__dict__['image'], self.__dict__['image'], self.__dict__['image'], self.__dict__['cred_id'])

    def anchoreConfigure(self):
        xml_modify("/home/ec2-user/AnNaBaDa_DevSecOps_Boilerplate/pipeline-github/jenkins_config/com.anchore.jenkins.plugins.anchore.AnchoreBuilder.xml", engineurl=self.__dict__['url'], engineuser=self.__dict__['username'], enginepass=self.__dict__['password'])
        copy_to_container("/home/ec2-user/AnNaBaDa_DevSecOps_Boilerplate/pipeline-github/jenkins_config","/var/jenkins_home","com.anchore.jenkins.plugins.anchore.AnchoreBuilder.xml")
    def createCredential(self):
        anchore_creds = self.jenkins.credentials
        cred_dict = {
            'description': self.__dict__['cred_description'],
            'credential_id': self.__dict__['cred_id'],
            'userName': self.__dict__['username'],
            'password': self.__dict__['password']
        }
        anchore_creds[self.__dict__['cred_description']] = UsernamePasswordCredential(cred_dict)