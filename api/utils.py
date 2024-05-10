from typing import Dict, List
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from kubernetes.dynamic.resource import ResourceInstance
from ocp_resources.cluster_claim import ClusterClaim
from ocp_resources.cluster_pool import ClusterPool
from ocp_resources.cluster_deployment import ClusterDeployment
from ocp_resources.secret import Secret
from ocp_utilities.infra import base64, get_client
import os

from pyaml_env import parse_config
import shortuuid

HIVE_CLUSTER_NAMESPACE = os.environ["HIVE_CLAIM_FLASK_APP_NAMESPACE"]

db = SQLAlchemy()


class Users(UserMixin, db.Model):  # type: ignore[name-defined]
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)


def create_users() -> None:
    _config = parse_config(os.environ["HIVE_CLAIM_FLASK_APP_USERS_FILE"])
    _pass = _config["password"]
    for user in _config["users"]:
        user = Users(username=user, password=_pass)
        db.session.add(user)


def get_all_claims() -> List[Dict[str, str]]:
    res = []
    dyn_client = get_client()
    for _claim in ClusterClaim.get(dyn_client=dyn_client, namespace=HIVE_CLUSTER_NAMESPACE):
        _instnce: ResourceInstance = _claim.instance

        res.append({
            "name": _instnce.metadata.name,
            "pool": _instnce.spec.clusterPoolName,
            "namespace": _instnce.spec.namespace or "Not Ready",
        })

    return res


def get_cluster_pools() -> List[Dict[str, str]]:
    res = []
    dyn_client = get_client()
    for cp in ClusterPool.get(dyn_client=dyn_client, namespace=HIVE_CLUSTER_NAMESPACE):
        _instnce: ResourceInstance = cp.instance
        _name = _instnce.metadata.name
        _size = _instnce.spec.size
        _status = _instnce.status
        _pool = {
            "name": _name,
            "size": _size,
            "claimed": _size - _status.size if _status else 0,
            "available": _status.size if _status else 0,
        }
        res.append(_pool)

    return res


def claim_cluster(user: str, pool: str) -> Dict[str, str]:
    res = {"error": "", "name": ""}
    _claim = ClusterClaim(
        name=f"{user}-{shortuuid.uuid()[0:5].lower()}-cluster-claim",
        namespace=HIVE_CLUSTER_NAMESPACE,
        cluster_pool_name=pool,
    )
    try:
        _claim.deploy()
    except Exception as exp:
        res["error"] = exp.summary()
    res["name"] = _claim.name
    return res


def claim_cluster_delete(claim_name: str) -> None:
    _claim = ClusterClaim(
        name=claim_name,
        namespace=HIVE_CLUSTER_NAMESPACE,
    )
    _claim.clean_up()


def delete_all_claims(user: str) -> Dict[str, str]:
    dyn_client = get_client()
    deleted_claims = ""
    for _claim in ClusterClaim.get(dyn_client=dyn_client, namespace=HIVE_CLUSTER_NAMESPACE):
        if user in _claim.name:
            _claim.clean_up()
            deleted_claims += f"Deleted {_claim.name} <br />"

    return {"deleted_claims": deleted_claims}


def get_claimed_cluster_deployment(claim_name: str) -> ClusterDeployment | str:
    _claim = ClusterClaim(name=claim_name, namespace=HIVE_CLUSTER_NAMESPACE)
    _instance: ResourceInstance = _claim.instance
    if not _instance.spec.namespace:
        return "<p><b>ClusterDeployment not found for this claim</b></p>"

    return ClusterDeployment(name=_instance.spec.namespace, namespace=_instance.spec.namespace)


def get_claimed_cluster_web_console(claim_name: str) -> Dict[str, str]:
    _cluster_deployment = get_claimed_cluster_deployment(claim_name=claim_name)
    if isinstance(_cluster_deployment, str):
        return _cluster_deployment

    _console_url = _cluster_deployment.instance.status.webConsoleURL
    return {"console_url": _console_url}


def get_claimed_cluster_creds(claim_name: str) -> Dict[str, str]:
    _cluster_deployment = get_claimed_cluster_deployment(claim_name=claim_name)
    if isinstance(_cluster_deployment, str):
        return {"username": "", "password": ""}

    _secret = Secret(
        name=_cluster_deployment.instance.spec.clusterMetadata.adminPasswordSecretRef.name,
        namespace=_cluster_deployment.namespace,
    )
    return {"username": _secret.instance.data.username, "password": _secret.instance.data.password}


def get_claimed_cluster_kubeconfig(claim_name: str) -> str:
    _cluster_deployment = get_claimed_cluster_deployment(claim_name=claim_name)
    if isinstance(_cluster_deployment, str):
        return ""

    _secret = Secret(
        name=_cluster_deployment.instance.spec.clusterMetadata.adminKubeconfigSecretRef.name,
        namespace=_cluster_deployment.namespace,
    )
    _kubeconfig_file_name = f"kubeconfig-{claim_name}"
    with open(f"/tmp/{_kubeconfig_file_name}", "w") as fd:
        fd.write(base64.b64decode(_secret.instance.data.kubeconfig).decode())

    return _kubeconfig_file_name
