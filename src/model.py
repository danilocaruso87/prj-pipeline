import logging
import pickle
import httpx
from src import config

logger = logging.getLogger(__name__)

pipeline = None   # modello caricato in memoria
is_ready = False  # True solo se il caricamento è andato a buon fine

async def load_model():
    global pipeline, is_ready
    try:
        if config.MODEL_PATH:
            # Sorgente locale: file .pkl montato o copiato nel container
            from pathlib import Path
            raw = Path(config.MODEL_PATH).read_bytes()
            logger.info("Modello letto da file locale: %s", config.MODEL_PATH)
        else:
            async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
                resp = await client.get(config.MODEL_URL)
                resp.raise_for_status()
                raw = resp.content
            logger.info("Modello scaricato da %s", config.MODEL_URL)
        pipeline = pickle.loads(raw)
        is_ready = True
        logger.info("Modello caricato")
    except Exception:
        pipeline = None
        is_ready = False
        logger.exception("Impossibile caricare modello")