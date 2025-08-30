pipeline {
    agent any
    environment {
        REGISTRY = "santhu100297/flask-company-site"
        KUBECONFIG_CREDENTIALS = "@Santhu97"
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Build Docker') {
            steps {
                bat 'docker build -t %REGISTRY%:latest .'
            }
        }
        stage('Push Docker') {
            steps {
                withCredentials([usernamePassword(credentialsId: "@Santhu97", usernameVariable:'DOCKER_USER', passwordVariable:'DOCKER_PASS')]) {
                    bat """
                    echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin
                    docker push %REGISTRY%:latest
                    """
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: "kubeconfig", variable:'KUBECONFIG_FILE')]) {
                    bat """
                    set KUBECONFIG=%KUBECONFIG_FILE%
                    kubectl set image deployment/flask-company-site flask-company-site=%REGISTRY%:latest --record
                    kubectl rollout status deployment/flask-company-site
                    """
                }
            }
        }
    }
}
