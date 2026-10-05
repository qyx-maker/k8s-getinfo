from core.kubernetes import get_core_api

async def list_nodes() -> list[dict]:
    async with get_core_api() as api:
        result = await api.list_node()

    nodes = []
    for node in result.items:
        conditions = node.status.conditions or []
        ready = next((c.status for c in conditions if c.type == "Ready"), "Unknown")
        nodes.append({"name": node.metadata.name, "ready_status": ready})
    return nodes
