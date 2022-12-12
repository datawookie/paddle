from werkzeug.utils import secure_filename

from .common import *
from .entry import load_entries
from .util import *


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


@blueprint.route("/race/<race_id>/results/capture", methods=("GET", "POST"))
def race_results_capture(race_id):
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

        return redirect(url_for("kanoe.race_results_capture", race_id=race_id))

    return render_template("race-results-capture.j2", race_id=race_id)


@blueprint.route("/race/<race_id>/results/validate")
def race_results_validate(race_id):
    entries = session.query(db.Entry).filter(db.Entry.race_id == race_id).all()
    race = session.query(db.Race).get(race_id)
    return render_template(
        "race-results-validate.j2",
        race=race,
        entries=entries,
        time_between=time_between,
    )


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
