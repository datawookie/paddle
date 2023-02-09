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


bcrypt = Bcrypt(app)

app.register_blueprint(blueprint)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
