pipeline {
    agent any
    environment {
        REGISTRY = "santhu100297/flask-company-site"
        REGISTRY_CREDENTIALS = "@Santhu97"
        KUBECONFIG_CREDENTIALS = "kubeconfig"
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Build Docker') {
            steps {
                bat 'docker build -t ${REGISTRY}:latest .'
            }
        }
        stage('Push Docker') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${REGISTRY_CREDENTIALS}", usernameVariable:'DOCKER_USER', passwordVariable:'DOCKER_PASS')]) {
                    bat '''
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker push ${REGISTRY}:latest
                    '''
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: "${KUBECONFIG_CREDENTIALS}", variable:'KUBECONFIG_FILE')]) {
                    bat '''
                        export KUBECONFIG=$KUBECONFIG_FILE
                        kubectl set image deployment/flask-company-site flask-company-site=${REGISTRY}:latest --record
                        kubectl rollout status deployment/flask-company-site
                    '''
                }
            }
        }
    }
}
