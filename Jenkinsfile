pipeline {
  agent any
  environment {
    DOCKER_IMAGE = "your-dockerhub-username/flask-company-site"
    DOCKER_TAG = "latest"
    REGISTRY_CREDENTIALS = "dockerhub-credentials"
    KUBECONFIG_CREDENTIALS = "kubeconfig"
    PYTHON_ENV = "venv"
  }
  stages {
    stage('Checkout'){ steps { checkout scm } }
    stage('Install Deps'){
      steps{
        sh '''
        python3 -m venv ${PYTHON_ENV}
        source ${PYTHON_ENV}/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        '''
      }
    }
    stage('Unit Tests'){ steps { sh 'echo "No tests yet"' } } 
    stage('Build Docker'){ steps { sh 'docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .' } }
    stage('Push Docker'){
      steps {
        withCredentials([usernamePassword(credentialsId: "${REGISTRY_CREDENTIALS}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh '''
          echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
          docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
          '''
        }
      }
    }
    stage('Deploy to K8s'){
      steps {
        withCredentials([file(credentialsId: "${KUBECONFIG_CREDENTIALS}", variable: 'KUBECONFIG_FILE')]) {
          sh '''
          export KUBECONFIG=$KUBECONFIG_FILE
          kubectl apply -f k8s/deployment.yaml
          kubectl apply -f k8s/service.yaml
          '''
        }
      }
    }
  }
}
