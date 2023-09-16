# Standard Library
import csv
import logging
import re
import tempfile

from flask_weasyprint import render_pdf
from openpyxl import Workbook
from openpyxl.styles import Font

from ...common import *


@blueprint.route("/race/<race_id>/results/export/csv")
@login_required
def race_results_export_csv(race_id):
    race = session.get(db.Race, race_id)
    path = os.path.join(tempfile.mkdtemp(), race.slug + "-results.csv")

    results = (
        session.query(db.Entry)
        .filter(db.Entry.race_id == race_id)
        .filter(db.Entry.time_start.is_not(None))
        .filter(db.Entry.time_finish.is_not(None))
        .all()
    )

    categories = db.entries_get_categories(results)

    # Sort results in each category.
    for results in categories.values():
        results.sort(key=lambda x: x.time, reverse=False)

    with open(path, "w", newline="") as fid:
        writer = csv.writer(fid, quoting=csv.QUOTE_NONNUMERIC)
        for results in categories.values():
            for position, result in enumerate(results):
                writer.writerow(
                    [result.category, position + 1, str(result), result.time]
                )

    return send_file(path, as_attachment=True)


@blueprint.route("/race/<race_id>/results/export/pdf")
@login_required
def race_results_export_pdf(race_id):
    race = session.get(db.Race, race_id)
    return render_pdf(
        url_for("kanoe.race_results_paginated", race_id=race_id),
        download_filename=race.slug + "-results.pdf",
    )


@blueprint.route("/race/<race_id>/results/export/xlsx")
@login_required
def race_results_export_xlsx(race_id):
    logging.info("Export XLSX results.")
    race = session.get(db.Race, race_id)
    path = os.path.join(tempfile.mkdtemp(), race.slug + "-results.xlsx")

    results = (
        session.query(db.Entry)
        .filter(db.Entry.race_id == race_id)
        .filter(db.Entry.time_start.is_not(None))
        .filter(db.Entry.time_finish.is_not(None))
        .all()
    )

    categories = db.entries_get_categories(results)

    # Sort results in each category.
    for results in categories.values():
        results.sort(key=lambda x: x.time, reverse=False)

    workbook = Workbook()
    font_data = Font(
        name="Arial",
        size=10,
    )
    font_head = Font(
        name="Courier New",
        size=13,
    )

    # Delete default sheet.
    workbook.remove_sheet(workbook.get_sheet_by_name("Sheet"))

    for category, results in categories.items():
        # Create sheet for category.
        category = re.sub(" +", "-", category)
        category = re.sub("/", "+", category)
        sheet = workbook.create_sheet(category)

        # Set column widths.
        sheet.column_dimensions["A"].width = 10  # Number
        sheet.column_dimensions["B"].width = 20  # Surname
        sheet.column_dimensions["C"].width = 20  # First name
        sheet.column_dimensions["D"].width = 10  # BCU number
        sheet.column_dimensions["E"].width = 10  # Expiry
        sheet.column_dimensions["F"].width = 25  # Club
        sheet.column_dimensions["G"].width = 10  # Class
        sheet.column_dimensions["H"].width = 10  # Div
        sheet.column_dimensions["I"].width = 10  # Due
        sheet.column_dimensions["J"].width = 10  # Paid
        sheet.column_dimensions["K"].width = 15  # Start
        sheet.column_dimensions["L"].width = 15  # Finish
        sheet.column_dimensions["M"].width = 15  # Elapsed
        sheet.column_dimensions["N"].width = 10  # Position
        sheet.column_dimensions["O"].width = 10  # Points
        sheet.column_dimensions["P"].width = 5  # P/D

        # Add header records.
        head = [
            "Number",
            "Surname",
            "First name",
            "BC Number",
            "Expiry",
            "Club",
            "Class",
            "Div",
            "Due",
            "Paid",
            "Start",
            "Finish",
            "Elapsed",
            "Position",
            "Points",
            "P/D",
        ]
        sheet.append(head)

        # Add results.
        for position, result in enumerate(results):
            print(dir(result))
            for crew in result.crews:
                print(crew.paddler.age_group)
                row = [
                    int(result.race_number),
                    crew.paddler.last,
                    crew.paddler.first,
                    crew.paddler.bcu,
                    crew.paddler.bcu_expiry.strftime("%d/%m/%Y")
                    if crew.paddler.bcu_expiry
                    else None,
                    crew.club.code if crew.club else None,
                    None,
                    crew.paddler.division,
                    None,
                    None,
                    result.time_start,
                    result.time_finish,
                    result.time,
                    position + 1,
                    None,
                    None,
                ]
                sheet.append(row)

        for cells in sheet.iter_rows(
            min_row=0, max_row=sheet.max_row, min_col=1, max_col=sheet.max_column
        ):
            for cell in cells:
                cell.font = font_head if cell.row == 1 else font_data

    workbook.save(path)

    return send_file(path, as_attachment=True)
