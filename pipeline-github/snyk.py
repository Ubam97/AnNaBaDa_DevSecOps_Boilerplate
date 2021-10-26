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

class Snyk:
    def __init__(self, jenkins, **data):
        self.jenkins = jenkins
        self.__dict__.update(**data)
        self.stage = """stage('Snyk Test') {
            steps {
                snykSecurity(
                    failOnIssues: false,
                    snykInstallation: 'snyk',
                    snykTokenId: '%s'
                )
            }
        }"""%(self.__dict__['cred_id'])
    


    def snykConfigure(self, snyk_jenkins_configname, snyk_version, snyk_update_hours):
        xml_modify("/home/ec2-user/AnNaBaDa_DevSecOps_Boilerplate/pipeline-github/jenkins_config/io.snyk.jenkins.SnykStepBuilder.xml", name=snyk_jenkins_configname, version=snyk_version, updatePolicyIntervalHours=snyk_update_hours)
        copy_to_container("/home/ec2-user/AnNaBaDa_DevSecOps_Boilerplate/pipeline-github/jenkins_config", "/var/jenkins_home", "io.snyk.jenkins.SnykStepBuilder.xml")