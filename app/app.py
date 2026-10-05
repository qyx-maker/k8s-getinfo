import asyncio

from aiohttp import ClientError
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from kubernetes_asyncio.client.exceptions import ApiException
from kubernetes_asyncio.config.config_exception import ConfigException

from routers import deployments, nodes, pods

app = FastAPI(title="Kubernetes Status API")

app.include_router(nodes.router)
app.include_router(pods.router)
app.include_router(deployments.router)


@app.exception_handler(ApiException)
async def handle_kubernetes_error(request: Request, exc: ApiException):
    status = exc.status if exc.status in (401, 403, 404) else 502
    return JSONResponse(
        status_code=status,
        content={"detail": "Kubernetes API request failed", "upstream_status": exc.status},
    )


@app.exception_handler(ConfigException)
@app.exception_handler(ClientError)
@app.exception_handler(asyncio.TimeoutError)
async def handle_cluster_unavailable(request: Request, exc: Exception):
    return JSONResponse(status_code=503, content={"detail": "Kubernetes cluster unavailable"})
