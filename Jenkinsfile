pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Frontend') {
            steps {
                bat 'npm ci'
                bat 'npm run build'
            }
        }

        stage('Install Backend') {
            steps {
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Migrate') {
            steps {
                bat 'python manage.py migrate --noinput'
            }
        }

        stage('Deploy') {
            steps {
                bat 'powershell -Command "Get-Process -Name daphne -ErrorAction SilentlyContinue | Stop-Process -Force"'
                bat 'start "HireflowApp" /B daphne -b 0.0.0.0 -p 8000 hireflow.asgi:application > daphne.log 2>&1'
                bat 'powershell -Command "Start-Sleep 3; Invoke-WebRequest -Uri http://localhost:8000/api/ -UseBasicParsing | Select-Object StatusCode"'
            }
        }
    }

    post {
        success {
            echo 'Hireflow is running on http://localhost:8000'
        }
        failure {
            bat 'type daphne.log 2>nul || echo No log file yet'
        }
    }
}
