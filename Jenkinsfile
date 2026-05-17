pipeline {
    agent any

    environment {
        IMAGE_NAME = 'hireflow'
        COMPOSE_FILE = 'docker-compose.yml'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .'
                sh 'docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${IMAGE_NAME}:latest'
            }
        }

        stage('Test') {
            steps {
                sh '''
                    docker run --rm \
                        -e DB_NAME="" \
                        ${IMAGE_NAME}:${BUILD_NUMBER} \
                        python manage.py test --verbosity=2
                '''
            }
        }

        stage('Deploy') {
            steps {
                withEnv([
                    "DB_NAME=${env.DB_NAME ?: 'hireflow'}",
                    "DB_USER=${env.DB_USER ?: 'postgres'}",
                    "DB_PASSWORD=${env.DB_PASSWORD ?: 'postgres'}"
                ]) {
                    sh 'docker compose -f ${COMPOSE_FILE} down --remove-orphans'
                    sh 'docker compose -f ${COMPOSE_FILE} up -d --build'
                }
            }
        }
    }

    post {
        success {
            echo 'Hireflow deployed successfully.'
        }
        failure {
            sh 'docker compose -f ${COMPOSE_FILE} logs --tail=50'
            echo 'Deployment failed. Check logs above.'
        }
        always {
            sh 'docker image prune -f'
        }
    }
}
