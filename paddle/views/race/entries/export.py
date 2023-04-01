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
    race = session.get(db.Race, race_id)
    return render_pdf(
        url_for("kanoe.race_entries_paginated", race_id=race_id),
        download_filename=race.slug + "-entries.pdf",
    )


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
                    entry.crews[1].club.code
                    if len(entry.crews) == 2 and entry.crews[1].club
                    else None,
                ]
                sheet.append(row)

    workbook.save(path)

    return send_file(path, as_attachment=True)
