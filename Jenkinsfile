pipeline {
    agent any

    environment {
        DOCKER_HUB_CREDENTIALS = 'dockerhub-creds'  // Jenkins Docker Hub credentials ID
        KUBECONFIG_CREDENTIALS = 'kubeconfig'        // Jenkins Kubernetes credentials ID
        IMAGE_NAME = 'santhu100297/flask-company-site'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/SanthoshSGowda/company_website.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Use Git commit hash as unique tag
                    def commitHash = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    env.IMAGE_TAG = "${commitHash}"
                    
                    bat "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${DOCKER_HUB_CREDENTIALS}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat """
                        docker login -u %DOCKER_USER% -p %DOCKER_PASS%
                        docker push ${IMAGE_NAME}:${IMAGE_TAG}
                    """
                }
            }
        }

        stage('Update Kubernetes Deployment') {
            steps {
                withCredentials([file(credentialsId: "${KUBECONFIG_CREDENTIALS}", variable: 'KUBECONFIG')]) {
                    bat """
                        kubectl set image deployment/flask-company-site flask-company-site=${IMAGE_NAME}:${IMAGE_TAG}
                        kubectl rollout status deployment/flask-company-site --timeout=120s
                    """
                }
            }
        }
    }

    post {
        success {
            echo "✅ Deployment Successful! Image: ${IMAGE_NAME}:${IMAGE_TAG}"
        }
        failure {
            echo "❌ Deployment Failed!"
        }
    }
}
