from fastapi import APIRouter

from services.node_service.list_nodes import list_nodes

router = APIRouter()


@router.get("/api/nodes")
async def get_nodes():
    return await list_nodes()
