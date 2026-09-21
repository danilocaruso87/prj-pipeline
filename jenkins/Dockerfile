# Build del container Jenkins con plugin pre-installati (evita il download UI al boot)
FROM jenkins/jenkins:lts-jdk21

# jenkins-plugin = Jenkins Configuration as Code: legge configuration-as-code.yaml
# al boot e crea l'admin user/pass (variabili JENKINS_UC_ADMIN_USER/PASSWORD nel compose)

RUN jenkins-plugin-cli --plugins \
    configuration-as-code \
    git \
    git-client \
    workflow-aggregator \
    workflow-cps \
    workflow-basic-steps \
    docker-plugin \
    blueocean

# Config-as-code base (plugins + message); il compose la monta in overwrite
COPY --chown=1000:1000 configuration-as-code.yaml /var/jenkins_home/configuration-as-code.yaml
COPY --chown=1000:1000 jobs/ /var/jenkins_home/jobs/

USER root
RUN apt-get update && apt-get install -y --no-install-recommends docker-cli \
    && rm -rf /var/lib/apt/lists/*
USER jenkins
