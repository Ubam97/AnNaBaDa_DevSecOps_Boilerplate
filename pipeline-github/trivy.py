class Trivy:
    def __init__(self, jenkins, **data):
        self.jenkins = jenkins
        self.__dict__.update(**data)
        self.stage = """
        stage('Trivy Image Scan') {
            steps {
                sh 'trivy image %s > trivy.txt'
            }
        }"""%(self.__dict__['image'])

















