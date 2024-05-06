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


def get_all_claims() -> str:
    claims = """
        <table style="width:100%">
        <tr>
        <th>Name</th>
        <th>Pool</th>
        <th>Namespace</th>
        <th>Status</th>
        <th>Message</th>
        <th>Info</th>
        </tr>
    """
    dyn_client = get_client()
    for _claim in ClusterClaim.get(dyn_client=dyn_client, namespace=HIVE_CLUSTER_NAMESPACE):
        claim_info = "<tr>"
        _instnce: ResourceInstance = _claim.instance
        claim_info += f"<td>{_instnce.metadata.name}</td>"
        claim_info += f"<td>{_instnce.spec.clusterPoolName}</td>"
        claim_info += f"<td>{_instnce.spec.namespace or 'Not Ready'}</td>"
        for cond in _instnce.status.conditions:
            if cond.type == "Pending":
                claim_info += f"<td>{cond.reason}</td>"
                claim_info += f"<td>{cond.message}</td>"

        claim_info += f"<td><a href='/claim?name={_instnce.metadata.name}'>View</a></td>"
        claim_info += "</tr>"
        claims += claim_info

    claims += "</table>"

    return claims


def get_cluster_pools() -> str:
    pools = """
        <table style="width:100%">
        <tr>
        <th>Name</th>
        <th>Size</th>
        <th>Ready</th>
        <th>Standby</th>
        </tr>
    """
    select_form = """
    <form action="/" method="POST">
    <label for="clusterpool">Claim from: </label>
    <select name="ClusterPools" class="Input" id="clusterpool">
    """
    dyn_client = get_client()
    for cp in ClusterPool.get(dyn_client=dyn_client, namespace=HIVE_CLUSTER_NAMESPACE):
        _instnce: ResourceInstance = cp.instance
        _name = _instnce.metadata.name
        _status = _instnce.status
        pool_info = "<tr>"
        pool_info += f"<td>{_name}</td>"
        pool_info += f"<td>{_instnce.spec.size}</td>"
        pool_info += f"<td>{_status.ready if _status else 'NA'}</td>"
        pool_info += f"<td>{_status.standby if _status else 'NA'}</td>"
        pool_info += "</tr>"
        pools += pool_info
        select_form += f"  <option value={_name}>{_name}</option>"

    pools += "</table>"
    select_form += "</select>"
    select_form += '<input type="submit" value="Claim cluster" /></form>'
    return f"{pools} <br /> {select_form}"


def claim_cluster(user: str, pool: str) -> str:
    _claim = ClusterClaim(
        name=f"{user}-{shortuuid.uuid()[0:5].lower()}-cluster-claim",
        namespace=HIVE_CLUSTER_NAMESPACE,
        cluster_pool_name=pool,
    )
    try:
        _claim.deploy()
    except Exception as exp:
        return f"<p>{exp.summary()}</p>"  # type: ignore[attr-defined]
    return f"<p>Cluster {_claim.name} claimed from {pool} by {user}</p>"


def claim_cluster_delete(claim_name: str) -> None:
    _claim = ClusterClaim(
        name=claim_name,
        namespace=HIVE_CLUSTER_NAMESPACE,
    )
    _claim.clean_up()


def delete_all_claims(user: str) -> str:
    dyn_client = get_client()
    deleted_claims = ""
    for _claim in ClusterClaim.get(dyn_client=dyn_client, namespace=HIVE_CLUSTER_NAMESPACE):
        if user in _claim.name:
            _claim.clean_up()
            deleted_claims += f"Deleted {_claim.name} <br />"

    return deleted_claims


def get_claimed_cluster_deployment(claim_name: str) -> ClusterDeployment | str:
    _claim = ClusterClaim(name=claim_name, namespace=HIVE_CLUSTER_NAMESPACE)
    _instance: ResourceInstance = _claim.instance
    if not _instance.spec.namespace:
        return "<p><b>ClusterDeployment not found for this claim</b></p>"

    return ClusterDeployment(name=_instance.spec.namespace, namespace=_instance.spec.namespace)


def get_claimed_cluster_web_console(claim_name: str) -> str:
    _cluster_deployment = get_claimed_cluster_deployment(claim_name=claim_name)
    if isinstance(_cluster_deployment, str):
        return _cluster_deployment

    _console_url = _cluster_deployment.instance.status.webConsoleURL
    return f"<p><b>Console:</b> <a href='{_console_url}'>{_console_url}</a></p>"


def get_claimed_cluster_creds(claim_name: str) -> str:
    _cluster_deployment = get_claimed_cluster_deployment(claim_name=claim_name)
    if isinstance(_cluster_deployment, str):
        return ""

    _secret = Secret(
        name=_cluster_deployment.instance.spec.clusterMetadata.adminPasswordSecretRef.name,
        namespace=_cluster_deployment.namespace,
    )
    return f"<p><b>username:</b> {_secret.instance.data.username}<br /><b>password:</b> {_secret.instance.data.password}</p>"


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

    return f"<p><b>Kubeconfig:</b> <a href='/kubeconfig/{_kubeconfig_file_name}'>Kubeconfig</a></p>"
