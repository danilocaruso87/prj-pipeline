# cdci

Piccolo progetto che mette insieme un'API FastAPI di sentiment analysis, un
po' di monitoring con Prometheus e Grafana, e una pipeline CI/CD su Jenkins:
a ogni push su main viene buildata l'immagine nuova, si fa un health check e
si sostituisce il container vecchio. Tutto automatico.

Si alza con un docker compose up -d. Il job di Jenkins, l'utente admin e le
dashboards di Grafana vengono creati al primo avvio, quindi nella UI non c'è
niente da configurare a mano.

## Per partire

Serve Docker con compose v2 e git.

```
git clone https://github.com/danilocaruso87/prj-pipeline.git
cd prj-pipeline
cp .env.example .env
```

Nel .env c'è una cosa da sistemare per forza: il DOCKER_GID, cioè il gruppo
del socket docker della propria macchina, che serve a Jenkins per fare le
build e che è diverso su ogni PC.

```
echo "DOCKER_GID=$(stat -c %g /var/run/docker.sock)" >> .env
```

Tutte le password (Jenkins, Grafana) stanno nel .env e si cambiano lì, così
come le porte se quelle di default danno fastidio. Poi si accende tutto:

```
docker compose up -d --build
```

Il primo avvio di Jenkins mette un minuto circa (carica i plugin). Dopo di
che la pipeline parte da sola a ogni push su main.

## Dove trovare le cose

L'API risponde su http://localhost:8003. Lo stato su /health, le predizioni
su /predict con un POST json tipo {"text": "che bello"}, le metriche su
/metrics/.

Jenkins sta su http://localhost:8089, utente admin e la password che avete
messo nel .env. Dentro c'è già il job cdci: dalla pagina del job si vedono la
Stage View e il Console Output di ogni build.

Grafana sta su http://localhost:3001 ed entra con admin/admin (le dashboards
sono nella cartella Applications). Prometheus su http://localhost:9090, dove
sotto Status → Targets si vedono i due target che deve raccogliere. Le
metriche della macchina sono su http://localhost:9100.

Tutte queste porte si cambiano dal .env.

## Far girare l'API in locale, senza Docker

Le dipendenze Python stanno nel requirements.txt, quindi basta un venv:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Se si aggiunge una dipendenza nuova, aggiornare il requirements (un pip freeze
> requirements.txt va benissimo) e committarlo, sennò la build successiva non
la trova.

## Come funziona la pipeline

Ogni push su main (il polling ci mette al massimo un paio di minuti ad
accorgersene) fa girare il job cdci: checkout del codice, build dell'immagine
con tag ci-N, poi il container nuovo viene fatto partire su una porta
provvisoria per un health check ( massimo 60 secondi ) e solo se risponde
viene deployato al posto del vecchio ml-api. Se qualcosa fallisce non si
deployta niente e il container vecchio continua a servire.

## Testare la pipeline sul proprio repo

Per provarla serve un fork: si fa il fork, poi su Jenkins si apre il job cdci
→ Configure, si cambia il Repository URL nella sezione Pipeline mettendo il
proprio, si salva. Da lì in poi ogni push sul proprio main avvia la pipeline.

## Note

Il DOCKER_GID serve perché Jenkins usa il docker dell'host tramite il socket
montato nel container, e il gruppo di quel socket cambia da macchina a
macchina.

Dopo un deploy fatto dalla pipeline, il container ml-api non ha più le label
di compose: se un docker compose up -d si lamenta di un conflitto su ml-api
è normale, si toglie il container a mano (docker rm -f ml-api) e si rilancia
compose.

I dati di Grafana non persistono perché non c'è un volume: le dashboards
vengono riprovisionate a ogni avvio dal folder monitoring/.
