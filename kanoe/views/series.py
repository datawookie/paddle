from flask_login import login_required
from flask_weasyprint import render_pdf

from .common import *


def series_results_team(series_id):
    series = session.get(db.Series, series_id)
    # Find past races in series.
    races = session.query(db.Race).filter(db.Race.series_id == series_id).all()
    races = [race for race in races if race.past]

    totals = {}
    #
    for team in session.query(db.Team).filter(db.Team.series_id == series_id).all():
        total = datetime.timedelta()
        #
        for race in races:
            crews = (
                session.query(db.Crew)
                .filter(db.Crew.team_id == team.id, db.Crew.entry.has(race_id=race.id))
                .all()
            )
            entries = set([crew.entry for crew in crews])
            entries = [entry for entry in entries if entry.team == team]
            # Get times for all entries.
            times = [entry.time for entry in entries if entry.time]
            # Keep only top 3 times.
            times = sorted(times)
            times = times[:3]
            # Don't qualify unless at least three finishers in each race.
            if len(times) == 3:
                total += sum(times, datetime.timedelta())
            else:
                total = None
                break

        if total:
            try:
                totals[team.type.label]
            except KeyError:
                totals[team.type.label] = {}

            totals[team.type.label][team] = total

    # Sort teams within type.
    #
    for type, teams in totals.items():
        totals[type] = sorted(teams.items(), key=lambda team: team[1])

    return series, totals


def series_results_category(series_id):
    series = session.get(db.Series, series_id)
    # Find past races in series.
    races = session.query(db.Race.id).filter(db.Race.series_id == series_id)
    # Find entries for races in series.
    entries = session.query(db.Entry)
    entries = (
        entries.filter(db.Entry.race_id.in_(races))
        .filter(db.Entry.time_start.is_not(None))
        .filter(db.Entry.time_finish.is_not(None))
    )
    entries = entries.all()

    races = session.query(db.Race).filter(db.Race.series_id == series_id).all()
    races_past = len([race for race in races if race.past])

    # Break down into categories.
    #
    categories = db.entries_get_categories(entries)

    # Within each category group entries using paddler hash.
    #
    # The resulting data structure is:
    #
    # - dictionary of categories
    #   - dictionary of crews
    #       - list of entries
    #
    for category, entries in categories.items():
        crews = {}
        for entry in entries:
            try:
                crews[entry.crew_hash].append(entry)
            except KeyError:
                crews[entry.crew_hash] = [entry]

        # Keep only crews who have finished all races in series.
        crews = [entries for entries in crews.values() if len(entries) == races_past]

        crews = [db.EntrySet(entries) for entries in crews]
        crews = sorted(crews, key=lambda x: x.time)

        categories[category] = crews

    return series, categories


def series_results_services(series_id):
    series = session.get(db.Series, series_id)
    # Find past races in series.
    races = session.query(db.Race.id).filter(db.Race.series_id == series_id)
    # Find entries for races in series.
    entries = session.query(db.Entry)
    entries = (
        entries.filter(db.Entry.race_id.in_(races))
        .filter(db.Entry.time_start.is_not(None))
        .filter(db.Entry.time_finish.is_not(None))
        .filter(db.Entry.time_finish.is_not(None))
    )
    entries = entries.all()

    races = session.query(db.Race).filter(db.Race.series_id == series_id).all()
    races_past = len([race for race in races if race.past])

    # Keep only services entries.
    entries = [entry for entry in entries if entry.services]

    crews = {}
    for entry in entries:
        try:
            crews[entry.crew_hash].append(entry)
        except KeyError:
            crews[entry.crew_hash] = [entry]

    # Keep only crews who have finished all races in series.
    crews = [entries for entries in crews.values() if len(entries) == races_past]

    crews = [db.EntrySet(entries) for entries in crews]
    crews = sorted(crews, key=lambda x: x.time)

    return series, crews


@blueprint.route("/series/<series_id>")
@login_required
def series(series_id):
    series, categories = series_results_category(series_id)
    _, types = series_results_team(series_id)
    _, services = series_results_services(series_id)

    return render_template(
        "series.j2",
        series=series,
        categories=categories,
        types=types,
        services=services,
    )


@blueprint.route("/series/<series_id>/results/paginated")
@login_required
def series_results_paginated(series_id):
    series, categories = series_results_category(series_id)
    _, types = series_results_team(series_id)
    _, services = series_results_services(series_id)

    return render_template(
        "series-results-paginated.j2",
        series=series,
        categories=categories,
        types=types,
        services=services,
        timestamp=datetime.datetime.now(),
    )


@blueprint.route("/series/<series_id>/results/export/pdf")
@login_required
def series_results_export_pdf(series_id):
    series = session.get(db.Series, series_id)
    return render_pdf(
        url_for("kanoe.series_results_paginated", series_id=series_id),
        download_filename=series.slug + "-results.pdf",
    )


@blueprint.route("/series/create", methods=("GET", "POST"))
@login_required
def series_create():
    if request.method == "POST":
        name = request.form.get("name")

        series = db.Series(name=name)
        session.add(series)
        session.commit()

        return redirect(url_for("kanoe.races"))

    return render_template("series-create.j2")
