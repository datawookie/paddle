import os
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask import Flask
import logging

from .views import blueprint
from .views.common import db, session

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)7s] %(message)s",
    # This will clobber existing handlers.
    force=True,
)
logging.getLogger("fontTools").setLevel(logging.WARNING)
logging.getLogger("weasyprint").setLevel(logging.ERROR)


def factory():
    app = Flask(__name__, static_url_path="")

    # Secret key for sessions.
    #
    app.secret_key = b"8842f61bd2e13ad8285f57a551e2e6cb3521f38740ac0358e74077714eea0c82"

    # app.config["EXPLAIN_TEMPLATE_LOADING"] = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SECRET_KEY"] = os.urandom(24).hex()

    # Initialise Flask-Bootstrap.
    #
    Bootstrap5(app)

    login_manager = LoginManager()
    #
    # login_manager.session_protection = "strong"
    # login_manager.login_view = "login"
    # login_manager.login_message_category = "info"
    #
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Reload user object from user ID stored in session.
        return session.query(db.User).get(user_id)

    # This will disable login required (use for development and testing).
    #
    app.config["LOGIN_DISABLED"] = True

    Bcrypt(app)

    app.register_blueprint(blueprint)

    return app


app = factory()


@app.template_filter("timedelta_hours")
def timedelta_hours(timedelta):
    seconds = timedelta.total_seconds()
    hours = seconds // 3600
    seconds -= hours * 3600
    minutes = seconds // 60
    seconds -= minutes * 60
    return "%02d:%02d:%02d" % (hours, minutes, seconds)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
