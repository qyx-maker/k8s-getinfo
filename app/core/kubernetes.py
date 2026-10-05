from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException


def load_config():
    try:
        config.load_incluster_config()
    except ConfigException:
        config.load_kube_config()


load_config()

core_api = client.CoreV1Api()
apps_api = client.AppsV1Api()