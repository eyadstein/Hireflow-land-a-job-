pipeline {
    agent any

    environment {
        PORT = "${env.PORT ?: '8000'}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Frontend') {
            steps {
                sh 'npm ci'
                sh 'npm run build'
            }
        }

        stage('Install Backend') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Migrate') {
            steps {
                sh 'python manage.py migrate --noinput'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    # Kill any existing daphne process on this port
                    fuser -k ${PORT}/tcp || true

                    # Start daphne in background, redirect logs
                    nohup daphne -b 0.0.0.0 -p ${PORT} hireflow.asgi:application \
                        > daphne.log 2>&1 &

                    echo "App started on port ${PORT}"
                    sleep 3
                    curl -sf http://localhost:${PORT}/api/ || echo "Health check failed"
                '''
            }
        }
    }

    post {
        success {
            echo "Hireflow is running on port ${PORT}"
        }
        failure {
            sh 'tail -n 30 daphne.log || true'
            echo 'Deployment failed. Check logs above.'
        }
    }
}
