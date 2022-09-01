from flask_bootstrap import Bootstrap5
from flask import Flask

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

bootstrap = Bootstrap5(app)

from . import views
