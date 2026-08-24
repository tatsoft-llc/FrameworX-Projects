#!/usr/bin/env python
"""
Generator for Highland_WTP_Equipment_Spec.pdf, the FICTIONAL equipment
specification that seeds the Example-HighlandWTP worked project.

Nothing in the produced document describes a real facility, a real firm, or a
real control system. The plant, the process values, the PLC address and both
organization names are invented for the example. The generated PDF carries that
statement on its own face, so the caveat travels with the file when it is
forwarded away from this repository.

Regenerate with:

    python -m pip install reportlab
    python Highland_WTP_Equipment_Spec.gen.py

Writes Highland_WTP_Equipment_Spec.pdf next to this file.
"""

import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

NAVY = colors.HexColor("#1F3864")
HEAD_BG = colors.HexColor("#1F3864")
ROW_ALT = colors.HexColor("#F2F5FA")
GRID = colors.HexColor("#C8D0DE")
STAMP_BG = colors.HexColor("#FFF4E5")
STAMP_LINE = colors.HexColor("#B26A00")

FICTION_NOTICE = "Fictional example. Not a real facility or a real firm."
PREPARED_FOR = "EXAMPLE WATER DISTRICT (fictional)"
PREPARED_BY = "EXAMPLE PROCESS ENGINEERING FIRM (fictional)"

_ss = getSampleStyleSheet()

S_TITLE = ParagraphStyle("t", parent=_ss["Title"], fontName="Helvetica-Bold",
                         fontSize=20, leading=24, textColor=NAVY, spaceAfter=2)
S_SUB = ParagraphStyle("s", parent=_ss["Normal"], fontSize=10.5, leading=14,
                       alignment=TA_CENTER, textColor=colors.HexColor("#333333"),
                       spaceAfter=10)
S_STAMP = ParagraphStyle("stamp", parent=_ss["Normal"], fontName="Helvetica-Bold",
                         fontSize=10.5, leading=14, alignment=TA_CENTER,
                         textColor=STAMP_LINE)
S_H1 = ParagraphStyle("h1", parent=_ss["Heading1"], fontName="Helvetica-Bold",
                      fontSize=14.5, leading=18, textColor=NAVY,
                      spaceBefore=16, spaceAfter=7)
S_H2 = ParagraphStyle("h2", parent=_ss["Heading2"], fontName="Helvetica-Bold",
                      fontSize=11.5, leading=15, textColor=NAVY,
                      spaceBefore=12, spaceAfter=5)
S_BODY = ParagraphStyle("b", parent=_ss["Normal"], fontSize=9.5, leading=13.5,
                        spaceAfter=6)
S_NOTE = ParagraphStyle("n", parent=S_BODY, fontName="Helvetica-Oblique",
                        fontSize=8.5, leading=11.5,
                        textColor=colors.HexColor("#444444"))
S_META = ParagraphStyle("m", parent=_ss["Normal"], fontSize=9.5, leading=13)
S_CELL = ParagraphStyle("c", parent=_ss["Normal"], fontSize=8.8, leading=11.5)
S_CELLH = ParagraphStyle("ch", parent=S_CELL, fontName="Helvetica-Bold",
                         textColor=colors.white)
S_END = ParagraphStyle("e", parent=_ss["Normal"], fontName="Helvetica-Oblique",
                       fontSize=9, alignment=TA_CENTER,
                       textColor=colors.HexColor("#666666"), spaceBefore=14)


def table(rows, widths):
    """Header row + body rows, rendered in the document's house style."""
    data = [[Paragraph(c, S_CELLH) for c in rows[0]]]
    data += [[Paragraph(c, S_CELL) for c in r] for r in rows[1:]]
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(2, len(data), 2):
        style.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle(style))
    return t


