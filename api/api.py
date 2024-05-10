import os
from typing import Any, Dict
from flask import Flask, render_template, request, send_file, url_for, redirect, jsonify
from werkzeug.wrappers import Response
from flask_login import LoginManager, login_user, logout_user, current_user

import json
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    unset_jwt_cookies,
    JWTManager,
)


from utils import (
    claim_cluster,
    claim_cluster_delete,
    create_users,
    delete_all_claims,
    get_all_claims,
    get_claimed_cluster_creds,
    get_claimed_cluster_kubeconfig,
    get_claimed_cluster_web_console,
    get_cluster_pools,
    Users,
    db,
)

DB_URI = os.path.join("/tmp", "db.sqlite")
flask_app = Flask("hive-claim-flask-app", template_folder="hive_claim_flask_app/templates")
flask_app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_URI}"
flask_app.config["SECRET_KEY"] = os.environ["HIVE_CLAIM_FLASK_APP_SECRET_KEY"]
flask_app.config["JWT_SECRET_KEY"] = os.environ["HIVE_CLAIM_FLASK_APP_SECRET_KEY"]
jwt = JWTManager(flask_app)


login_manager = LoginManager()
login_manager.init_app(flask_app)


flask_app.jinja_env.globals.update(
    get_all_claims=get_all_claims,
    claim_cluster=claim_cluster,
    get_cluster_pools=get_cluster_pools,
    get_claimed_cluster_kubeconfig=get_claimed_cluster_kubeconfig,
    get_claimed_cluster_creds=get_claimed_cluster_creds,
    get_claimed_cluster_web_console=get_claimed_cluster_web_console,
)


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


@flask_app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response


@flask_app.route("/token", methods=["POST"])
def create_token():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user = Users.query.filter_by(username=email).first()
    if user and user.password == password:
        access_token = create_access_token(identity=email)
        response = {"access_token": access_token}
        return response

    return {"msg": "Wrong email or password"}, 401


@flask_app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@flask_app.route("/login", methods=["GET", "POST"])
def login() -> Response | str:
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form.get("username")).first()
        if not user:
            return redirect(url_for("login"))

        if user.password == request.form.get("password"):
            login_user(user)
            return redirect(url_for("home"))

    return render_template("login.html")


# @flask_app.route("/logout")
# def logout() -> Response:
#     logout_user()
#     return redirect(url_for("home"))
#


@flask_app.route("/cluster-pools", methods=["GET"])
# @jwt_required()
def cluster_pools() -> Response | Dict[str, Any]:
    pools = get_cluster_pools()
    # flask_app.logger.info(pools)
    return pools


@flask_app.route("/cluster-claims", methods=["GET"])
# @jwt_required()
def cluster_claims() -> Response | Dict[str, Any]:
    cliams = get_all_claims()
    # flask_app.logger.info(cliams)
    return cliams


@flask_app.route("/cluster-creds", methods=["GET"])
def cluster_creds_endpoint() -> Response | Dict[str, Any]:
    _claim_name = request.args.get("name")

    _console = get_claimed_cluster_web_console(claim_name=_claim_name)
    _kubeconfig_file = get_claimed_cluster_kubeconfig(claim_name=_claim_name)
    _creds = get_claimed_cluster_creds(claim_name=_claim_name)
    res = {
        "name": _claim_name,
        "kubeconfig": _kubeconfig_file,
        "console": _console,
        "creds": _creds,
    }
    # flask_app.logger.info(res)
    return res


@flask_app.route("/claim-cluster", methods=["GET"])
def claim_cluster_endpoint() -> Response | Dict[str, Any]:
    _pool_name = request.args.get("name")
    return claim_cluster(user="temp-user", pool=_pool_name)


@flask_app.route("/delete-claim", methods=["GET"])
def delete_claim_endpoint() -> Response | Dict[str, Any]:
    _claim_name = request.args.get("name")
    claim_cluster_delete(claim_name=_claim_name.strip())
    return {"deleted": _claim_name}


@flask_app.route("/", methods=["GET", "POST"])
def home() -> Response | str:
    if request.method == "POST":
        if current_user.is_authenticated:
            username = current_user.username
            if request.form.get("logout"):
                logout_user()
                return redirect(url_for("home"))

            if pool := request.form.get("ClusterPools"):
                claimed = claim_cluster(user=username, pool=pool)
                flask_app.jinja_env.globals.update(claimed=claimed)
                return redirect(url_for("home"))

            if request.form.get("delete_claim"):
                if claim_name := request.form.get("name"):
                    if username not in claim_name:
                        return render_template(
                            "home.html", delete_claim_error=f"{username} is not allowed to delete {claim_name}"
                        )

                    claim_cluster_delete(claim_name=claim_name.strip())

            if request.form.get("delete_all_claims"):
                deleted_claims = delete_all_claims(user=username)
                return render_template("home.html", deleted_claims=deleted_claims)

        else:
            user = Users.query.filter_by(username=request.form.get("username")).first()
            if not user:
                return redirect(url_for("home"))

            if user.password == request.form.get("password"):
                login_user(user)
                return redirect(url_for("home"))

    return render_template("home.html")


@flask_app.route("/claim", methods=["GET"])
def cluster_info() -> Response | str:
    return render_template("cluster-claimed.html", cluster_name=request.args.get("name"))


@flask_app.route("/kubeconfig/<filename>", methods=["GET"])
def download_kubeconfig(filename: str) -> Response | str:
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
