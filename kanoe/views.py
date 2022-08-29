from flask import render_template

from . import app
import database as db

session = db.Session()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/boats")
def boats():
    return "Hello World!"


@app.route("/clubs")
def clubs():
    clubs = session.query(db.Club).all()
    return render_template("clubs.html", clubs=clubs)
