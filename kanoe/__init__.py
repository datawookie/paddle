import os
from flask_bootstrap import Bootstrap5
from flask import Flask
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)7s] %(message)s",
    # This will clobber existing handlers.
    force=True,
)


app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SECRET_KEY"] = os.urandom(24).hex()

bootstrap = Bootstrap5(app)

from . import views

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
