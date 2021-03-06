pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Building'
                sh '''
                    export LC_ALL=C.UTF-8
                    export LANG=C.UTF-8
                    pipenv install --dev --three
                    pipenv run flake8 --version
                    pipenv run black --version
                    pipenv run black --check ./maverick_api/
                '''
            }
        }
        stage('Test') {
            steps {
                echo 'Testing'
                sh '''
                    pipenv run black --check ./maverick_api/
                '''
            }
        }
        stage('Deploy') {
            when {
                tag 'v*'
            }
            steps {
                echo 'Deploying only because this commit is tagged...'
            }
        }
    }
    post {
        always {
            echo 'This will always run'
        }
        success {
            echo 'This will run only if successful'
        }
        failure {
            echo 'This will run only if failed'
        }
        unstable {
            echo 'This will run only if the run was marked as unstable'
        }
        changed {
            echo 'This will run only if the state of the Pipeline has changed'
            echo 'For example, if the Pipeline was previously failing but is now successful'
        }
    }
}
