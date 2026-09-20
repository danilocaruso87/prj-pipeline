import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi_profiler import PyInstrumentProfilerMiddleware
from prometheus_client import make_asgi_app, Counter

from src import model as ml
from src.schemas import RowInput, DetectionOutput
from time import perf_counter


from src.metrics import (
    PREDICTIONS_TOTAL,
    PREDICTION_ERRORS_TOTAL,
    PREDICTION_DURATION_SECONDS,
    HTTP_DURATION_SECONDS,
    HTTP_IN_FLIGHT,
    REVIEW_LENGTH_CHARS,
    SENTIMENT_CONFIDENCE,
)

logger = logging.getLogger(__name__)

# Counter richieste HTTP — stesso nome che usa la dashboard Grafana
HTTP_REQUESTS_TOTAL = Counter(
    "http_server_requests_seconds",
    "Richieste HTTP totali",
    ["method", "endpoint", "status"],
)



@asynccontextmanager
async def lifespan(app: FastAPI):
    await ml.load_model()
    yield

app = FastAPI(lifespan=lifespan,
              title="Modello di Sentiment Analysis",
              description="API che espone le funzionalità del modello di Sentiment Analysis",
              version="1.0.0")

app.add_middleware(PyInstrumentProfilerMiddleware,
                   server_app=app,
                   profiler_output_type='html',
                   is_print_each_request=False,
                   open_in_browser=False,
                   html_file_name='profiling_performance.html')


@app.middleware("http")
async def http_requests_counter(request: Request, call_next):
    """Conta ogni richiesta HTTP (method/endpoint/status) e ne misura la durata."""
    HTTP_IN_FLIGHT.inc()
    start = perf_counter()
    try:
        response = await call_next(request)
        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            endpoint=request.url.path,
            status=str(response.status_code),
        ).inc()
        return response
    finally:
        HTTP_DURATION_SECONDS.labels(
            method=request.method,
            endpoint=request.url.path,
        ).observe(perf_counter() - start)
        HTTP_IN_FLIGHT.dec()

# Espone metriche leggibili da Prometheus
app.mount("/metrics", make_asgi_app())







@app.post("/predict",
          description="accetta una recensione in formato JSON e restituisce il sentimento analizzato.",
          response_description="ritorna un oggetto DetectionOutput")
def identify_sentiment(rowInput: RowInput) -> DetectionOutput:
    if not ml.is_ready:
        logger.error("Impossibile eseguire la richiesta, riprovare più tardi")
        raise HTTPException(status_code=503,
                            detail="Impossibile eseguire la richiesta, riprovare più tardi")
    if rowInput.review == "":
        logger.error("Impossibile eseguire la richiesta, input non valido")
        raise HTTPException(status_code=422,
                            detail="Impossibile eseguire la richiesta, input non valido")
    try:
        return predict(rowInput)
    except Exception as e:
        logger.error(f"Errore in fase di prediction: {e}")
        raise HTTPException(status_code=500,
                            detail="Impossibile eseguire la richiesta, errore in fase di prediction")



def predict(row: RowInput) -> DetectionOutput:
        logger.info(f"[identify_sentiment] richiesta input: {row.review}")

        start = perf_counter()

        try:
            REVIEW_LENGTH_CHARS.observe(len(row.review))
            sentiment = ml.pipeline.predict([row.review])
            proba = ml.pipeline.predict_proba([row.review]).max()

            result = DetectionOutput(
                sentiment=sentiment[0],
                confidence=float(proba),
            )

            PREDICTIONS_TOTAL.labels(sentiment=result.sentiment).inc()
            SENTIMENT_CONFIDENCE.observe(result.confidence)
            return result

        except Exception:
            PREDICTION_ERRORS_TOTAL.inc()
            logger.exception("Errore in fase di prediction")
            raise

        finally:
            PREDICTION_DURATION_SECONDS.observe(perf_counter() - start)

@app.get("/health")
def health(response: Response):
    if not ml.is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "error", "detail": "model non caricato"}
    return {"status": "ok"}