from fastapi import FastAPI, Request
import time
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram
import uvicorn

# Création des métriques
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

app = FastAPI()

# Configuration de l'instrumentation
instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=["/metrics", "/health"]
)
instrumentator.instrument(app).expose(app)

# Middleware pour le suivi des requêtes
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    method = request.method
    endpoint = request.url.path
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=method,
        endpoint=endpoint,
        http_status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=method,
        endpoint=endpoint
    ).observe(process_time)
    
    return response

# Routes de base
@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API Météo"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Démarrer l'application avec Uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)