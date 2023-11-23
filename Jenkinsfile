pipeline {

    agent any

    environment {

        DOCKERHUB_CREDENTIALS = credentials("docker-hub-credentials")

        DOCKER_IMAGE_NAME = "crypto-bot"
        VERSION_FILE = "../../VERSION"
        LAST_VERSION = sh(
            script: "cat ../../VERSION",
            returnStdout: true
        ).trim()
        NEW_VERSION = incrementLastVersionNumber("${LAST_VERSION}")
    }

    stages {
        stage("Build") {
            steps {
                echo "Building phase..."

                sh "docker build -t $DOCKERHUB_CREDENTIALS_USR/${DOCKER_IMAGE_NAME}:${NEW_VERSION} ."
                sh "docker build -t $DOCKERHUB_CREDENTIALS_USR/${DOCKER_IMAGE_NAME}:latest ."
            }
        }

        stage("Test") {
            agent {
                docker {
                    image "qnib/pytest"
                }
            }
            steps {
                echo "Test phase..."
                
                sh "pip install -r requirements.txt"
                sh "pytest --junit-xml=./test-reports/results.xml -v ./test/"
            }
        }

        stage("Deliver") {
            steps {
                echo "Delivery phase..."

                echo "Logging in the docker hub with username $DOCKERHUB_CREDENTIALS_USR"
                sh "echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin"

                echo "Pushing $DOCKERHUB_CREDENTIALS_USR/${DOCKER_IMAGE_NAME}:${NEW_VERSION} to docker hub"
                sh "docker push $DOCKERHUB_CREDENTIALS_USR/${DOCKER_IMAGE_NAME}:${NEW_VERSION}"

                echo "Pushing $DOCKERHUB_CREDENTIALS_USR/${DOCKER_IMAGE_NAME}:latest to docker hub"
                sh "docker push $DOCKERHUB_CREDENTIALS_USR/${DOCKER_IMAGE_NAME}:latest"
            }
            post {
                success {
                    script {
                        echo "Writing new version ${NEW_VERSION} to file ${VERSION_FILE}"
                        writeFile(file: "${VERSION_FILE}", text: "${NEW_VERSION}")
                    }
                }
            }
        }
    }
}

def incrementLastVersionNumber(String version) {
    def versionArray = version.split("\\.")
    def lastNumber = versionArray[-1].toInteger()
    versionArray[-1] = (lastNumber + 1).toString()
    return versionArray.join(".")
}