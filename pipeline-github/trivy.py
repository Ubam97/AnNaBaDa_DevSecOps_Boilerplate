class Trivy:
    def __init__(self, jenkins, **data):
        self.jenkins = jenkins
        self.__dict__.update(**data)
        if self.__dict__['tool'] == 'dockerhub':
            self.stage = """
            stage('Trivy Image Scan') {
                steps {
                    sh 'trivy image %s > trivy.txt'
                }
            }"""%(self.__dict__['image'])

        elif self.__dict__['tool'] == 'ecr':
            self.stage = """
            stage('Trivy Image Scan') {
                steps {
                    sh 'aws ecr get-login-password --region %s | docker login --username AWS --password-stdin %s.dkr.ecr.%s.amazonaws.com'
                    sh 'trivy image %s > trivy.txt'
                }
            }"""%(self.__dict__['region'], self.__dict__['account'], self.__dict__['region'], self.__dict__['image'])

















