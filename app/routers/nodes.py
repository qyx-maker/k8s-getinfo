from fastapi import APIRouter

from app.services.deploy_service import (
    list_nodes
)

router = APIRouter()


@router.get("/")
def get_nodes(namespace: str):

    return list_nodes(namespace)