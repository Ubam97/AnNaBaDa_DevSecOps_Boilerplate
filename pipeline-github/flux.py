from jenkinsapi.credential import SSHKeyCredential

class Flux:
    def __init__(self, jenkins, **data):
        self.jenkins = jenkins
        self.__dict__.update(**data)
        self.stage = """
        stage('Flux Deploy') {
            steps {
                script {
                    sshagent (credentials: ['%s']) {
                        sh "ssh -o StrictHostKeyChecking=no ec2-user@%s fluxctl sync --k8s-fwd-ns flux"
                    }
                }
            }
        }"""%(self.__dict__['cred_id'], self.__dict__['masternode_url'])

    def createCredential(self):
        flux_creds = self.jenkins.credentials
        cred_dict = {
            'credential_id': self.__dict__['cred_id'],
            'description': self.__dict__['cred_description'],
            'userName': self.__dict__['cred_username'],
            'passphrase': '',
            'private_key': self.__dict__['cred_sshkey']
        }
        flux_creds[self.__dict__['cred_description']] = SSHKeyCredential(cred_dict)
    