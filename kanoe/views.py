import datetime
from flask import render_template, request, url_for, flash, redirect, jsonify

from . import app
import database as db

session = db.Session()


@app.route("/")
def index():
    return render_template("index.j2")


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


@app.route("/race/<race_id>/results/bulk", methods=("GET", "POST"))
def race_results_bulk(race_id):
    entries = session.query(db.Entry).filter(db.Entry.race_id == race_id).all()
    return render_template("race-results-bulk.j2", race_id=race_id, entries=entries)


@app.route("/update", methods=("GET", "POST"))
def update():
    if request.method == "POST":
        try:
            field = request.form["field"]
            value = request.form["value"]
            edit_id = request.form["edit_id"]

            entry = session.query(db.Entry).get(edit_id)

            if field == "start":
                entry.time_start = value
            if field == "finish":
                entry.time_finish = value

            session.commit()

            success = 1
        except:
            success = 0

        return jsonify(success)


@app.route("/entry/<entry_id>")
def entry(entry_id):
    entry = session.query(db.Entry).get(entry_id)
    return render_template("entry.j2", entry=entry)


@app.route("/seat/<seat_id>", methods=("GET", "POST"))
def entry_edit_seat(seat_id):
    seat = session.query(db.Seat).get(seat_id)
    paddlers = session.query(db.Paddler).order_by(db.Paddler.name).all()
    clubs = session.query(db.Club).all()

    if request.method == "POST":
        paddler_id = request.form["paddler"]
        club_id = request.form["club"]

        # seat.update({db.Seat.paddler_id: paddler_id})
        seat.paddler_id = paddler_id
        seat.club_id = club_id
        session.commit()

        flash("Updated seat.", "success")

        return redirect(url_for("entry", entry_id=seat.entry.id))

    return render_template(
        "entry-edit-seat.j2", seat=seat, paddlers=paddlers, clubs=clubs
    )


@app.route("/paddlers", methods=("GET", "POST"))
def paddlers():
    if request.method == "POST":
        first = request.form["first"]
        middle = request.form["middle"]
        last = request.form["last"]
        division = request.form["division"]
        dob = request.form["dob"]
        title = request.form["title"]
        emergency_name = request.form["emergency_name"]
        emergency_phone = request.form["emergency_phone"]

        if dob:
            dob = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
        else:
            dob = None

        if middle == "":
            middle = None
        if title == "":
            title = None

        if not first:
            flash("First name is required!", "danger")
        elif not last:
            flash("Last name is required!", "danger")
        elif not division:
            flash("Division is required!", "danger")
        else:
            paddler = db.Paddler(
                first=first,
                middle=middle,
                last=last,
                division=division,
                dob=dob,
                title=title,
                emergency_name=emergency_name,
                emergency_phone=emergency_phone,
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
