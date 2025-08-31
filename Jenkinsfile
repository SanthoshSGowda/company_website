pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = 'dockerhub-creds'   // Jenkins Docker Hub credentials ID
        DOCKERHUB_USERNAME = 'santhu100297'
        KUBE_CREDENTIALS = 'kubeconfig'             // Jenkins Kubeconfig credentials ID
        DOCKER_IMAGE = "santhu100297/flask-company-site:latest"
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/SanthoshSGowda/company_website.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    bat "docker build -t %DOCKER_IMAGE% ."
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat """
                        docker login -u %DOCKER_USER% -p %DOCKER_PASS%
                        docker push %DOCKER_IMAGE%
                    """
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    writeFile file: 'deployment.yaml', text: """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-company-site
spec:
  replicas: 2
  selector:
    matchLabels:
      app: flask-company-site
  template:
    metadata:
      labels:
        app: flask-company-site
    spec:
      containers:
      - name: flask-company-site
        image: ${DOCKER_IMAGE}
        ports:
        - containerPort: 5000
        imagePullPolicy: Always
"""
                    bat 'kubectl apply -f deployment.yaml'
                }
            }
        }
    }

    post {
        failure {
            echo '❌ Deployment Failed!'
        }
        success {
            echo '✅ Deployment Successful!'
        }
    }
}
