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
    
class Dependency:
    def __init__(self):
        self.stage = """
        stage('OWASP Dependency-Check') {
            steps {
                dependencyCheck additionalArguments: '-s "./" -f "XML" -o "./" --prettyPrint', odcInstallation: 'dependency'
                dependencyCheckPublisher pattern: 'dependency-check-report.xml'
                dependencyCheck additionalArguments: '-s "./" -f "HTML" -o "./" --prettyPrint', odcInstallation: 'dependency'
            }
        }
        """
    def dependencyConfigure(self, dependency_jenkins_configname, dependency_version):
        xml_modify("./jenkins_config/org.jenkinsci.plugins.DependencyCheck.DependencyCheckToolBuilder.xml", name=dependency_jenkins_configname, id=dependency_version)
        copy_to_container("./jenkins_config", "/var/jenkins_home", "org.jenkinsci.plugins.DependencyCheck.DependencyCheckToolBuilder.xml")
