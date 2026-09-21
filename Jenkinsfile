// Pipeline CI/CD del progetto cdci
// Trigger: polling del repo git ogni 2 minuti (al commit la build parte da sola,
// fino a 2 min di latenza). Per attivazione istantanea usa webhook:
//   - nel plugin "Webhook": endpoint http://<host>:8089/job/<nome>/hook/CD
//   - sul repo GitHub: Settings > Webhooks > URL sopra
//
pipeline {
    agent any

    triggers {
        pollSCM('*/2 * * * *')
    }

    environment {
        IMAGE_NAME = "mio-progetto"
        HEALTH_URL = "http://host.docker.internal:8003/health"
    }

    stages {

        stage("Checkout") {
            steps {
                checkout scm
            }
        }

        stage("Build immagine") {
            steps {
                sh "docker build -t ${IMAGE_NAME}:ci-${env.BUILD_NUMBER} -t ${IMAGE_NAME}:latest ."
            }
        }

        stage("Health check") {
            steps {
                // dry-run: lancia l'immagine su una porta provvisoria e verifica /health
                sh "docker rm -f ml-api-ci || true"
                sh "docker run -d --name ml-api-ci -p 18003:8000 ${IMAGE_NAME}:latest"
                sh '''
                    ok=0
                    for i in $(seq 1 12); do
                        if curl -sf http://host.docker.internal:18003/health; then ok=1; break; fi
                        echo "attendo healthcheck... ($i/12)"; sleep 5
                    done
                    [ $ok -eq 1 ] || { echo "healthcheck fallito"; exit 1; }
                    echo "healthcheck OK"
                '''
            }
            post {
                always {
                    sh "docker rm -f ml-api-ci || true"
                }
            }
        }

        stage("Deploy") {
            steps {
                sh "docker rm -f ml-api || true"
                sh "docker run -d --name ml-api -p 8003:8000 --restart unless-stopped ${IMAGE_NAME}:latest"
                sh """
                    ok=0
                    for i in \$(seq 1 12); do
                        if curl -sf ${env.HEALTH_URL}; then ok=1; break; fi
                        echo "attendo deploy... (\$i/12)"; sleep 5
                    done
                    [ \$ok -eq 1 ] || { echo "deploy non sano"; exit 1; }
                    echo "Deploy OK"
                """
            }
            post {
                failure {
                    echo "FAIL build ${env.BUILD_NUMBER} - controlla i log e rilancia 'docker compose up -d'"
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline #${env.BUILD_NUMBER} terminata"
        }
    }
}
