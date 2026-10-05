from contextlib import asynccontextmanager

from kubernetes_asyncio import client, config
from kubernetes_asyncio.config.config_exception import ConfigException


async def load_config() -> None:
    """Use the service account in a Pod, or local kubeconfig during development."""
    try:
        config.load_incluster_config()
    except ConfigException:
        await config.load_kube_config()


@asynccontextmanager
async def get_core_api():
    await load_config()
    async with client.ApiClient() as api_client:
        yield client.CoreV1Api(api_client)


@asynccontextmanager
async def get_apps_api():
    await load_config()
    async with client.ApiClient() as api_client:
        yield client.AppsV1Api(api_client)
