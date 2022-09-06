from flask import render_template, request, url_for, flash, redirect

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


@app.route("/races")
def races():
    races = session.query(db.Race).all()
    return render_template("races.j2", races=races)


@app.route("/race/<race_id>")
def race(race_id):
    entries = session.query(db.Entry).filter(db.Entry.race_id == race_id).all()
    return render_template("race.j2", race_id=race_id, entries=entries)


@app.route("/race/<race_id>/entry/<entry_id>")
def entry(race_id, entry_id):
    entry = session.query(db.Entry).get(entry_id)
    return render_template("entry.j2", entry=entry)


@app.route("/paddlers", methods=("GET", "POST"))
def paddlers():
    if request.method == "POST":
        first = request.form["first"]
        middle = request.form["middle"]
        last = request.form["last"]

        if not first:
            flash("First name is required!", "danger")
        elif not last:
            flash("Last name is required!", "danger")
        else:
            paddler = db.Paddler(
                first=first,
                middle=middle,
                last=last,
            )
            session.add(paddler)
            session.commit()

            flash("Added a new paddler.", "success")

            return redirect(url_for("paddlers"))

    paddlers = session.query(db.Paddler).all()
    return render_template("paddlers.j2", paddlers=paddlers)


@app.route("/paddler/<paddler_id>")
def paddler(paddler_id):
    paddler = session.query(db.Paddler).get(paddler_id)
    return render_template("paddler.j2", paddler=paddler)
