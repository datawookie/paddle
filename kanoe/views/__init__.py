import os
import json
import datetime
import re
import logging
from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    flash,
    redirect,
    jsonify,
    abort,
)
from werkzeug.utils import secure_filename
from sqlalchemy.sql import func

import database as db
from database.database import announcement
from .util import *
from .entry import load_entries

session = db.Session()

blueprint = Blueprint("kanoe", __name__, url_prefix="/")


@blueprint.route("/")
def index():
    return render_template("index.j2")


@blueprint.route("/clubs")
def clubs():
    clubs = session.query(db.Club).all()
    return render_template("clubs.j2", clubs=clubs)


@blueprint.route("/club/<club_id>")
def club(club_id):
    club = session.query(db.Club).get(club_id)
    return render_template("club.j2", club=club)


@blueprint.route("/time-trial")
def time_trial():
    members = session.query(db.Member).all()
    return render_template("time-trial.j2", members=members)


@blueprint.route("/member/<member_id>")
def member(member_id):
    member = session.query(db.Member).get(member_id)
    return render_template("member.j2", member=member)


UPLOAD_FOLDER = "/tmp"


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"json"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@blueprint.route("/series/create", methods=("GET", "POST"))
def series_create():
    if request.method == "POST":
        name = request.form.get("name")

        series = db.Series(name=name)
        session.add(series)
        session.commit()

        return redirect(url_for("kanoe.races"))

    return render_template("series-create.j2")


