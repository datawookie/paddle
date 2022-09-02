from flask import render_template

from . import app
import database as db

session = db.Session()


@app.route("/")
def index():
    return render_template("index.j2")


@app.route("/boats")
def boats():
    return "Hello World!"


@app.route("/clubs")
def clubs():
    clubs = session.query(db.Club).all()
    return render_template("clubs.j2", clubs=clubs)


@app.route("/club/<club_id>")
def club(club_id):
    club = session.query(db.Club).get(club_id)
    return render_template("club.j2", club=club)


@app.route("/time-trial")
def time_trial():
    members = session.query(db.Member).all()
    return render_template("time-trial.j2", members=members)


@app.route("/member/<member_id>")
def member(member_id):
    member = session.query(db.Member).get(member_id)
    return render_template("member.j2", member=member)


@app.route("/entries")
def entries():
    entries = session.query(db.Entry).all()
    return render_template("entries.j2", entries=entries)


@app.route("/entry/<entry_id>")
def entry(entry_id):
    entry = session.query(db.Entry).get(entry_id)
    return render_template("entry.j2", entry=entry)
