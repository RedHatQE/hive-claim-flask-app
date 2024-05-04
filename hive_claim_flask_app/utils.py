from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from kubernetes.dynamic.resource import ResourceInstance
from ocp_resources.cluster_claim import ClusterClaim
from ocp_utilities.infra import get_client
import os

from pyaml_env import parse_config
import shortuuid

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
        <th>Status</th>
        <th>Message</th>
        </tr>
    """
    dyn_client = get_client()
    for _claim in ClusterClaim.get(dyn_client=dyn_client, namespace=os.getenv("HIVE_NAMESPACE")):
        claim_info = "<tr>"
        _instnce: ResourceInstance = _claim.instance
        claim_info += f"<td>{_instnce.metadata.name}</td>"
        claim_info += f"<td>{_instnce.spec.clusterPoolName}</td>"
        for cond in _instnce.status.conditions:
            if cond.type == "Pending":
                claim_info += f"<td>{cond.reason}</td>"
                claim_info += f"<td>{cond.message}</td>"

        claim_info += "</tr>"
        claims += claim_info

    claims += "</table>"

    return claims


def get_cluster_pools() -> str:
    # TODO: Get cluster pools from OCP
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
    for cp in ["msiqe-4.15"]:
        pool_info = "<tr>"
        pool_info += f"<td>{cp}</td>"
        pool_info += "<td>5</td>"
        pool_info += "<td>5</td>"
        pool_info += "<td>0</td>"
        pool_info += "</tr>"
        pools += pool_info
        select_form += f"  <option value={cp}>{cp}</option>"

    pools += "</table>"
    select_form += "</select>"
    select_form += '<input type="submit" value="Claim cluster" /></form>'
    return f"{pools} <br /> {select_form}"


def claim_cluster(user: str, pool: str) -> str:
    _claim = ClusterClaim(
        name=f"{user}-{shortuuid.uuid()[0:5].lower()}-cluster-claim",
        namespace=os.getenv("HIVE_NAMESPACE"),
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
        namespace=os.getenv("HIVE_NAMESPACE"),
    )
    _claim.clean_up()


def delete_all_claims() -> None:
    dyn_client = get_client()
    for _claim in ClusterClaim.get(dyn_client=dyn_client, namespace=os.getenv("HIVE_NAMESPACE")):
        _claim.clean_up()