def stamp_block():
    """The fictional-example notice, boxed, on the face of page 1."""
    t = Table([[Paragraph(FICTION_NOTICE, S_STAMP)]], colWidths=[6.5 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), STAMP_BG),
        ("BOX", (0, 0), (-1, -1), 1.0, STAMP_LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def stamp_footer(canvas, doc):
    """Repeat the notice at the foot of every page, so no page stands alone."""
    canvas.saveState()
    canvas.setFont("Helvetica-Oblique", 7.5)
    canvas.setFillColor(STAMP_LINE)
    canvas.drawCentredString(letter[0] / 2.0, 0.45 * inch, FICTION_NOTICE)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#888888"))
    canvas.drawRightString(letter[0] - 0.9 * inch, 0.45 * inch,
                           "Page %d" % canvas.getPageNumber())
    canvas.restoreState()


def build(out_path):
    doc = SimpleDocTemplate(
        out_path, pagesize=letter,
        leftMargin=0.9 * inch, rightMargin=0.9 * inch,
        topMargin=0.8 * inch, bottomMargin=0.8 * inch,
        title="Highland Municipal Water Treatment Plant, Equipment Specification (fictional example)",
        author=PREPARED_BY,
        subject=FICTION_NOTICE,
    )
    f = []

    f.append(Paragraph("Highland Municipal Water Treatment Plant", S_TITLE))
    f.append(Paragraph("Equipment Specification &amp; Process Variables", S_SUB))
    f.append(stamp_block())
    f.append(Spacer(1, 10))
    f.append(HRFlowable(width="100%", thickness=1.6, color=NAVY,
                        spaceBefore=0, spaceAfter=10))

    meta = Table([
        [Paragraph("<b>Document:</b>", S_META), Paragraph("HMWTP-SPEC-2026-001", S_META),
         Paragraph("<b>Revision:</b>", S_META), Paragraph("C", S_META)],
        [Paragraph("<b>Date:</b>", S_META), Paragraph("January 15, 2026", S_META),
         Paragraph("", S_META), Paragraph("", S_META)],
        [Paragraph("<b>Prepared for:</b>", S_META), Paragraph(PREPARED_FOR, S_META),
         Paragraph("", S_META), Paragraph("", S_META)],
        [Paragraph("<b>Prepared by:</b>", S_META), Paragraph(PREPARED_BY, S_META),
         Paragraph("", S_META), Paragraph("", S_META)],
    ], colWidths=[1.05 * inch, 3.15 * inch, 0.85 * inch, 1.45 * inch])
    meta.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    f.append(meta)
    f.append(Spacer(1, 6))
    f.append(Paragraph(
        "This document is a worked training artifact for the FrameworX Solution Workspace. Both organization "
        "names above are placeholders, and the plant, its process values, its compliance figures and its "
        "controller address are invented. Do not cite it as a description of any real system.", S_NOTE))

    f.append(Paragraph("1. Plant Overview", S_H1))
    f.append(Paragraph(
        "Highland Municipal Water Treatment Plant is a conventional surface water treatment facility serving "
        "approximately 18,000 residents. The plant treats raw water from Highland Reservoir with a design "
        "capacity of 5 MGD (million gallons per day) and an average daily production of 3.2 MGD.", S_BODY))
    f.append(table([
        ["Area", "Name", "Description"],
        ["Area 100", "Raw Water Intake", "Reservoir intake structure with raw water pumping"],
        ["Area 200", "Chemical Feed", "Coagulant, chlorine, and fluoride chemical storage and dosing"],
        ["Area 500", "Filtration", "Four dual-media gravity filters with automated backwash"],
        ["Area 600", "Disinfection &amp; Clearwell", "Chlorine contact basin and 0.5 MG clearwell"],
    ], [0.95 * inch, 1.65 * inch, 4.0 * inch]))

    f.append(Paragraph("2. Control System Architecture", S_H1))
    f.append(Paragraph(
        "The treatment plant is controlled by an Allen-Bradley ControlLogix L83E processor in the main plant "
        "MCC room.", S_BODY))
    f.append(table([
        ["Parameter", "Value"],
        ["Processor", "1756-L83E CompactLogix"],
        ["IP Address", "192.168.1.10"],
        ["Slot", "0"],
        ["I/O Chassis", "1756-A13 (13-slot)"],
        ["Program File", "Highland_WTP_Main.L5K"],
    ], [2.1 * inch, 4.5 * inch]))
    f.append(Spacer(1, 6))
    f.append(Paragraph(
        "All treatment plant process variables are available as Controller Tags in the ControlLogix program. "
        "The attached L5K file contains the complete tag database.", S_BODY))

    f.append(Paragraph("3. Equipment List by Process Area", S_H1))

    f.append(Paragraph("Area 100: Raw Water Intake", S_H2))
    f.append(table([
        ["Tag", "Equipment", "Description"],
        ["P-101", "Raw Water Pump 1", "100 HP VFD centrifugal, 2500 GPM"],
        ["P-102", "Raw Water Pump 2", "100 HP VFD centrifugal, 2500 GPM (standby)"],
        ["FT-101", "Flow Transmitter", "Magnetic flow meter, raw water header"],
        ["AIT-101", "Turbidity Analyzer", "Raw water turbidity, Hach 1720E"],
        ["AIT-102", "pH Analyzer", "Raw water pH, Hach pHD sc"],
        ["LT-101", "Level Transmitter", "Intake wet well level"],
    ], [0.85 * inch, 1.95 * inch, 3.8 * inch]))

    f.append(Paragraph("Area 200: Chemical Feed", S_H2))
    f.append(table([
        ["Tag", "Equipment", "Description"],
        ["P-201", "Coagulant Pump", "Metering pump, aluminum sulfate (alum)"],
        ["P-202", "Pre-Chlorine Pump", "Metering pump, sodium hypochlorite"],
        ["P-203", "Fluoride Pump", "Metering pump, hydrofluosilicic acid"],
        ["LT-201", "Coagulant Tank Level", "2,500 gallon poly tank"],
        ["LT-202", "Hypochlorite Tank Level", "5,000 gallon poly tank"],
        ["LT-203", "Fluoride Tank Level", "1,500 gallon poly tank"],
    ], [0.85 * inch, 1.95 * inch, 3.8 * inch]))

    f.append(Paragraph("Area 500: Filtration", S_H2))
    f.append(Paragraph("Four identical dual-media (anthracite/sand) gravity filters:", S_BODY))
    f.append(table([
        ["Tag Pattern", "Description", "Type"],
        ["FILT{n}_HeadLoss", "Filter differential pressure", "Analog, 0-10 PSI"],
        ["FILT{n}_Turbidity", "Filtered effluent turbidity", "Analog, 0-5 NTU"],
        ["FILT{n}_InService", "Filter in-service status", "Digital"],
        ["FILT{n}_Backwashing", "Backwash in progress", "Digital"],
        ["FILT{n}_Valve", "Effluent valve position", "Analog, 0-100%"],
    ], [1.75 * inch, 2.85 * inch, 2.0 * inch]))
    f.append(Paragraph(
        "Where {n} = 1, 2, 3, 4. Backwash trigger: HeadLoss &gt; 8.0 PSI or operator-initiated. "
        "Cycle: ~15 min. Only one filter may backwash at a time.", S_NOTE))

    f.append(Paragraph("Area 600: Disinfection &amp; Clearwell", S_H2))
    f.append(table([
        ["Tag", "Equipment", "Description"],
        ["AIT-601", "Free Chlorine Analyzer", "Post-chlorination residual, Hach CL17sc"],
        ["AIT-602", "pH Analyzer", "Finished water pH, Hach pHD sc"],
        ["AIT-603", "Turbidity Analyzer", "Finished water turbidity, Hach TU5400sc"],
        ["LT-601", "Clearwell Level", "0.5 MG clearwell, ultrasonic level"],
    ], [0.85 * inch, 1.95 * inch, 3.8 * inch]))

    f.append(Paragraph("4. Water Quality Compliance Limits", S_H1))
    f.append(Paragraph(
        "Invented figures, written in the shape of a TCEQ / EPA Surface Water Treatment Rule limit table so "
        "the example exercises alarm rationalization. They are not regulatory values and must not be used as "
        "such.", S_BODY))
    f.append(table([
        ["Parameter", "Tag", "Warn Lo", "Warn Hi", "Crit Lo", "Crit Hi", "Unit"],
        ["Finished Water Turbidity", "AIT-603", "n/a", "0.3", "n/a", "1.0", "NTU"],
        ["Filter Turbidity (each)", "FILT{n}", "n/a", "0.15", "n/a", "0.5", "NTU"],
        ["Free Chlorine Residual", "AIT-601", "0.2", "3.5", "0.1", "4.0", "mg/L"],
        ["Finished Water pH", "AIT-602", "6.5", "8.5", "6.0", "9.0", "n/a"],
        ["Clearwell Level", "LT-601", "25%", "95%", "15%", "98%", "%"],
        ["Chemical Tank Levels", "LT-201,2,3", "15%", "n/a", "10%", "n/a", "%"],
    ], [1.75 * inch, 0.9 * inch, 0.72 * inch, 0.72 * inch, 0.72 * inch,
        0.72 * inch, 0.57 * inch]))

    f.append(Paragraph("5. Process Notes for SCADA Configuration", S_H1))
    for i, (n, txt) in enumerate([
        ("Chemical Dosing:", "Coagulant (alum) dose rate is flow-paced from FT-101. Pre-chlorination is "
                             "operator-adjusted. Fluoride is flow-paced with manual trim."),
        ("Filter Backwash:", "Only one filter may backwash at a time. Sequence takes ~15 minutes. Remaining "
                             "three filters handle full plant flow."),
        ("ML Opportunity:", "Filter headloss rate and post-sedimentation turbidity are early indicators of "
                            "raw water quality changes. Predictive monitoring could enable proactive "
                            "chemical dose adjustment."),
        ("Historian Requirements:", "All analog process variables historized with appropriate deadband. "
                                    "Digital status on-change. Minimum 1-year retention for regulatory "
                                    "compliance."),
    ]):
        f.append(Paragraph("%d. <b>%s</b> %s" % (i + 1, n, txt), S_BODY))

    f.append(Spacer(1, 8))
    f.append(HRFlowable(width="100%", thickness=0.7, color=GRID))
    f.append(Paragraph("End of Document. " + FICTION_NOTICE, S_END))

    doc.build(f, onFirstPage=stamp_footer, onLaterPages=stamp_footer)
    return out_path


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    print("wrote %s" % build(os.path.join(here, "Highland_WTP_Equipment_Spec.pdf")))
