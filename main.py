import logging
import uvicorn

logging.basicConfig(
    filename="audit.log",
    level=logging.INFO,
    format="[%(levelname)s]%(name)s - %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)

from src.api import app

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)