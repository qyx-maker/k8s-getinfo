# Kubernetes Status API

通过 FastAPI 读取 Kubernetes API Server 中的 Node、Pod 和 Deployment 状态。接口只读，不提供资源修改操作。Pod 的 `phase` 与容器 `ready` 分开返回；`Running` 不代表容器已经就绪。

## 本地运行

在项目根目录创建并激活 Python 虚拟环境后，安装依赖：

```powershell
python -m pip install -r requirements.txt
```

从 `app` 目录启动，保证 `routers`、`services` 和 `core` 使用同一个导入根目录：

```powershell
cd app
python -m uvicorn app:app --reload
```

打开 `http://127.0.0.1:8000/docs` 查看接口。查询使用 Pod 内的 ServiceAccount 配置；在本地运行时使用当前用户的 kubeconfig。集群未启动时，应用可以启动，但资源查询可能返回 503。

| 接口 | 内容 |
| --- | --- |
| `GET /api/nodes` | 节点名称与 Ready condition |
| `GET /api/pods/{namespace}` | Pod 阶段、容器就绪、重启次数、所在节点 |
| `GET /api/deployments/{namespace}` | 期望、就绪、可用副本数 |

## 不依赖集群的测试

在项目根目录运行：

```powershell
python -m unittest discover -s tests -v
```

测试模拟 Kubernetes 客户端响应，验证路由返回、状态字段和错误状态码。集群启动后，可把 API 的结果与相同 kubeconfig 下的 `kubectl get nodes`、`kubectl get pods -n default`、`kubectl get deployments -n default` 对照。
