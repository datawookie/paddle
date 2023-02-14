import tempfile
import csv
import logging
from werkzeug.utils import secure_filename
from flask_login import login_required
from flask_weasyprint import HTML, render_pdf

from .common import *
from .entry import load_entries, load_xlsx
from .util import *


@blueprint.route("/", methods=("GET", "POST"))
@login_required
def races():
    if request.method == "POST":
        # Create a list of race IDs from the checkbox fields.
        races = [key for key in request.form.keys() if re.match("race_id", key)]
        races = [int(re.sub("race_id_", "", id)) for id in races]
        races = [session.query(db.Race).get(id) for id in races]

        file = request.files.get("file")
        if file and allowed_file(file.filename):
            logging.debug(f"Entries file: {file.filename}")
            filename = secure_filename(file.filename)
            logging.debug(f"Entries file: {filename} (secure)")
            filename = os.path.join(UPLOAD_FOLDER, filename)
            logging.debug(f"Entries file: {filename} (upload path)")
            file.save(filename)

            entries = load_xlsx(filename)

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
@login_required
def race(race_id):
    entries = session.query(db.Entry).filter(db.Entry.race_id == race_id).all()
    race = session.query(db.Race).get(race_id)
    return render_template("race.j2", race=race, entries=entries)


@blueprint.route("/race/<race_id>/update", methods=("GET", "POST"))
@blueprint.route("/race/create", defaults={"race_id": None}, methods=("GET", "POST"))
def race_update(race_id):
    if race_id:
        race = race = session.query(db.Race).get(race_id)
    else:
        race = None

    if request.method == "POST":
        name = request.form.get("name")
        date = request.form.get("date")
        series_id = request.form.get("series")
        time_min_start = request.form.get("time_min_start")
        time_max_start = request.form.get("time_max_start")
        time_min_finish = request.form.get("time_min_finish")
        time_max_finish = request.form.get("time_max_finish")

        if name and not date:
            flash("Race date must be supplied.", "danger")
        elif date and not name:
            flash("Race name must be supplied.", "danger")
        elif not date and not name:
            flash("Race name and date must be supplied.", "danger")
        elif not time_min_start:
            flash("Minimum start time must be supplied.", "danger")
        elif not time_max_start:
            flash("Maximum start time must be supplied.", "danger")
        elif not time_min_finish:
            flash("Minimum finish time must be supplied.", "danger")
        elif not time_max_finish:
            flash("Maximum finish time must be supplied.", "danger")
        else:
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            series = session.query(db.Series).get(series_id)
            time_min_start = parse_time(time_pad_seconds(time_min_start))
            time_max_start = parse_time(time_pad_seconds(time_max_start))
            time_min_finish = parse_time(time_pad_seconds(time_min_finish))
            time_max_finish = parse_time(time_pad_seconds(time_max_finish))

            if race:
                # Update existing race.
                race.name = name
                race.date = date
                race.series = series

                flash("Updated existing race.", "success")
            else:
                # Create new race.
                race = db.Race(name=name, date=date, series_id=series.id)
                session.add(race)

            race.time_min_start = time_min_start
            race.time_max_start = time_max_start
            race.time_min_finish = time_min_finish
            race.time_max_finish = time_max_finish

            session.commit()

            return redirect(url_for("kanoe.races"))

    serieses = session.query(db.Series).order_by(db.Series.name.desc()).all()
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

    categories = db.entries_get_categories(results)

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


@blueprint.route("/race/<race_id>/results/capture", methods=("GET", "POST"))
@login_required
def race_results_capture(race_id):
    if request.method == "POST":
        entry_id = request.form["entry_id"]
        time_start = request.form["time_start"]
        time_finish = request.form["time_finish"]
        time_adjustment = request.form["time_adjustment"]
        note = request.form["note"]
        retired = request.form.get("retired", False)
        disqualified = request.form.get("disqualified", False)

        time_start = parse_time(time_start)
        time_finish = parse_time(time_finish)

        entry = session.query(db.Entry).get(entry_id)

        if time_start:
            entry.time_start = time_start
        if time_finish:
            entry.time_finish = time_finish
        if time_adjustment:
            entry.time_adjustment = time_adjustment
        if retired:
            entry.retired = True
        if disqualified:
            entry.disqualified = True
        if note:
            entry.note = note

        session.commit()

        flash("Captured result!", "success")

        return redirect(url_for("kanoe.race_results_capture", race_id=race_id))

    return render_template("race-results-capture.j2", race_id=race_id)


