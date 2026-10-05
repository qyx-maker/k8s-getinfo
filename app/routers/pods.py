from fastapi import APIRouter

from app.services.pod_service import list_pods


router = APIRouter()


@router.get("/{namespace}")
def get_pods(namespace: str):

    return list_pods(namespace)