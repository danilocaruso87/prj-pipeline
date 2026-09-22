# cdci — ML API + Monitoring + CI/CD

Microservizio FastAPI (sentiment analysis) con monitoring Prometheus/Grafana e
pipeline CI/CD su Jenkins: **push su `main` → build automatica → health check →
deploy** del nuovo container, senza toccare nulla.

Tutto si alza con un solo `docker compose up -d`. Admin di Jenkins, job `cdci`,
datasource e dashboards Grafana vengono creati al primo avvio (seed): nessuna
configurazione manuale in UI.

## Requisiti

- Docker + Docker Compose v2 (`docker compose ...`)
- git (per clonare e per il push che innesca la pipeline)

## Avvio (4 mosse)

```bash
# 1) clona ed entra
git clone https://github.com/danilocaruso87/prj-pipeline.git cdci && cd cdci

# 2) crea la tua configurazione locale
cp .env.example .env

# 3) scrivi il gruppo docker della TUA macchina (varia da PC a PC)
echo "DOCKER_GID=$(stat -c %g /var/run/docker.sock)" >> .env
#    ...e sistema JENKINS_ADMIN_PASSWORD nel .env

# 4) accendi tutto
docker compose up -d --build
```

Jenkins impiega ~1 minuto al primo avvio (plugin + job seed). Poi la pipeline
parte da sola a ogni push su `main`.

## Servizi e indirizzi

Porte di default (si cambiano tutte nel `.env`, vedi sotto):

| Servizio | Indirizzo | Login | Cosa ci trovi |
|---|---|---|---|
| **API** (`ml-api`) | http://localhost:8003 | — | l'app deployata: `POST /predict`, `GET /health`, `GET /metrics/` |
| **Jenkins** | http://localhost:8089 | admin / password del `.env` | job `cdci` già configurato, Stage View e Console Output |
| **Grafana** | http://localhost:3001 | admin / admin | dashboard in cartella *Applications*: Application Overview, Node Overview |
| **Prometheus** | http://localhost:9090 | — | metriche; target su `Status → Targets` (ml-api, node-exporter) |
| **Node Exporter** | http://localhost:9100/metrics | — | metriche della macchina host |

Esempio di predizione:

```bash
curl -X POST http://localhost:8003/predict -H 'Content-Type: application/json' -d '{"text": "che bello"}'
```

## Come funziona la pipeline

Ogni push su `main` (rilevato dal polling, max 2 minuti) fa girare il job `cdci`:

1. **Checkout** — preleva il codice dal repo
2. **Build immagine** — `docker build` con tag `mio-progetto:ci-N` e `latest`
3. **Health check** — dry-run del container nuovo su una porta provvisoria
   (`CI_HEALTH_PORT`, default 18003) e verifica `/health` per max 60s
4. **Deploy** — sostituisce il container `ml-api` (stessa porta di `.env`) e
   riverifica `/health`

Se una build fallisce non si deploya nulla: il container vecchio continua a
servire le richieste.

## Configurazione (`.env`)

| Variabile | Default | Scopo |
|---|---|---|
| `ML_API_PORT` | `8003` | porta pubblica dell'API |
| `JENKINS_ADMIN_USER` / `JENKINS_ADMIN_PASSWORD` | `admin` / — | login Jenkins (creato via JCasC) |
| `JENKINS_PORT` | `8089` | UI Jenkins |
| `JENKINS_AGENT_PORT` | `50001` | porta agenti JNLP |
| `DOCKER_GID` | — | gruppo del socket docker (obbligatorio, vedi mossa 3) |
| `GRAFANA_PORT` | `3001` | UI Grafana |
| `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD` | `admin` / `admin` | login Grafana |
| `PROMETHEUS_PORT` | `9090` | UI Prometheus |
| `NODE_EXPORTER_PORT` | `9100` | metriche host |
| `CI_HEALTH_PORT` | `18003` | porta dry-run della pipeline |

Dopo aver cambiato una porta: `docker compose up -d` (ricrea i servizi
interessati). La pipeline legge le porte dal container Jenkins, quindi deploya
sempre sulla porta scelta nel `.env`.

## Usare il proprio fork

Il job `cdci` punta a questo repo. Per usare il tuo fork: Jenkins → job `cdci` →
**Configure** → sezione *Pipeline* → cambia **Repository URL** → Save. La
modifica resta nel volume `jenkins_home`, nessun altro passo.

## Note operative

- **Perché `DOCKER_GID`**: la pipeline esegue `docker build` sul Docker
  dell'host tramite il socket montato; il gruppo del socket cambia da macchina
  a macchina, quindi va scritto una volta nel proprio `.env`.
- **Reset di Jenkins** (perde job, build e utenti ricreati poi dal seed):
  `docker compose down jenkins && docker volume rm cdci_jenkins_home && docker compose up -d jenkins`
- Dopo un deploy della pipeline il container `ml-api` non ha le label compose:
  se un successivo `docker compose up -d` segnala *conflict su "ml-api"* è normale —
  `docker rm -f ml-api` e rilancia `docker compose up -d`.
- I dati di monitoraggio non persistono (Grafana è senza volume): i dashboard
  vengono riprovisionati a ogni avvio dal folder `monitoring/`.
- Le metriche dell'app sono esposte su `/metrics/` e scarpite da Prometheus
  ogni 5s (config in `monitoring/prometheus/prometheus.yml`).
