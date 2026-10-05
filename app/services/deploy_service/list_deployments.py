from kubernetes.aio.client.api_client import ApiClient
from kubernetes.aio.client.exceptions import ApiException
from app.core.kubernetes import core_api,apps_api

async def list_deployments(namespace:str):

    async with ApiClient() as api:
        print(f"命名空间{namespace}下的全部deployment:")
        try:
            ret = await apps_api.list_namespaced_deployment(namespace=namespace)
        except ApiException as e:
            print(f"查询失败: {e.status} {e.reason}")
            return
        for i in ret.items:
            name = i.metadata.name
            print(f"{name}")