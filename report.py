from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import datetime, io

RISK_COLORS_HEX = {
    "low":      "#2d6a4f",
    "medium":   "#f4a261",
    "high":     "#e76f51",
    "critical": "#c1121f"
}
RISK_EMOJIS = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}


def generate_report(
    factory_name,
    factory_type,
    risk_result,
    actions,
    profit_comparison,
    market_inputs,
    currency_symbol="€",
    oee_data=None,
    shift_plan=None,
    prod_targets=None,
):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    primary  = colors.HexColor("#1a3a5c")
    accent   = colors.HexColor("#0077b6")
    positive = colors.HexColor("#2d6a4f")
    negative = colors.HexColor("#c1121f")

    styles     = getSampleStyleSheet()
    title_s    = ParagraphStyle("t",  fontSize=20, textColor=primary,  alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=4)
    subtitle_s = ParagraphStyle("st", fontSize=11, textColor=accent,   alignment=TA_CENTER, spaceAfter=4)
    h2_s       = ParagraphStyle("h2", fontSize=13, textColor=primary,  fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=6)
    body_s     = ParagraphStyle("b",  fontSize=10, spaceAfter=4, leading=14)
    small_s    = ParagraphStyle("sm", fontSize=8,  textColor=colors.grey)
    footer_s   = ParagraphStyle("f",  fontSize=8,  textColor=colors.grey, alignment=TA_CENTER)

    story = []
    now   = datetime.datetime.now()
    story.append(Paragraph("🏭 AI Risk Intelligence Engine", title_s))
    story.append(Paragraph("Daily Factory Briefing & Action Plan", subtitle_s))
    story.append(Paragraph(f"Generated: {now.strftime('%A, %B %d, %Y at %H:%M')}", small_s))
    story.append(HRFlowable(width="100%", thickness=2, color=accent, spaceAfter=10))

    meta = [
        ["Factory:",            factory_name],
        ["Type:",               factory_type],
        ["Overall Risk Level:", f"{RISK_EMOJIS[risk_result['overall_level']]} {risk_result['overall_level'].upper()}"],
        ["Critical Risks:",     str(risk_result["critical_count"])],
        ["High Risks:",         str(risk_result["high_count"])],
        ["Currency:",           currency_symbol],
    ]
    mt = Table(meta, colWidths=[4*cm, 13*cm])
    mt.setStyle(TableStyle([
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("TEXTCOLOR",     (0, 0), (0, -1), primary),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(mt)
    story.append(Spacer(1, 0.3*cm))

    # ── Profit Impact ─────────────────────────────────────────────────
    story.append(Paragraph("💰 Profit Impact Summary", h2_s))
    diff = profit_comparison["difference"]
    pct  = profit_comparison["improvement_pct"]

    profit_data = [
        ["Metric", "Value"],
        ["Without AI Plan (status quo)", f"{currency_symbol}{profit_comparison['profit_without']:,.2f}"],
        ["With AI Plan (recommended)",   f"{currency_symbol}{profit_comparison['profit_with']:,.2f}"],
        ["Daily Profit Gain",            f"{'+'if diff>=0 else ''}{currency_symbol}{diff:,.2f}  ({pct:+.1f}%)"],
        ["Total Potential Savings",      f"{currency_symbol}{profit_comparison['total_action_savings']:,.2f}"],
    ]
    pt = Table(profit_data, colWidths=[9*cm, 8*cm])
    pt.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), primary),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND",    (0, -2), (-1, -2), colors.HexColor("#e8f5e9")),
        ("FONTNAME",      (0, -2), (-1, -2), "Helvetica-Bold"),
    ]))
    story.append(pt)
    story.append(Spacer(1, 0.3*cm))

    # ── OEE ──────────────────────────────────────────────────────────
    if oee_data:
        story.append(Paragraph("📊 OEE — Overall Equipment Effectiveness", h2_s))
        oee_table_data = [
            ["Metric",        "Value",                                   "Notes"],
            ["OEE Score",     f"{oee_data.get('oee', 0):.1f}%",         oee_data.get("status", "—")],
            ["Availability",  f"{oee_data.get('availability', 0):.1f}%","% uptime"],
            ["Performance",   f"{oee_data.get('performance', 0):.1f}%", "vs rated speed"],
            ["Quality",       f"{oee_data.get('quality', 0):.1f}%",     "good units / total"],
        ]
        ot = Table(oee_table_data, colWidths=[5*cm, 4*cm, 8*cm])
        ot.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), primary),
            ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
            ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("ALIGN",         (1, 0), (1, -1), "CENTER"),
        ]))
        story.append(ot)
        story.append(Spacer(1, 0.3*cm))

    # ── Production Targets ────────────────────────────────────────────
    if prod_targets:
        story.append(Paragraph("🎯 Production Targets", h2_s))
        pt2_data = [
            ["Metric", "Value"],
            ["Max possible units",    f"{prod_targets.get('max_units_possible', 0):,}"],
            ["Projected units today", f"{prod_targets.get('projected_units', 0):,}"],
            ["Break-even units",      f"{prod_targets.get('breakeven_units', 0):,}"],
            ["Margin per unit",       f"{currency_symbol}{prod_targets.get('margin_per_unit', 0):,.2f}"],
            ["Daily revenue (proj.)", f"{currency_symbol}{prod_targets.get('daily_revenue_proj', 0):,.0f}"],
        ]
        pt2 = Table(pt2_data, colWidths=[9*cm, 8*cm])
        pt2.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), primary),
            ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 10),
            ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
            ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(pt2)
        story.append(Spacer(1, 0.3*cm))

    # ── Shift Plan ────────────────────────────────────────────────────
    if shift_plan:
        story.append(Paragraph("🕐 Recommended Shift Plan", h2_s))
        sp_data = [["Shift", "Time", "Workers", "Speed", "Energy Cost"]]
        for s in shift_plan:
            sp_data.append([
                f"{s.get('icon', '')} {s.get('name', '')}",
                s.get("time", "—"),
                str(s.get("workers", "—")),
                f"{s.get('recommended_speed', 1.0):.1f}x",
                f"{s.get('energy_mult', 1.0):.2f}x",
            ])
        spt = Table(sp_data, colWidths=[3.5*cm, 4.5*cm, 2.5*cm, 2.5*cm, 4*cm])
        spt.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), primary),
            ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
            ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("ALIGN",         (2, 0), (-1, -1), "CENTER"),
        ]))
        story.append(spt)
        story.append(Spacer(1, 0.3*cm))

    # ── Risk Scorecard ────────────────────────────────────────────────
    story.append(Paragraph("⚠️ Risk Scorecard", h2_s))
    risk_data = [["Risk", "Level", "Value", "Impact"]]
    for r in risk_result["risks"]:
        risk_data.append([
            f"{r['icon']} {r['name']}",
            f"{RISK_EMOJIS[r['level']]} {r['level'].upper()}",
            r["value"],
            r["impact"][:60] + "..." if len(r["impact"]) > 60 else r["impact"]
        ])
    rt = Table(risk_data, colWidths=[5.5*cm, 2.5*cm, 2.5*cm, 6.5*cm])
    rt.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), primary),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f8f8")]),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#dddddd")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(rt)
    story.append(Spacer(1, 0.3*cm))

    # ── Action Plan ───────────────────────────────────────────────────
    story.append(Paragraph("🎯 AI Recommended Action Plan", h2_s))
    priority_labels = {1: "🔴 URGENT", 2: "🟡 TODAY", 3: "🟢 MONITOR"}
    type_colors = {
        "energy":      "#fff3e0",
        "cost":        "#e8f5e9",
        "maintenance": "#fce4ec",
        "revenue":     "#e3f2fd",
        "strategy":    "#f3e5f5",
        "info":        "#f5f5f5",
    }

    for i, action in enumerate(actions, 1):
        priority_label = priority_labels.get(action["priority"], "🟢 MONITOR")
        bg = colors.HexColor(type_colors.get(action["type"], "#f5f5f5"))
        action_data = [
            [f"#{i} — {action['icon']} {action['title']}", priority_label],
            [action["detail"], f"Impact: {currency_symbol}{action['saving']:,.0f}"]
        ]
        at = Table(action_data, colWidths=[13.5*cm, 3.5*cm])
        at.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), bg),
            ("FONTNAME",      (0, 0), (0, 0),   "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("ALIGN",         (1, 0), (-1, -1), "RIGHT"),
            ("FONTNAME",      (1, 0), (1, 0),   "Helvetica-Bold"),
            ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(at)
        story.append(Spacer(1, 0.15*cm))

    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "AI Risk Intelligence Engine — CITX.C 2026 | Powered by real industrial data (UCI AI4I 2020)",
        footer_s
    ))
    doc.build(story)
    buffer.seek(0)
    return buffer.read()
