class Jacoco:
    def __init__(self, **data):
        self.__dict__.update(**data)
        if self.__dict__['tool'] == 'maven':
            self.stage = """
            stage('Jacoco') {
                steps {
                    jacoco execPattern: 'target/**.exec', runAlways: true
                }
            }"""

        elif self.__dict__['tool'] == 'gradle':
            self.stage = """
            stage('Jacoco') {
                steps {
                    jacoco execPattern: 'target/**.exec', runAlways: true
                }
            }"""