from core.kubernetes import get_core_api

async def list_pods(namespace: str) -> list[dict]:
    async with get_core_api() as api:
        result = await api.list_namespaced_pod(namespace=namespace)

    pods = []
    for pod in result.items:
        containers = pod.status.container_statuses or []
        pods.append({
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "phase": pod.status.phase,
            "ready": bool(containers) and all(c.ready for c in containers),
            "restarts": sum(c.restart_count for c in containers),
            "node": pod.spec.node_name,
        })
    return pods
