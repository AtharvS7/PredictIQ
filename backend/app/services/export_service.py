"""
Predictify Export Service
Generates PDF reports for estimates using ReportLab.
Supports multi-currency output with live exchange rates.
"""
import io
from datetime import datetime
from typing import Optional
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

# Currency symbols for PDF display
CURRENCY_SYMBOLS: dict[str, str] = {
    "USD": "$", "INR": "₹", "EUR": "€", "GBP": "£",
    "AED": "AED ", "SGD": "S$", "CAD": "CA$", "AUD": "A$",
    "JPY": "¥", "CHF": "Fr ", "CNY": "¥", "HKD": "HK$",
    "KRW": "₩", "BRL": "R$", "MXN": "$", "NZD": "NZ$",
    "SEK": "kr ", "NOK": "kr ", "DKK": "kr ", "ZAR": "R",
}


def _format_currency(
    amount: float,
    currency_code: str,
    symbol: str,
) -> str:
    """Format an amount for PDF display, using Indian numbering for INR."""
    if currency_code == "INR":
        if amount >= 10_000_000:
            return f"{symbol}{amount / 10_000_000:.2f}Cr"
        elif amount >= 100_000:
            return f"{symbol}{amount / 100_000:.2f}L"
        else:
            # Indian number formatting
            s = f"{amount:,.0f}"
            # Convert Western grouping to Indian grouping for <1L
            return f"{symbol}{s}"
    elif currency_code in ("JPY", "KRW", "VND", "IDR"):
        # No decimals for these currencies
        return f"{symbol}{amount:,.0f}"
    else:
        return f"{symbol}{amount:,.0f}"


def generate_pdf_report(
    estimate: dict,
    currency_code: str = "USD",
    exchange_rate: float = 1.0,
) -> bytes:
    """
    Generate a branded PDF report for an estimate.

    Args:
        estimate: Full estimate result dictionary.
        currency_code: Target currency code (e.g., "USD", "INR", "EUR").
        exchange_rate: Exchange rate from USD to target currency.

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
    symbol = CURRENCY_SYMBOLS.get(currency_code.upper(), currency_code + " ")
    cc = currency_code.upper()

    def convert(usd_amount: float) -> float:
        """Convert a USD amount to the target currency."""
        return usd_amount * exchange_rate

    def fmt(usd_amount: float) -> str:
        """Convert and format a USD amount in the target currency."""
        return _format_currency(convert(usd_amount), cc, symbol)

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
    elements.append(Paragraph("Predictify", title_style))
    elements.append(Paragraph(
        f"Cost Estimation Report — {estimate.get('project_name', 'Project')}",
        subtitle_style,
    ))
    elements.append(HRFlowable(
        width="100%", thickness=2, color=BRAND_BLUE, spaceAfter=20
    ))

    # Meta info
    hourly_rate_display = fmt(inputs.get("hourly_rate_usd", 75))
    meta_data = [
        ["Generated:", datetime.now().strftime("%B %d, %Y at %I:%M %p")],
        ["Currency:", f"{cc} ({symbol.strip()})"],
        ["Project Type:", inputs.get("project_type", "N/A")],
        ["Complexity:", inputs.get("complexity", "N/A")],
        ["Methodology:", inputs.get("methodology", "N/A")],
        ["Team Size:", str(inputs.get("team_size", "N/A"))],
        ["Duration:", f"{inputs.get('duration_months', 'N/A')} months"],
        ["Hourly Rate:", f"{hourly_rate_display}/hr"],
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
            f"Cost ({cc})",
            fmt(outputs.get("cost_min_usd", 0)),
            fmt(outputs.get("cost_likely_usd", 0)),
            fmt(outputs.get("cost_max_usd", 0)),
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

    phase_header = ["Phase", "Effort (hrs)", f"Cost ({cc})", "Duration (wks)", "% of Total"]
    phase_rows = [phase_header]
    for phase in outputs.get("phase_breakdown", []):
        phase_rows.append([
            phase.get("phase", ""),
            f"{phase.get('effort_hours', 0):,.0f}",
            fmt(phase.get("cost_usd", 0)),
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

    # ── Exchange Rate Note ──────────────────────────────────
    if cc != "USD":
        elements.append(Spacer(1, 16))
        rate_note_style = ParagraphStyle(
            "RateNote", parent=styles["Normal"],
            fontSize=8, textColor=BRAND_GRAY, alignment=TA_LEFT,
        )
        elements.append(Paragraph(
            f"Exchange rate used: 1 USD = {exchange_rate:.4f} {cc} "
            f"(Rate fetched on {datetime.now().strftime('%B %d, %Y')})",
            rate_note_style,
        ))

    # ── Footer ──────────────────────────────────────────────
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=1, color=BRAND_GRAY))
    elements.append(Spacer(1, 6))
    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"],
        fontSize=8, textColor=BRAND_GRAY, alignment=TA_CENTER,
    )
    elements.append(Paragraph(
        "Generated by Predictify — AI-Powered Cost Estimation | Predictify.app",
        footer_style,
    ))

    doc.build(elements)
    return buffer.getvalue()
