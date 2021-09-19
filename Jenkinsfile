pipeline {
    agent none
    stages {
        stage('Build') {
            agent {
                docker {
                    image 'python:3-alpine'
                }
            }
            steps {
                sh 'python3 --version'
//                 stash(name: 'compiled-results', includes: 'sources/*.py*')
            }
        }
    }
}