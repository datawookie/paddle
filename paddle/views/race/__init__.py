import logging

from ...config import __version__
from ..common import *
from ..entry import load_entries, load_xlsx
from ..util import *
from .entries import *
from .results import *


@blueprint.route("/", methods=("GET", "POST"))
@login_required
def races():
    # Count number of entries per race.
    entries = (
        session.query(
            db.Entry.race_id,
            func.count(db.Entry.id.distinct()).label("count_entry"),
            func.count(db.Crew.id.distinct()).label("count_paddler"),
        )
        .join(db.Crew, db.Entry.id == db.Crew.entry_id)
        .group_by(db.Entry.race_id)
        .subquery()
    )
    # Merge counts into races.
    races = (
        session.query(
            db.Race,
            entries.c.count_entry,
            entries.c.count_paddler,
        )
        .outerjoin(entries, entries.c.race_id == db.Race.id)
        .all()
    )
    # Inject counts into Race objects.
    for race, count_entry, count_paddler in races:
        race.count_entries = count_entry if count_entry else 0
        race.count_paddlers = count_paddler if count_paddler else 0

    # Unzip the list, extracting races and counts separately (Race objects already contain counts).
    if races:
        races, _, _ = zip(*races)

    serieses = session.query(db.Series).all()

    return render_template(
        "races.j2", races=races, serieses=serieses, version=__version__
    )


@blueprint.route("/race/<race_id>")
@login_required
def race(race_id):
    entries = session.query(db.Entry).filter(db.Entry.race_id == race_id).all()
    race = session.get(db.Race, race_id)
    return render_template("race.j2", race=race, entries=entries)


@blueprint.route("/race/<race_id>/update", methods=("GET", "POST"))
@blueprint.route("/race/create", defaults={"race_id": None}, methods=("GET", "POST"))
def race_update(race_id):
    if race_id:
        race = session.get(db.Race, race_id)
    else:
        race = None

    if request.method == "POST":
        name = request.form.get("name")
        date = request.form.get("date")
        series_id = request.form.get("series_id")
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
            series = session.get(db.Series, series_id)
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
                race = db.Race(name=name, date=date)
                session.add(race)

            if series:
                race.series_id = series.id

            race.time_min_start = time_min_start
            race.time_max_start = time_max_start
            race.time_min_finish = time_min_finish
            race.time_max_finish = time_max_finish

            session.commit()

            return redirect(url_for("kanoe.races"))

    serieses = session.query(db.Series).order_by(db.Series.name.desc()).all()
    return render_template("race-update.j2", race=race, serieses=serieses)


@blueprint.route("/race/<race_id>/allocate-numbers", methods=("GET", "POST"))
@login_required
def race_allocate_numbers(race_id):
    if request.method == "POST":
        chunk = 0

        for category_id, allocated in request.form.items():
            category_id = int(category_id.replace("category_id_", ""))
            allocated = int(allocated)

            logging.debug(f"* Allocating numbers for category ID = {category_id}.")
            entries = (
                session.query(db.Entry)
                .filter(db.Entry.race_id == race_id)
                .filter(db.Entry.category_id == category_id)
                .all()
            )
            logging.debug(f"- Found {len(entries)} entries.")

            number = chunk
            #
            for entry in entries:
                #
                # Find next number that is
                #
                # - greater than previously allocated number and
                # - not missing!
                #
                (number,) = (
                    session.query(db.Number.id)
                    .filter(db.Number.id > number)
                    .filter(db.or_(~db.Number.lost, db.Number.lost == None))
                    .order_by(db.Number.id)
                    .first()
                )
                logging.debug(f"Allocate race number {number} to {entry}.")
                # Check for existing allocation.
                try:
                    allocation = (
                        session.query(db.NumberEntry)
                        .filter(db.NumberEntry.entry_id == entry.id)
                        .one()
                    )
                    logging.debug(
                        f"- Entry already has an assigned number: {allocation.number_id}."
                    )
                    allocation.number_id = number
                except db.NoResultFound:
                    allocation = db.NumberEntry(number_id=number, entry_id=entry.id)

                session.add(allocation)

            chunk += allocated - (1 if chunk == 0 else 0)

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

    missing = session.query(db.Number.id).filter(db.Number.lost).all()
    missing = [id for (id,) in missing]

    return render_template(
        "race-allocate-numbers.j2",
        race_id=race_id,
        categories=categories,
        missing=missing,
    )
