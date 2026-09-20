# Build del container Jenkins con plugin pre-installati (evita il download UI al boot)
FROM jenkins/jenkins:lts-jdk21

# jenkins-plugin = Jenkins Configuration as Code: legge configuration-as-code.yaml
# al boot e crea l'admin user/pass (variabili JENKINS_UC_ADMIN_USER/PASSWORD nel compose)
RUN /usr/local/bin/install_plugins \
    jenkins-plugin \
    git \
    git-client \
    workflow-aggregator \
    workflow-cps \
    workflow-basic-steps \
    docker-plugin \
    blueocean

# Config-as-code base (plugins + message); il compose la monta in overwrite
COPY configuration-as-code.yaml /var/jenkins_home/configuration-as-code.yaml
