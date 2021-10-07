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

class Gradle:
    def __init__(self):
        self.stage = """stage('Gradle Junit Test') {
            steps {
                sh 'chmod +x ./gradlew'
                sh "chmod +x gradlew; ./gradlew test"
            }
        }
        stage('Gradle Build ') {
            steps {
                sh 'chmod +x ./gradlew'
                sh './gradlew clean build'
            }
        }
        stage('Publish Test Result') {
            steps {
                junit '**/build/test-results/test/*.xml'
            }
        }"""

    def gradleConfigure(self, gradle_jenkins_configname, gradle_version):
        xml_modify("./jenkins_config/hudson.plugins.gradle.Gradle.xml", name=gradle_jenkins_configname, id=gradle_version)
        copy_to_container("./jenkins_config", "/var/jenkins_home", "hudson.plugins.gradle.Gradle.xml")
    