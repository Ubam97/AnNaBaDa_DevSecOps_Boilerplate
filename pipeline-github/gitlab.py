import requests
from jenkinsapi.credential import UsernamePasswordCredential
from xml.etree.ElementTree import parse
import os

class Gitlab(object):
    def __init__(self, jenkins, **data):
        self.jenkins = jenkins
        self.__dict__.update(**data)
        self.session = requests.Session()
        self.stage = """stage('Git Progress') {
            steps {
                git  branch: 'main', credentialsId: '%s', url: '%s'
            }
        }"""%(self.__dict__['cred_id'], self.__dict__['url'])
        # github api 를 요청할 때 헤더에 token 추가 필요
        if hasattr(self, 'token'):
           self.session.headers['PRIVATE-TOKEN'] = self.__dict__['token']
           self.session.headers['Content-Type'] = "application/json"

    def call_api(self, type, Url, body):
        response = self.session.request(type ,url=Url, headers=self.session.headers, json=body)
        return response

    def createCredential(self):
        gitlab_creds = self.jenkins.credentials
        cred_dict = {
            'description': self.__dict__['cred_description'],
            'credential_id': self.__dict__['cred_id'],
            'userName': self.__dict__['username'],
            'password': self.__dict__['password']
        }
        gitlab_creds[self.__dict__['cred_description']] = UsernamePasswordCredential(cred_dict)