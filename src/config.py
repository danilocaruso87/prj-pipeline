import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# URL fissato di default: garanzia di replicabilità (stesso file = stesso modello).
# Può essere sovrascritto da config.yaml (chiave model.source) senza toccare il codice.
_DEFAULT_MODEL_URL = (
    "https://raw.githubusercontent.com/Profession-AI/progetti-devops/main/"
    "Deploy%20e%20monitoraggio%20di%20un%20modello%20di%20sentiment%20analysis%20per%20recensioni/"
    "sentiment_analysis_model.pkl"
)
AUDIT_LOG = "audit.log"


def _load_yaml_config() -> dict:
    """Legge config.yaml se presente; errori/assenza → config vuota (si usano i default)."""
    path = Path(__file__).resolve().parent.parent / "config.yaml"
    if not path.exists():
        return {}
    try:
        import yaml  # pyyaml, aggiunta ai requirements

        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        logger.info("Config caricata da %s", path)
        return data
    except Exception:
        logger.exception("Errore lettura %s: uso i default", path)
        return {}


_cfg = _load_yaml_config()
_model_source = (_cfg.get("model") or {}).get("source") or _DEFAULT_MODEL_URL

# Sorgente effettiva del modello: URL remota (http/https) o path locale.
# model.py la usa così: URL → download httpx; path locale → lettura da disco.
MODEL_URL = _model_source
MODEL_PATH = None if str(MODEL_URL).startswith(("http://", "https://")) else str(MODEL_URL)
