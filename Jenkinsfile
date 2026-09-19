pipeline {
    agent any

    environment {
        VENV = "venv"
        APP_PORT = "5001"
        DEPLOY_DIR = "/tmp/devops-cicd-deploy"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Checked out commit ${env.GIT_COMMIT}"
            }
        }

        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv ${VENV}
                    . ${VENV}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    . ${VENV}/bin/activate
                    ruff check .
                '''
            }
        }

        stage('Test & Coverage') {
            steps {
                sh '''
                    . ${VENV}/bin/activate
                    pytest --cov=app --cov-report=term-missing --cov-fail-under=80
                '''
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                    . ${VENV}/bin/activate
                    bandit -r . --exclude ./venv
                '''
            }
        }

        stage('Dependency Audit') {
            steps {
                sh '''
                    . ${VENV}/bin/activate
                    pip-audit -r requirements.txt
                '''
            }
        }

        stage('Package') {
            steps {
                sh '''
                    mkdir -p ${DEPLOY_DIR}/releases/${BUILD_NUMBER}
                    cp app.py ${DEPLOY_DIR}/releases/${BUILD_NUMBER}/
                    