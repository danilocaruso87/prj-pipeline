

FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# --default-timeout/--retries: pip piu' paziente con reti lente o a singhiozzo
RUN pip install --no-cache-dir --default-timeout=100 --retries 5 -r requirements.txt

COPY src/ ./src/
COPY main.py ./main.py
COPY config.yaml ./config.yaml

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]