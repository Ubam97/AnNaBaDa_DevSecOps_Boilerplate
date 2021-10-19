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

class Maven:
    def __init__(self):
        self.stage = """
        stage('Maven Build') {
            steps {
                sh 'chmod +x ./mvnw'
                sh './mvnw -B -DskipTests clean package'
            }
        }
        stage('Maven Junit Test') {
            steps {
                sh 'chmod +x ./mvnw'
                sh './mvnw test -Dmaven.test.failure.ignore=true'
            }
        }"""

    def mavenConfigure(self, maven_jenkins_configname, maven_version):
        xml_modify("/home/ec2-user/AnNaBaDa_DevSecOps_Boilerplate/pipeline-github/jenkins_config/hudson.tasks.Maven.xml", name=maven_jenkins_configname, id=maven_version)
        copy_to_container("/home/ec2-user/AnNaBaDa_DevSecOps_Boilerplate/pipeline-github/jenkins_config", "/var/jenkins_home", "hudson.tasks.Maven.xml")
    