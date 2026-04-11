"""
PredictIQ Export Service
Generates PDF reports for estimates using ReportLab.
"""
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import structlog

logger = structlog.get_logger()

# Brand colors
BRAND_BLUE = colors.HexColor("#1A56DB")
BRAND_DARK = colors.HexColor("#0F172A")
BRAND_GRAY = colors.HexColor("#64748B")
BRAND_GREEN = colors.HexColor("#10B981")
BRAND_AMBER = colors.HexColor("#F59E0B")
BRAND_RED = colors.HexColor("#EF4444")
LIGHT_BG = colors.HexColor("#F8FAFC")


def generate_pdf_report(estimate: dict) -> bytes:
    """
    Generate a branded PDF report for an estimate.

    Args:
        estimate: Full estimate result dictionary.

    Returns:
        PDF file content as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=24,
        textColor=BRAND_DARK,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=BRAND_GRAY,
        spaceAfter=20,
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=BRAND_BLUE,
        spaceBefore=20,
        spaceAfter=10,
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=10,
        textColor=BRAND_DARK,
        leading=14,
    )
    metric_label = ParagraphStyle(
        "MetricLabel",
        parent=styles["Normal"],
        fontSize=9,
        textColor=BRAND_GRAY,
    )
    metric_value = ParagraphStyle(
        "MetricValue",
        parent=styles["Normal"],
        fontSize=18,
        textColor=BRAND_DARK,
    )

    elements = []
    inputs = estimate.get("inputs", {})
    outputs = estimate.get("outputs", {})

    # ── Header ──────────────────────────────────────────────
    elements.append(Paragraph("PredictIQ", title_style))
    elements.append(Paragraph(
        f"Cost Estimation Report — {estimate.get('project_name', 'Project')}",
        subtitle_style,
    ))
    elements.append(HRFlowable(
        width="100%", thickness=2, color=BRAND_BLUE, spaceAfter=20
    ))

    # Meta info
    meta_data = [
        ["Generated:", datetime.now().strftime("%B %d, %Y at %I:%M %p")],
        ["Project Type:", inputs.get("project_type", "N/A")],
        ["Complexity:", inputs.get("complexity", "N/A")],
        ["Methodology:", inputs.get("methodology", "N/A")],
        ["Team Size:", str(inputs.get("team_size", "N/A"))],
        ["Duration:", f"{inputs.get('duration_months', 'N/A')} months"],
        ["Hourly Rate:", f"${inputs.get('hourly_rate_usd', 75)}/hr"],
    ]
    meta_table = Table(meta_data, colWidths=[3 * cm, 12 * cm])
    meta_table.setStyle(TableStyle([
        ("TEXTCOLOR", (0, 0), (0, -1), BRAND_GRAY),
        ("TEXTCOLOR", (1, 0), (1, -1), BRAND_DARK),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 20))

    # ── Cost Summary ────────────────────────────────────────
    elements.append(Paragraph("Cost Summary", heading_style))

    cost_data = [
        ["", "Optimistic", "Most Likely", "Conservative"],
        [
            "Cost (USD)",
            f"${outputs.get('cost_min_usd', 0):,.0f}",
            f"${outputs.get('cost_likely_usd', 0):,.0f}",
            f"${outputs.get('cost_max_usd', 0):,.0f}",
        ],
        [
            "Effort (hrs)",
            f"{outputs.get('effort_min_hours', 0):,.0f}",
            f"{outputs.get('effort_likely_hours', 0):,.0f}",
            f"{outputs.get('effort_max_hours', 0):,.0f}",
        ],
        [
            "Timeline (wks)",
            f"{outputs.get('timeline_min_weeks', 0):.1f}",
            f"{outputs.get('timeline_likely_weeks', 0):.1f}",
            f"{outputs.get('timeline_max_weeks', 0):.1f}",
        ],
    ]

    cost_table = Table(cost_data, colWidths=[3.5 * cm, 4 * cm, 4 * cm, 4 * cm])
    cost_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 1), (-1, -1), LIGHT_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(cost_table)
    elements.append(Spacer(1, 10))

    conf_pct = outputs.get("confidence_pct", 0)
    elements.append(Paragraph(
        f"<b>Confidence:</b> {conf_pct:.0f}% | "
        f"<b>Risk Score:</b> {outputs.get('risk_score', 0):.0f}/100 "
        f"({outputs.get('risk_level', 'N/A')})",
        body_style,
    ))

    # ── Phase Breakdown ─────────────────────────────────────
    elements.append(Paragraph("Phase Breakdown", heading_style))

    phase_header = ["Phase", "Effort (hrs)", "Cost (USD)", "Duration (wks)", "% of Total"]
    phase_rows = [phase_header]
    for phase in outputs.get("phase_breakdown", []):
        phase_rows.append([
            phase.get("phase", ""),
            f"{phase.get('effort_hours', 0):,.0f}",
            f"${phase.get('cost_usd', 0):,.0f}",
            f"{phase.get('duration_weeks', 0):.1f}",
            f"{phase.get('pct_of_total', 0):.0f}%",
        ])

    phase_table = Table(phase_rows, colWidths=[5 * cm, 2.5 * cm, 3 * cm, 2.5 * cm, 2.5 * cm])
    phase_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(phase_table)

    # ── Risk Analysis ───────────────────────────────────────
    elements.append(Paragraph("Risk Analysis", heading_style))

    for risk in outputs.get("top_risks", []):
        severity = risk.get("severity", "Low")
        sev_color = {
            "Critical": "red",
            "High": "#F59E0B",
            "Medium": "#3B82F6",
            "Low": "#10B981",
        }.get(severity, "gray")

        elements.append(Paragraph(
            f'<font color="{sev_color}">●</font> '
            f'<b>{risk.get("name", "")}</b> ({severity}): '
            f'{risk.get("description", "")}',
            body_style,
        ))
        elements.append(Spacer(1, 4))

    # ── Benchmark & Insights ────────────────────────────────
    if outputs.get("benchmark_comparison"):
        elements.append(Paragraph("Benchmark Comparison", heading_style))
        elements.append(Paragraph(outputs["benchmark_comparison"], body_style))

    if outputs.get("model_explanation"):
        elements.append(Paragraph("AI Model Insights", heading_style))
        elements.append(Paragraph(outputs["model_explanation"], body_style))

    # ── Footer ──────────────────────────────────────────────
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=1, color=BRAND_GRAY))
    elements.append(Spacer(1, 6))
    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"],
        fontSize=8, textColor=BRAND_GRAY, alignment=TA_CENTER,
    )
    elements.append(Paragraph(
        "Generated by PredictIQ — AI-Powered Cost Estimation | predictiq.app",
        footer_style,
    ))

    doc.build(elements)
    return buffer.getvalue()
