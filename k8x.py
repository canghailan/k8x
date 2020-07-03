import time
from kubernetes import client, config

config.load_kube_config()
api = client.CoreV1Api()


def list_pod_for_node(node_name):
    pods = api.list_pod_for_all_namespaces(watch=False)
    return [pod for pod in pods.items if pod.spec.node_name == node_name]


def delete_label_pod(label_selector, delay=120):
    pods = api.list_pod_for_all_namespaces(
        watch=False, label_selector=label_selector)
    for pod in pods.items:
        print(f"""{time.strftime("%Y-%m-%d %H:%M:%S")} delete {pod.metadata.name}""")
        api.delete_namespaced_pod(pod.metadata.name, pod.metadata.namespace)
        if delay > 0:
            time.sleep(delay)


def delete_node_pod(node_name, namespace="*", delay=120):
    pods = list_pod_for_node(node_name)
    for pod in pods:
        if pod.metadata.owner_references is not None:
            owner_kind = ",".join(
                [o.kind for o in pod.metadata.owner_references])
            if owner_kind == "DaemonSet":
                print(
                    f"""{time.strftime("%Y-%m-%d %H:%M:%S")} skip {pod.metadata.name}""")
                continue
        else:
            print(
                f"""{time.strftime("%Y-%m-%d %H:%M:%S")} skip {pod.metadata.name}""")
            continue
        if namespace == "*" or pod.metadata.namespace == namespace:
            print(
                f"""{time.strftime("%Y-%m-%d %H:%M:%S")} delete {pod.metadata.name}""")
            api.delete_namespaced_pod(
                pod.metadata.name, pod.metadata.namespace)
            if delay > 0:
                time.sleep(delay)


# delete_node_pod("cn-hangzhou.172.18.194.23", "kube-system", 30)
# delete_label_pod("app=mysql")
# delete_label_pod("app=postgres")
# delete_label_pod("app=mongo")
# delete_label_pod("app=redis")
# delete_label_pod("app=elasticsearch")
# delete_label_pod("app=kafka")
# delete_node_pod("cn-hangzhou.172.18.194.23", "*", 30)
