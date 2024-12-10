import csv
import logging
import tempfile

from flask_weasyprint import render_pdf
from openpyxl import Workbook

from ...common import *


@blueprint.route("/race/<race_id>/entries/paginated")
@login_required
def race_entries_paginated(race_id):
    race = session.get(db.Race, race_id)

    entries = session.query(db.Entry).filter(db.Entry.race_id == race_id).all()

    categories = db.entries_get_categories(entries)
    clubs = db.entries_get_clubs(entries)

    # Sort by last name of first paddler in crew.
    for entries in categories.values():
        entries.sort(key=lambda x: x.crews[0].paddler.last, reverse=False)
    for entries in clubs.values():
        entries.sort(
            key=lambda x: str(x.team) + "|" + x.crews[0].paddler.last, reverse=False
        )

    return render_template(
        "race-entries-paginated.j2",
        race=race,
        categories=categories,
        clubs=clubs,
        timestamp=datetime.datetime.now(),
    )


@blueprint.route("/race/<race_id>/entries/export/pdf")
@login_required
def race_entries_export_pdf(race_id):
    race = session.get(db.Race, race_id)
    return render_pdf(
        url_for("paddle.race_entries_paginated", race_id=race_id),
        download_filename=race.slug + "-entries.pdf",
    )


@blueprint.route("/race/<race_id>/numbers/")
@login_required
def race_numbers(race_id):
    race = session.get(db.Race, race_id)

    # Get entries and link to race numbers.
    #
    entries = (
        session.query(db.Entry.id, db.NumberEntry.number_id, db.Category.label)
        .join(db.NumberEntry, db.Entry.id == db.NumberEntry.entry_id)
        .join(db.Category, db.Entry.category_id == db.Category.id)
        .filter(db.Entry.race_id == race.id)
        .subquery()
    )

    # Outer join with race numbers (so that we get all of them!).
    #
    entries = (
        session.query(entries, db.Number)
        .outerjoin(entries, entries.c.number_id == db.Number.id, full=True)
        .order_by(db.Number.id)
        .all()
    )

    assigned = {}
    unassigned = []
    missing = []

    for entry in entries:
        _, id, category, number = entry
        if entry[0] is None:
            if number.lost:
                missing.append(number.id)
            else:
                unassigned.append(number.id)
        else:
            try:
                assigned[category]
            except KeyError:
                assigned[category] = []

            assigned[category].append(id)

    return render_template(
        "race-numbers.j2",
        race=race,
        unassigned=unassigned,
        missing=missing,
        assigned=assigned,
    )


@blueprint.route("/race/<race_id>/numbers/export/pdf")
@login_required
def race_numbers_export_pdf(race_id):
    race = session.get(db.Race, race_id)
    return render_pdf(
        url_for("paddle.race_numbers", race_id=race_id),
        download_filename=race.slug + "-numbers.pdf",
    )


@blueprint.route("/race/<race_id>/entries/export/txt")
@login_required
def race_entries_export_txt(race_id):
    logging.debug("Exporting entries to TXT.")
    race = session.get(db.Race, race_id)
    path = os.path.join(tempfile.mkdtemp(), race.slug + "-entries.txt")

    entries = session.query(db.Entry).filter(db.Entry.race_id == race_id).all()

    logging.debug(f"Found {len(entries)} entries.")

    categories = db.entries_get_categories(entries)
    # Sort by last name of first paddler in crew.
    for entries in categories.values():
        entries.sort(key=lambda x: x.crews[0].paddler.last, reverse=False)

    with open(path, "wt") as fid:
        writer = csv.writer(fid)

        for entries in categories.values():
            for entry in entries:
                clubs = [
                    entry.crews[0].club.code if entry.crews[0].club else None,
                    (
                        entry.crews[1].club.code
                        if len(entry.crews) == 2 and entry.crews[1].club
                        else None
                    ),
                ]
                clubs = [club for club in clubs if club]
                clubs = "/".join(clubs)
                row = [
                    entry.crews[0].paddler.last,
                    entry.crews[0].paddler.first,
                    entry.crews[1].paddler.last if len(entry.crews) == 2 else None,
                    entry.crews[1].paddler.first if len(entry.crews) == 2 else None,
                    entry.category.id,
                    clubs,
                    int(entry.race_number) if entry.race_number else None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ]
                writer.writerow(row)

    return send_file(path, as_attachment=True)


@blueprint.route("/race/<race_id>/entries/export/xlsx")
@login_required
def race_entries_export_xlsx(race_id):
    race = session.get(db.Race, race_id)
    path = os.path.join(tempfile.mkdtemp(), race.slug + "-entries.xlsx")

    entries = session.query(db.Entry).filter(db.Entry.race_id == race_id).all()

    categories = db.entries_get_categories(entries)
    # Sort by last name of first paddler in crew.
    for entries in categories.values():
        entries.sort(key=lambda x: x.crews[0].paddler.last, reverse=False)

    workbook = Workbook()

    # grab the active worksheet
    sheet = workbook.active

    sheet.column_dimensions["A"].width = 5
    sheet.column_dimensions["B"].width = 20
    sheet.column_dimensions["C"].width = 5
    sheet.column_dimensions["D"].width = 20
    sheet.column_dimensions["E"].width = 20
    sheet.column_dimensions["F"].width = 5
    sheet.column_dimensions["G"].width = 20
    sheet.column_dimensions["H"].width = 20
    sheet.column_dimensions["I"].width = 5

    for entries in categories.values():
        for entry in entries:
            if entry.race_number:
                row = [
                    int(entry.race_number),
                    entry.category.label,
                    entry.category.id,
                    entry.crews[0].paddler.last,
                    entry.crews[0].paddler.first,
                    entry.crews[0].club.code if entry.crews[0].club else None,
                    entry.crews[1].paddler.last if len(entry.crews) == 2 else None,
                    entry.crews[1].paddler.first if len(entry.crews) == 2 else None,
                    (
                        entry.crews[1].club.code
                        if len(entry.crews) == 2 and entry.crews[1].club
                        else None
                    ),
                ]
                sheet.append(row)

    workbook.save(path)

    return send_file(path, as_attachment=True)
