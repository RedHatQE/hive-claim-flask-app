import os
from typing import Any, Dict, List
from flask import Flask, Response, request, send_file
from flask_login import LoginManager
from flask_login import login_user, logout_user, current_user


from utils import (
    claim_cluster,
    claim_cluster_delete,
    create_users,
    get_all_claims,
    get_cluster_pools,
    Users,
    db,
)

DB_URI = os.path.join("/tmp", "db.sqlite")
flask_app = Flask("hive-claim-flask-app", template_folder="hive_claim_flask_app/templates")
flask_app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_URI}"
flask_app.config["SECRET_KEY"] = os.environ["HIVE_CLAIM_FLASK_APP_SECRET_KEY"]


login_manager = LoginManager()
login_manager.init_app(flask_app)


db.init_app(flask_app)
with flask_app.app_context():
    db.drop_all()
    db.session.commit()
    db.create_all()
    create_users()
    db.session.commit()


@login_manager.user_loader
def loader_user(user_id: str) -> Users:
    return Users.query.get(user_id)


@flask_app.route("/login", methods=["GET", "POST"])
def login() -> Dict[str, Any]:
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form.get("username")).first()
        if not user:
            return {"error": "User not found", "authenticated": False}

        if user.password == request.form.get("password"):
            login_user(user)
            return {"error": "", "authenticated": True}

    return {"error": "", "authenticated": False}


@flask_app.route("/logout")
def logout() -> str:
    logout_user()
    return "Logged out"


@flask_app.route("/is-authenticated", methods=["GET"])
def is_authenticated_endpoint() -> str:
    return "Authenticated" if current_user.is_authenticated else "Not Authenticated"


@flask_app.route("/cluster-pools", methods=["GET"])  # type: ignore[type-var]
def cluster_pools_endpoint() -> List[Dict[str, str]]:
    return get_cluster_pools()


@flask_app.route("/cluster-claims", methods=["GET"])  # type: ignore[type-var]
def cluster_claims_endpoint() -> List[Dict[str, str]]:
    return get_all_claims()


@flask_app.route("/claim-cluster", methods=["GET"])
def claim_cluster_endpoint() -> Dict[str, str]:
    _pool_name: str = request.args.get("name")  # type: ignore[assignment]
    return claim_cluster(user="temp-user", pool=_pool_name)


@flask_app.route("/delete-claim", methods=["GET"])
def delete_claim_endpoint() -> Dict[str, str]:
    _claim_name: str = request.args.get("name")  # type: ignore[assignment]
    claim_cluster_delete(claim_name=_claim_name.strip())
    return {"deleted": _claim_name}


@flask_app.route("/kubeconfig/<filename>", methods=["GET"])
def download_kubeconfig_endpoint(filename: str) -> Response:
    return send_file(f"/tmp/{filename}", download_name=filename, as_attachment=True)  # type: ignore[call-arg]


def main() -> None:
    flask_app.logger.info(f"Starting {flask_app.name} app")
    flask_app.run(
        port=int(os.getenv("HIVE_CLAIM_FLASK_APP_PORT", 5000)),
        host=os.getenv("HIVE_CLAIM_FLASK_APP_HOST", "0.0.0.0"),
        use_reloader=bool(os.getenv("HIVE_CLAIM_FLASK_APP_RELOAD", False)),
        debug=bool(os.getenv("HIVE_CLAIM_FLASK_APP_DEBUG", False)),
    )


if __name__ == "__main__":
    main()
