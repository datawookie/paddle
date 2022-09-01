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


@app.route("/time-trial")
def time_trial():
    members = session.query(db.Member).all()
    return render_template("time-trial.html", members=members)


@app.route("/member/<member_id>")
def member(member_id):
    member = session.query(db.Member).get(member_id)
    return render_template("member.html", member=member)
