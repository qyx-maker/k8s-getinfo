import importlib
import json
import sys
import unittest
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from app import app  # noqa: E402
from kubernetes_asyncio.client.exceptions import ApiException  # noqa: E402
from kubernetes_asyncio.config.config_exception import ConfigException  # noqa: E402


def obj(**values):
    return SimpleNamespace(**values)


async def request(path):
    messages = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        messages.append(message)

    scope = {
        "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
        "method": "GET", "scheme": "http", "path": path,
        "raw_path": path.encode(), "query_string": b"", "headers": [],
        "client": ("test", 1234), "server": ("test", 80),
    }
    await app(scope, receive, send)
    status = next(m["status"] for m in messages if m["type"] == "http.response.start")
    body = b"".join(m.get("body", b"") for m in messages if m["type"] == "http.response.body")
    return status, json.loads(body)


class StatusApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_nodes_return_ready_condition(self):
        service = importlib.import_module("services.node_service.list_nodes")
        api = obj(list_node=AsyncMock(return_value=obj(items=[
            obj(metadata=obj(name="node-1"), status=obj(conditions=[obj(type="Ready", status="True")]))
        ])))

        @asynccontextmanager
        async def fake_api():
            yield api

        with patch.object(service, "get_core_api", fake_api):
            status, body = await request("/api/nodes")
        self.assertEqual((status, body), (200, [{"name": "node-1", "ready_status": "True"}]))

    async def test_pods_return_phase_readiness_and_restarts(self):
        service = importlib.import_module("services.pod_service.list_pods")
        api = obj(list_namespaced_pod=AsyncMock(return_value=obj(items=[obj(
            metadata=obj(name="web", namespace="default"),
            status=obj(phase="Running", container_statuses=[obj(ready=False, restart_count=2)]),
            spec=obj(node_name="node-1"),
        )])))

        @asynccontextmanager
        async def fake_api():
            yield api

        with patch.object(service, "get_core_api", fake_api):
            status, body = await request("/api/pods/default")
        self.assertEqual(status, 200)
        self.assertEqual(body[0]["phase"], "Running")
        self.assertFalse(body[0]["ready"])
        self.assertEqual(body[0]["restarts"], 2)
        api.list_namespaced_pod.assert_awaited_once_with(namespace="default")

    async def test_deployments_return_replica_counts(self):
        service = importlib.import_module("services.deploy_service.list_deployments")
        api = obj(list_namespaced_deployment=AsyncMock(return_value=obj(items=[obj(
            metadata=obj(name="web", namespace="default"),
            spec=obj(replicas=3), status=obj(ready_replicas=2, available_replicas=None),
        )])))

        @asynccontextmanager
        async def fake_api():
            yield api

        with patch.object(service, "get_apps_api", fake_api):
            status, body = await request("/api/deployments/default")
        self.assertEqual(status, 200)
        self.assertEqual(body[0]["desired_replicas"], 3)
        self.assertEqual(body[0]["ready_replicas"], 2)
        self.assertEqual(body[0]["available_replicas"], 0)

    async def test_kubernetes_permission_error_is_not_reported_as_success(self):
        service = importlib.import_module("services.node_service.list_nodes")
        api = obj(list_node=AsyncMock(side_effect=ApiException(status=403, reason="Forbidden")))

        @asynccontextmanager
        async def fake_api():
            yield api

        with patch.object(service, "get_core_api", fake_api):
            status, body = await request("/api/nodes")
        self.assertEqual(status, 403)
        self.assertEqual(body["upstream_status"], 403)

    async def test_missing_cluster_config_returns_503(self):
        service = importlib.import_module("services.node_service.list_nodes")

        @asynccontextmanager
        async def unavailable_api():
            raise ConfigException("No kubeconfig")
            yield

        with patch.object(service, "get_core_api", unavailable_api):
            status, body = await request("/api/nodes")
        self.assertEqual(status, 503)
        self.assertEqual(body["detail"], "Kubernetes cluster unavailable")


if __name__ == "__main__":
    unittest.main()
