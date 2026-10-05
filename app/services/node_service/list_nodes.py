from kubernetes.aio.client.api_client import ApiClient
from kubernetes.aio.client.exceptions import ApiException
from app.core.kubernetes import core_api

async def list_nodes(namespace:str):

    async with ApiClient() as api:
        print(f"集群node情况:")
        ret = await core_api.list_node(namespace=namespace)
        for i in ret.items:
            name = i.metadata.name
            print(f"{name}")