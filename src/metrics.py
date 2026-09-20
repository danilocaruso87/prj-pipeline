from prometheus_client import Counter, Gauge, Histogram, Summary

PREDICTIONS_TOTAL = Counter(
    "sentiment_predictions",
    "Numero totale di predizioni eseguite",
    ["sentiment"],
)

PREDICTION_ERRORS_TOTAL = Counter(
    "sentiment_prediction_errors",
    "Numero totale di errori durante la predizione",
)

PREDICTION_DURATION_SECONDS = Histogram(
    "sentiment_prediction_duration_seconds",
    "Durata della predizione del modello in secondi",
)

# --- Metriche HTTP dell'API ---
HTTP_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "Durata delle richieste HTTP in secondi",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)

HTTP_IN_FLIGHT = Gauge(
    "http_requests_in_flight",
    "Richieste HTTP attualmente in corso",
)

REVIEW_LENGTH_CHARS = Histogram(
    "sentiment_review_length_chars",
    "Lunghezza in caratteri delle recensioni ricevute",
    buckets=(10, 50, 100, 250, 500, 1000, 2500, 5000),
)

SENTIMENT_CONFIDENCE = Summary(
    "sentiment_confidence",
    "Distribuzione della confidence delle predizioni",
)