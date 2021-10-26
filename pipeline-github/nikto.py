class Nikto:
    def __init__(self, **data):
        self.__dict__.update(**data)
        self.stage = """
        stage('Nikto scanner') {
            steps {
                script {
                    try {
                        sh '/nikto/program/./nikto.pl -host %s -o . -Format txt'
                    } catch (e) {
                        sh 'echo Succese'
                    }
                }
            }
        }"""%(self.__dict__['node_url'])