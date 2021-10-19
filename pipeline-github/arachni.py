class Arachni:
    def __init__(self, **data):
        self.__dict__.update(**data)
        self.stage = """
        stage('Arachni scanner') {
            steps {
                script {
                    sshagent (credentials: ['%s']) {
                            sh "ssh -o StrictHostKeyChecking=no ec2-user@%s /home/ec2-user/arachni-1.5.1-0.5.12/bin/arachni %s --report-save-path=arachni.afr"
                            sh "ssh -o StrictHostKeyChecking=no ec2-user@%s /home/ec2-user/arachni-1.5.1-0.5.12/bin/arachni_reporter arachni.afr --reporter=json:outfile=arachni.json.zip"
                    }
                }
            }
        }"""%(self.__dict__['cred_id'], self.__dict__['masternode_url'], self.__dict__['node_url'], self.__dict__['masternode_url'])