@blueprint.route("/race/<race_id>/results/validate")
@login_required
def race_results_validate(race_id):
    entries = session.query(db.Entry).filter(db.Entry.race_id == race_id).all()
    race = session.query(db.Race).get(race_id)
    return render_template(
        "race-results-validate.j2",
        race=race,
        entries=entries,
        time_between=time_between,
    )


@blueprint.route("/race/<race_id>/results/export/csv")
@login_required
def race_results_export_csv(race_id):
    race = session.query(db.Race).get(race_id)
    path = os.path.join(tempfile.mkdtemp(), race.slug + "-results.csv")

    results = (
        session.query(db.Entry)
        .filter(db.Entry.race_id == race_id)
        .filter(db.Entry.time_start != None)
        .filter(db.Entry.time_finish != None)
        .all()
    )

    categories = db.entries_get_categories(results)

    # Sort results in each category.
    for results in categories.values():
        results.sort(key=lambda x: x.time, reverse=False)

    with open(path, "w", newline="") as fid:
        spamwriter = csv.writer(fid, quoting=csv.QUOTE_NONNUMERIC)
        for results in categories.values():
            for position, result in enumerate(results):
                spamwriter.writerow(
                    [result.category, position + 1, str(result), result.time]
                )

    return send_file(path, as_attachment=True)


@blueprint.route("/race/<race_id>/results/paginated")
@login_required
def race_results_paginated(race_id):
    race = session.query(db.Race).get(race_id)

    results = (
        session.query(db.Entry)
        .filter(db.Entry.race_id == race_id)
        .filter(db.Entry.time_start != None)
        .filter(db.Entry.time_finish != None)
        .all()
    )

    categories = db.entries_get_categories(results)

    # Sort results in each category.
    for results in categories.values():
        results.sort(key=lambda x: x.time, reverse=False)

    return render_template(
        "race-results-paginated.j2",
        race=race,
        categories=categories,
        timestamp=datetime.datetime.now(),
    )


@blueprint.route("/race/<race_id>/results/export/pdf")
@login_required
def race_results_export_pdf(race_id):
    return render_pdf(url_for("kanoe.race_results_paginated", race_id=race_id))


@blueprint.route("/race/<race_id>/allocate-numbers", methods=("GET", "POST"))
@login_required
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
                number = session.query(db.Number).filter(db.Number.id == running).one()
                allocation = db.NumberAllocation(number_id=number.id, entry_id=entry.id)
                session.add(allocation)
                running += 1

            chunk += numbers - (1 if chunk == 1 else 0)

        session.commit()

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


@blueprint.route("/race/<race_id>/entries/export/csv")
@login_required
def race_entries_export_csv(race_id):
    race = session.query(db.Race).get(race_id)
    path = os.path.join(tempfile.mkdtemp(), race.slug + "-entries.csv")

    entries = session.query(db.Entry).filter(db.Entry.race_id == race_id).all()

    with open(path, "w", newline="") as fid:
        spamwriter = csv.writer(fid, quoting=csv.QUOTE_NONNUMERIC)
        for entry in entries:
            spamwriter.writerow([entry, entry.id])

    return send_file(path, as_attachment=True)


@blueprint.route("/race/<race_id>/entries/paginated")
@login_required
def race_entries_paginated(race_id):
    race = session.query(db.Race).get(race_id)

    entries = session.query(db.Entry).filter(db.Entry.race_id == race_id).all()

    categories = db.entries_get_categories(entries)
    # Sort by last name of first paddler in crew.
    for entries in categories.values():
        entries.sort(key=lambda x: x.crews[0].paddler.last, reverse=False)

    return render_template(
        "race-entries-paginated.j2",
        race=race,
        categories=categories,
        timestamp=datetime.datetime.now(),
    )


@blueprint.route("/race/<race_id>/entries/export/pdf")
@login_required
def race_entries_export_pdf(race_id):
    return render_pdf(url_for("kanoe.race_entries_paginated", race_id=race_id))
