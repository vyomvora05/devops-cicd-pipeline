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
                    cp requirements.txt ${DEPLOY_DIR}/releases/${BUILD_NUMBER}/
                    cp -r ${VENV} ${DEPLOY_DIR}/releases/${BUILD_NUMBER}/venv
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    # stop any previously running instance
                    if [ -f ${DEPLOY_DIR}/current.pid ]; then
                        kill $(cat ${DEPLOY_DIR}/current.pid) 2>/dev/null || true
                        rm -f ${DEPLOY_DIR}/current.pid
                    fi

                    cd ${DEPLOY_DIR}/releases/${BUILD_NUMBER}
                    . venv/bin/activate

                    export BUILD_NUMBER=${BUILD_NUMBER}
                    export GIT_COMMIT=${GIT_COMMIT}
                    export PORT=${APP_PORT}
                    export JENKINS_NODE_COOKIE=dontKillMe
                    export BUILD_ID=dontKillMe

                    nohup python3 app.py > ${DEPLOY_DIR}/app.log 2>&1 &
                    disown
                    echo $! > ${DEPLOY_DIR}/current.pid

                    echo ${BUILD_NUMBER} > ${DEPLOY_DIR}/current_build.txt
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                script {
                    sleep(time: 3, unit: 'SECONDS')
                    def result = sh(script: "curl -sf http://127.0.0.1:${APP_PORT}/health", returnStatus: true)
                    if (result != 0) {
                        error("Smoke test failed: app did not respond on /health")
                    }
                }
            }
        }
    }

    post {
        failure {
            script {
                sh '''
                    LAST_GOOD=$(cat ${DEPLOY_DIR}/last_good_build.txt 2>/dev/null || echo "")
                    if [ -f ${DEPLOY_DIR}/current.pid ]; then
                        kill $(cat ${DEPLOY_DIR}/current.pid) 2>/dev/null || true
                        rm -f ${DEPLOY_DIR}/current.pid
                    fi
                    if [ -n "$LAST_GOOD" ] && [ -d ${DEPLOY_DIR}/releases/$LAST_GOOD ]; then
                        cd ${DEPLOY_DIR}/releases/$LAST_GOOD
                        . venv/bin/activate

                        export BUILD_NUMBER=$LAST_GOOD
                        export PORT=${APP_PORT}
                        export JENKINS_NODE_COOKIE=dontKillMe
                        export BUILD_ID=dontKillMe

                        nohup python3 app.py > ${DEPLOY_DIR}/app.log 2>&1 &
                        disown
                        echo $! > ${DEPLOY_DIR}/current.pid
                        echo "Rolled back to build $LAST_GOOD"
                    else
                        echo "No previous good build to roll back to"
                    fi
                '''
            }
        }
        success {
            sh '''
                cp ${DEPLOY_DIR}/current_build.txt ${DEPLOY_DIR}/last_good_build.txt
            '''
        }
    }
}
