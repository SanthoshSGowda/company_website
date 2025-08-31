pipeline {
    agent any

    environment {
        DOCKER_HUB_CREDENTIALS = 'dockerhub-creds' // Docker Hub credentials ID in Jenkins
        DOCKER_IMAGE = 'santhu100297/flask-company-site'
        KUBE_CREDENTIALS = 'kubeconfig'           // Kubernetes credentials ID
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
                    // Generate unique image tag from git commit
                    def commitHash = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    env.IMAGE_TAG = "${commitHash}"
                    sh "docker build -t ${DOCKER_IMAGE}:${IMAGE_TAG} ."
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${DOCKER_HUB_CREDENTIALS}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh "echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin"
                    sh "docker push ${DOCKER_IMAGE}:${IMAGE_TAG}"
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: "${KUBE_CREDENTIALS}", variable: 'KUBECONFIG')]) {
                    // Update deployment with new image tag
                    sh "kubectl set image deployment/flask-company-site flask-company-site=${DOCKER_IMAGE}:${IMAGE_TAG}"
                    sh "kubectl rollout status deployment/flask-company-site --timeout=120s"
                }
            }
        }
    }

    post {
        success {
            echo "✅ Deployment Successful! New version is live."
        }
        failure {
            echo "❌ Deployment Failed! Check Jenkins logs and Kubernetes pods."
        }
    }
}
