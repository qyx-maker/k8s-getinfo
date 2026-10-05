from core.kubernetes import get_apps_api

async def list_deployments(namespace: str) -> list[dict]:
    async with get_apps_api() as api:
        result = await api.list_namespaced_deployment(namespace=namespace)

    return [
        {
            "name": deployment.metadata.name,
            "namespace": deployment.metadata.namespace,
            "desired_replicas": deployment.spec.replicas,
            "ready_replicas": deployment.status.ready_replicas or 0,
            "available_replicas": deployment.status.available_replicas or 0,
        }
        for deployment in result.items
    ]
