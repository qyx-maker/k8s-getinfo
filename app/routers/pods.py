from fastapi import APIRouter

from services.pod_service.list_pods import list_pods


router = APIRouter()


@router.get("/api/pods/{namespace}")
async def get_pods(namespace: str):
    return await list_pods(namespace)