@blueprint.route("/races", methods=("GET", "POST"))
def races():
    if request.method == "POST":
        # Create a list of race IDs from the checkbox fields.
        races = [key for key in request.form.keys() if re.match("race_id", key)]
        races = [int(re.sub("race_id_", "", id)) for id in races]
        races = [session.query(db.Race).get(id) for id in races]

        file = request.files.get("file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filename)

            with open(filename, "rt") as file:
                entries = file.read()
                entries = json.loads(entries)

            for race in races:
                load_entries(race, entries)

        return redirect(url_for("kanoe.races"))

    # Count number of entries per race.
    entries = (
        session.query(db.Entry.race_id, func.count(db.Entry.race_id).label("count"))
        .group_by(db.Entry.race_id)
        .subquery()
    )
    # Merge counts into races.
    races = (
        session.query(db.Race, entries.c.count)
        .outerjoin(entries, entries.c.race_id == db.Race.id)
        .all()
    )
    # Inject counts into Race objects.
    for race, count in races:
        race.count = count if count else 0

    # Unzip the list, extracting races and counts separately (Race objects already contain counts).
    if races:
        races, _ = zip(*races)

    serieses = session.query(db.Series).all()

    return render_template("races.j2", races=races, serieses=serieses)


@blueprint.route("/race/<race_id>")
def race(race_id):
    entries = session.query(db.Entry).filter(db.Entry.race_id == race_id).all()
    race = session.query(db.Race).get(race_id)
    return render_template("race.j2", race=race, entries=entries)


@blueprint.route("/race/create", methods=("GET", "POST"))
def race_create():
    if request.method == "POST":
        name = request.form.get("name")
        date = request.form.get("date")
        series_id = request.form.get("series")

        if name and not date:
            flash("Race date must be supplied.", "danger")
        elif date and not name:
            flash("Race name must be supplied.", "danger")
        elif not date and not name:
            flash("Race name and date must be supplied.", "danger")
        else:
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            series = session.query(db.Series).get(series_id)
            race = db.Race(name=name, date=date, series_id=series.id)
            session.add(race)
            session.commit()

            return redirect(url_for("kanoe.races"))

    serieses = session.query(db.Series).order_by(db.Series.name.desc()).all()
    return render_template("race-create.j2", serieses=serieses)


@blueprint.route("/race/<race_id>/update", methods=("GET", "POST"))
def race_update(race_id):
    if request.method == "POST":
        time_min_start = request.form.get("time_min_start")
        time_max_start = request.form.get("time_max_start")
        time_min_finish = request.form.get("time_min_finish")
        time_max_finish = request.form.get("time_max_finish")

        race = session.query(db.Race).get(race_id)

        if not time_min_start:
            flash("Minimum start time must be supplied.", "danger")
        else:
            time_min_start = parse_time(time_pad_seconds(time_min_start))
            race.time_min_start = time_min_start

        if not time_max_start:
            flash("Maximum start time must be supplied.", "danger")
        else:
            time_max_start = parse_time(time_pad_seconds(time_max_start))
            race.time_max_start = time_max_start

        if not time_min_finish:
            flash("Minimum finish time must be supplied.", "danger")
        else:
            time_min_finish = parse_time(time_pad_seconds(time_min_finish))
            race.time_min_finish = time_min_finish

        if not time_max_finish:
            flash("Maximum finish time must be supplied.", "danger")
        else:
            time_max_finish = parse_time(time_pad_seconds(time_max_finish))
            race.time_max_finish = time_max_finish

        session.add(race)
        session.commit()

    serieses = session.query(db.Series).order_by(db.Series.name.desc()).all()
    race = session.query(db.Race).get(race_id)
    return render_template("race-update.j2", race=race, serieses=serieses)


@blueprint.route("/race/<race_id>/results/display")
def race_results_display(race_id):
    race = session.query(db.Race).get(race_id)
    results = (
        session.query(db.Entry)
        .filter(db.Entry.race_id == race_id)
        .filter(db.Entry.time_start != None)
        .filter(db.Entry.time_finish != None)
        .all()
    )

    categories = {}
    #
    # Group results into categories.
    #
    for result in results:
        try:
            categories[result.category.label]
        except KeyError:
            categories[result.category.label] = []

        categories[result.category.label].append(result)

    # Sort results in each category.
    for results in categories.values():
        results.sort(key=lambda x: x.time, reverse=False)

    announcements = session.query(db.Announcement).filter(db.Announcement.enabled).all()

    return render_template(
        "race-results-display.j2",
        race=race,
        categories=categories,
        announcements=announcements,
    )


@blueprint.route("/race/<race_id>/results/quick", methods=("GET", "POST"))
def race_results_quick(race_id):
    if request.method == "POST":
        entry_id = request.form["entry_id"]
        time_start = request.form["time_start"]
        time_finish = request.form["time_finish"]
        retired = request.form.get("retired", False)
        disqualified = request.form.get("disqualified", False)

        time_start = parse_time(time_start)
        time_finish = parse_time(time_finish)

        entry = session.query(db.Entry).get(entry_id)

        if time_start:
            entry.time_start = time_start
        if time_finish:
            entry.time_finish = time_finish
        if retired:
            entry.retired = True
        if disqualified:
            entry.disqualified = True

        session.commit()

        flash("Captured result!", "success")

        return redirect(url_for("kanoe.race_results_quick", race_id=race_id))

    return render_template("race-results-quick.j2", race_id=race_id)


@blueprint.route("/race/<race_id>/results/validate")
def race_results_validate(race_id):
    entries = session.query(db.Entry).filter(db.Entry.race_id == race_id).all()
    race = session.query(db.Race).get(race_id)
    return render_template("race-results-validate.j2", race=race, entries=entries)


@blueprint.route("/race/<race_id>/allocate-numbers", methods=("GET", "POST"))
def race_allocate_numbers(race_id):
    if request.method == "POST":
        chunk = 1

        for category_id, numbers in request.form.items():
            category_id = int(category_id.replace("category_id_", ""))
            numbers = int(numbers)

            logging.debug(f"Allocating numbers for category ID = {category_id}.")
            entries = (
                session.query(db.Entry)
                .filter(db.Entry.race_id == race_id)
                .filter(db.Entry.category_id == category_id)
                .all()
            )
            logging.debug(f"Found {len(entries)} entries.")

            running = chunk
            #
            for entry in entries:
                logging.debug(f"Allocating race number {running} to {entry}.")
                entry.number_id = running
                running += 1

            chunk += numbers - (1 if chunk == 1 else 0)

        return redirect(url_for("kanoe.races"))

    # Count number of entries per race.
    entries = (
        session.query(db.Entry.category_id, func.count(db.Entry.id).label("count"))
        .filter(db.Entry.race_id == race_id)
        .group_by(db.Entry.category_id)
        .subquery()
    )
    # Merge counts into races.
    categories = (
        session.query(db.Category, entries.c.count)
        .outerjoin(entries, entries.c.category_id == db.Category.id)
        .all()
    )
    # Inject counts into Category objects.
    for category, count in categories:
        category.count = count if count else 0

    # Unzip the list, extracting categories and counts separately.
    if categories:
        categories, _ = zip(*categories)

    # Drop empty categories.
    #
    categories = [category for category in categories if category.count > 0]

    return render_template(
        "race-allocate-numbers.j2", race_id=race_id, categories=categories
    )


@blueprint.route("/api/get-entry", methods=("GET", "POST"))
def get_entry():
    if request.method == "POST":
        race_id = request.form["race_id"]
        # Get race number.
        race_number = request.form["race_number"]
        try:
            race_number = (
                session.query(db.Number)
                .filter(
                    db.Number.id == race_number,
                )
                .one()
            )
        except db.NoResultFound:
            logging.warning(f"Race number {race_number} not found.")
            abort(404)
        # Get corresponding entry.
        entry = (
            session.query(db.Entry)
            .filter(
                db.Entry.race_id == race_id,
                db.Entry.race_number == race_number,
            )
            .one()
        )
        data = {
            "entry_id": entry.id,
            "paddlers": str(entry),
            "time_start": entry.time_start,
            "time_finish": entry.time_finish,
        }
        return jsonify(data)


@blueprint.route("/api/update", methods=("GET", "POST"))
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


@blueprint.route("/entry/<entry_id>")
def entry(entry_id):
    entry = session.query(db.Entry).get(entry_id)
    return render_template("entry.j2", entry=entry)


@blueprint.route("/seat/<seat_id>", methods=("GET", "POST"))
def seat(seat_id):
    seat = session.query(db.Seat).get(seat_id)

    if request.method == "POST":
        paddler_id = request.form["paddler"]
        club_id = request.form["club"]
        team_id = request.form.get("team")
        services = request.form.get("services", None)

        seat.paddler_id = paddler_id
        seat.club_id = club_id
        if team_id:
            seat.team_id = team_id
        if services:
            seat.services = True
        else:
            seat.services = False
        session.commit()

        flash("Updated seat.", "success")

        return redirect(url_for("kanoe.entry", entry_id=seat.entry.id))

    paddlers = session.query(db.Paddler).order_by(db.Paddler.name).all()
    clubs = session.query(db.Club).all()
    teams = session.query(db.Team).all()
    return render_template(
        "seat.j2", seat=seat, paddlers=paddlers, clubs=clubs, teams=teams
    )


@blueprint.route("/paddlers", methods=("GET", "POST"))
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

            return redirect(url_for("kanoe.paddlers"))

    paddlers = session.query(db.Paddler).all()
    return render_template("paddlers.j2", paddlers=paddlers)


@blueprint.route("/paddler/<paddler_id>")
def paddler(paddler_id):
    paddler = session.query(db.Paddler).get(paddler_id)
    return render_template("paddler.j2", paddler=paddler)


@blueprint.route("/teams", methods=("GET", "POST"))
def teams():
    if request.method == "POST":
        name = request.form["name"]

        team = db.Team(name=name)
        session.add(team)
        session.commit()

        return redirect(url_for("kanoe.teams"))

    teams = session.query(db.Team).all()
    return render_template("teams.j2", teams=teams)
