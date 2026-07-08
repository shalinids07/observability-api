from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import time
import uuid

app = FastAPI()

EMAIL = "23f1000746@ds.study.iitm.ac.in"

START_TIME = time.time()

REQUEST_COUNTER = Counter(
    "http_requests_total",
    "Total HTTP Requests"
)

logs = []


@app.middleware("http")
async def log_requests(request: Request, call_next):
    REQUEST_COUNTER.inc()

    request_id = str(uuid.uuid4())

    entry = {
        "level": "INFO",
        "ts": time.time(),
        "path": request.url.path,
        "request_id": request_id,
    }

    logs.append(entry)

    if len(logs) > 500:
        logs.pop(0)

    response = await call_next(request)
    return response


@app.get("/work")
def work(n: int):
    for _ in range(n):
        pass

    return {
        "email": EMAIL,
        "done": n
    }


@app.get("/metrics")
def metrics():
    return PlainTextResponse(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "uptime_s": time.time() - START_TIME
    }


@app.get("/logs/tail")
def tail(limit: int = 10):
    return logs[-limit:]
