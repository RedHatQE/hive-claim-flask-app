import os
from flask import Flask, render_template, request, url_for, redirect
from werkzeug.wrappers import Response
from flask_login import LoginManager, login_user, logout_user, current_user


from hive_claim_flask_app.utils import (
    claim_cluster,
    claim_cluster_delete,
    create_users,
    delete_all_claims,
    get_all_claims,
    get_cluster_pools,
    Users,
    db,
)

flask_app = Flask("hive-claim-flask-app", template_folder="hive_claim_flask_app/templates")
flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
flask_app.config["SECRET_KEY"] = os.environ["HIVE_CLAIM_FLASK_APP_SECRET_KEY"]


login_manager = LoginManager()
login_manager.init_app(flask_app)


flask_app.jinja_env.globals.update(
    get_all_claims=get_all_claims,
    claim_cluster=claim_cluster,
    get_cluster_pools=get_cluster_pools,
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


@flask_app.route("/logout")
def logout() -> Response:
    logout_user()
    return redirect(url_for("home"))


@flask_app.route("/", methods=["GET", "POST"])
def home() -> Response | str:
    if request.method == "POST":
        if current_user.is_authenticated:
            if request.form.get("logout"):
                logout_user()
                return redirect(url_for("home"))

            if pool := request.form.get("ClusterPools"):
                claimed = claim_cluster(user=current_user.username, pool=pool)
                flask_app.jinja_env.globals.update(claimed=claimed)
                return redirect(url_for("home"))

            if request.form.get("delete_claim"):
                if claim_name := request.form.get("name"):
                    claim_cluster_delete(claim_name=claim_name.strip())

            if request.form.get("delete_all_claims"):
                delete_all_claims()

        else:
            user = Users.query.filter_by(username=request.form.get("username")).first()
            if not user:
                return redirect(url_for("home"))

            if user.password == request.form.get("password"):
                login_user(user)
                return redirect(url_for("home"))

    return render_template("home.html")


def main() -> None:
    flask_app.logger.info(f"Starting {flask_app.name} app")
    flask_app.run(
        port=int(os.getenv("HIVE_CLAIM_FLASK_APP_PORT", 5000)),
        host=os.getenv("HIVE_CLAIM_FLASK_APP_HOST", "0.0.0.0"),
        use_reloader=os.getenv("HIVE_CLAIM_FLASK_APP_RELOAD", False),
        debug=bool(os.getenv("HIVE_CLAIM_FLASK_APP_DEBUG", False)),
    )


if __name__ == "__main__":
    main()
