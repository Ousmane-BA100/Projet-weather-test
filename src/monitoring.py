from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure le logging structuré"""
    logger = logging.getLogger()
    log_handler = logging.StreamHandler()
    
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s',
        timestamp=True
    )
    
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)
    
    return logger

def setup_metrics(app: FastAPI):
    """Configure les métriques Prometheus"""
    Instrumentator().instrument(app).expose(app)

def add_health_check(app: FastAPI):
    """Ajoute un endpoint de vérification de santé"""
    @app.get("/health", tags=["health"])
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "service": "weather-api"
        }