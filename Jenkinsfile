pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = 'dockerhub-creds'   // Jenkins Docker Hub credentials ID
        DOCKERHUB_USERNAME = 'santhu100297'
        IMAGE_NAME = "${DOCKERHUB_USERNAME}/flask-company-site"
        KUBE_CREDENTIALS = 'kubeconfig'             // Jenkins Kubeconfig credentials ID
    }

    stages {

        stage('Checkout Code') {
            steps {
                git url: 'https://github.com/SanthoshSGowda/company_website.git', branch: 'main'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${IMAGE_NAME}:latest")
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${DOCKERHUB_CREDENTIALS}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    script {
                        bat "echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin"
                        bat "docker push ${IMAGE_NAME}:latest"
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: "${KUBE_CREDENTIALS}", variable: 'KUBECONFIG')]) {
                   bat "kubectl apply -f k8s/deployment.yaml"
                    bat "kubectl rollout status deployment flask-company-site"
                }
            }
        }

    }

    post {
        success {
            echo '✅ Deployment Successful!'
        }
        failure {
            echo '❌ Deployment Failed!'
        }
    }
}
