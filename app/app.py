import os
import shortuuid
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from pyaml_env import parse_config
from ocp_resources.cluster_claim import ClusterClaim
from ocp_utilities.infra import get_client

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "TOPSECRET"
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)


def get_all_claims():
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
        _instnce = _claim.instance
        claim_info += f"<td>{_instnce.metadata.name}</td>"
        claim_info += f"<td>{_instnce.spec.clusterPoolName}</td>"
        for cond in _instnce.status.conditions:
            if cond.type == "Pending":
                claim_info += f"<td>{cond.reason}</td>"
                claim_info += f"<td>{cond.message}</td>"

        claim_info += "</tr>"
        claims += f"{claim_info}"

    claims += "</table>"

    return claims


def get_cluster_pools():
    # TODO: Get cluster pools from OCP
    select_form = """
    <form action="/" method="POST">
    <label for="clusterpool">Claim from: </label>
    <select name="ClusterPools" class="Input" id="clusterpool">
    """
    for cp in ["msiqe-4.15"]:
        select_form += f"  <option value={cp}>{cp}</option>"

    select_form += "</select>"
    select_form += '<input type="submit" value="Claim cluster" /></form>'
    return select_form


def claim_cluster(user, pool):
    _claim = ClusterClaim(
        name=f"{user}-{shortuuid.uuid()[0:5].lower()}-cluster-claim",
        namespace=os.getenv("HIVE_NAMESPACE"),
        cluster_pool_name=pool,
    )
    try:
        _claim.deploy()
    except Exception as exp:
        return f"<p>{exp.summary()}</p>"
    return f"<p>Cluster {_claim.name} claimed from {pool} by {user}</p>"


def claim_cluster_delete(claim_name):
    _claim = ClusterClaim(
        name=claim_name,
        namespace=os.getenv("HIVE_NAMESPACE"),
    )
    _claim.clean_up()


app.jinja_env.globals.update(
    get_all_claims=get_all_claims,
    claim_cluster=claim_cluster,
    get_cluster_pools=get_cluster_pools,
)


def create_users() -> None:
    for user in parse_config("app/users.yaml")["users"]:
        user = Users(username=user, password="msiqe")
        db.session.add(user)


db.init_app(app)
with app.app_context():
    db.drop_all()
    db.session.commit()
    db.create_all()
    create_users()
    db.session.commit()


@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form.get("username")).first()
        if not user:
            return redirect(url_for("login"))

        if user.password == request.form.get("password"):
            login_user(user)
            return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        if current_user.is_authenticated:
            if request.form.get("logout"):
                logout_user()
                return redirect(url_for("home"))

            if pool := request.form.get("ClusterPools"):
                claimed = claim_cluster(user=current_user.username, pool=pool)
                app.jinja_env.globals.update(claimed=claimed)
                return redirect(url_for("home"))

            if request.form.get("delete_claim"):
                if claim_name := request.form.get("name"):
                    claim_cluster_delete(claim_name=claim_name.strip())
        else:
            user = Users.query.filter_by(username=request.form.get("username")).first()
            if not user:
                return redirect(url_for("home"))

            if user.password == request.form.get("password"):
                login_user(user)
                return redirect(url_for("home"))

    return render_template("home.html")


if __name__ == "__main__":
    os.environ["HIVE_NAMESPACE"] = "msiqe"
    os.environ["KUBECONFIG"] = "/home/myakove/work/CSPI/hive/msiqe-kubeconfig.txt"
    app.run(debug=True)
