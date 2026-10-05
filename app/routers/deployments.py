from fastapi import APIRouter

from app.services.deploy_service import (
    list_deployments
)

router = APIRouter()


@router.get("/{namespace}")
def get_deployments(namespace: str):

    return list_deployments(namespace)