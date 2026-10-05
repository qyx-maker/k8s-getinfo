from fastapi import APIRouter

from services.deploy_service.list_deployments import list_deployments

router = APIRouter()


@router.get("/api/deployments/{namespace}")
async def get_deployments(namespace: str):
    return await list_deployments(namespace)
