import plotly.graph_objects as go
import streamlit as st
from industry_profiles import get_profile, get_compliance_status, get_weighted_risks, get_industry_kpi_targets


def render_industry_tab(factory_type, factory_inputs, market_inputs, risk_result, oee_data, currency):
    from config import FACTORY_PRESETS
    preset   = FACTORY_PRESETS.get(factory_type, {})
    ind_key  = preset.get("industry", "custom")
    profile  = get_profile(ind_key)
    kpi_tgts = get_industry_kpi_targets(factory_inputs, profile)
    sym      = currency["symbol"]

    st.markdown(f"""
    <div style="background:#0d1627;border:1px solid #1a3a5f;border-radius:12px;
                padding:1.5rem 2rem;margin-bottom:1.5rem;display:flex;align-items:center;gap:1.5rem;">
        <div style="font-size:3rem;">{profile['icon']}</div>
        <div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.4rem;font-weight:700;
                        color:#c8d8e8;text-transform:uppercase;letter-spacing:2px;">
                {profile['name']}
            </div>
            <div style="font-size:0.85rem;color:#5a7a9a;margin-top:0.2rem;">
                Industry Intelligence · Benchmarks · Compliance · KPI Targets
            </div>
        </div>
        <div style="margin-left:auto;background:#060b14;border:1px solid #1a3a5f;
                    border-radius:8px;padding:0.8rem 1.2rem;text-align:center;">
            <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:1px;color:#3a5a7a;">
                World-Class OEE
            </div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.8rem;font-weight:700;color:#00ff87;">
                {profile['oee_world_class']}%
            </div>
            <div style="font-size:0.7rem;color:#3a5a7a;">industry benchmark</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_bench, col_comply = st.columns([1, 1])

    with col_bench:
        st.markdown('<div class="section-header">OEE vs Industry Benchmark</div>', unsafe_allow_html=True)

        your_oee  = oee_data["oee"]
        world_cls = profile["oee_world_class"]
        ind_avg   = profile["oee_industry_avg"]
        ind_poor  = profile["oee_poor"]

        if your_oee >= world_cls:
            bench_label = "🏆 World Class"
            bench_color = "#00ff87"
        elif your_oee >= ind_avg:
            bench_label = "✅ Above Industry Average"
            bench_color = "#00d4ff"
        elif your_oee >= ind_poor:
            bench_label = "⚠️ Below Industry Average"
            bench_color = "#f59e0b"
        else:
            bench_label = "🔴 Poor — Significant Losses"
            bench_color = "#ff4757"

        fig_bench = go.Figure()

        fig_bench.add_shape(type="rect", x0=0,        x1=ind_poor,  y0=0, y1=1,
                            fillcolor="rgba(255,71,87,0.06)",  line_width=0, layer="below")
        fig_bench.add_shape(type="rect", x0=ind_poor, x1=ind_avg,   y0=0, y1=1,
                            fillcolor="rgba(245,158,11,0.06)", line_width=0, layer="below")
        fig_bench.add_shape(type="rect", x0=ind_avg,  x1=world_cls, y0=0, y1=1,
                            fillcolor="rgba(0,212,255,0.06)",  line_width=0, layer="below")
        fig_bench.add_shape(type="rect", x0=world_cls,x1=100,       y0=0, y1=1,
                            fillcolor="rgba(0,255,135,0.06)",  line_width=0, layer="below")

        for val, label, color in [
            (ind_poor, "Poor",         "#ff4757"),
            (ind_avg,  "Industry Avg", "#f59e0b"),
            (world_cls,"World Class",  "#00ff87"),
        ]:
            fig_bench.add_vline(x=val, line_dash="dot", line_color=color, line_width=1.5,
                                annotation_text=f"{label} {val}%",
                                annotation_font={"color": color, "size": 10},
                                annotation_position="top right")

        fig_bench.add_trace(go.Bar(
            x=[your_oee], y=["Your OEE"],
            orientation="h",
            marker_color=bench_color,
            marker_line_width=0,
            text=[f"{your_oee}%"],
            textposition="inside",
            textfont={"color": "#000", "size": 13, "family": "Rajdhani"},
            width=0.5
        ))

        fig_bench.update_layout(
            paper_bgcolor="#0d1627", plot_bgcolor="#0d1627",
            xaxis={"range": [0, 100], "tickfont": {"color": "#5a7a9a", "size": 10},
                   "gridcolor": "#1a3a5f", "ticksuffix": "%"},
            yaxis={"tickfont": {"color": "#a0b8d0"}, "gridcolor": "#1a3a5f"},
            height=140, margin=dict(t=40, b=20, l=10, r=20),
            showlegend=False
        )
        st.plotly_chart(fig_bench, use_container_width=True)

        st.markdown(f"""
        <div style="background:#060b14;border:1px solid #1a3a5f;border-radius:8px;
                    padding:1rem;margin-top:-0.5rem;text-align:center;">
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.1rem;
                        font-weight:700;color:{bench_color};">{bench_label}</div>
            <div style="font-size:0.8rem;color:#5a7a9a;margin-top:0.3rem;">
                {'You are already at world-class level 🏆' if your_oee >= world_cls else
                 f'Close the {world_cls - your_oee:.1f}% OEE gap = +{sym}{(world_cls - your_oee) * factory_inputs.get("machines",10) * factory_inputs.get("product_price",200) * factory_inputs.get("hours",8) * 0.5:,.0f} revenue potential'}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-header" style="margin-top:1.5rem;">Industry KPI Targets</div>',
                    unsafe_allow_html=True)

        kpi_rows = [
            ("MTBF Target",         f"{kpi_tgts['mtbf_target_h']}h",         "Time between failures",                          "#00d4ff"),
            ("MTTR Target",         f"{kpi_tgts['mttr_target_h']}h",         "Time to repair",                                 "#f59e0b"),
            ("Availability Target", f"{kpi_tgts['availability_target']}%",   "Planned uptime",                                 "#00ff87"),
            ("TEEP",                f"{kpi_tgts['teep']}%",                  "Total effective equip performance (24h)",         "#a0b8d0"),
            ("Max Scrap Rate",      f"{kpi_tgts['target_scrap_pct']}%",      "Good units / total",                             "#00ff87"),
            ("Max Rework Rate",     f"{kpi_tgts['target_rework_pct']}%",     "Rework / total",                                 "#f59e0b"),
        ]

        for label, value, desc, color in kpi_rows:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:0.6rem 0.8rem;border-bottom:1px solid #1a3a5f;">
                <div>
                    <div style="font-size:0.85rem;color:#c8d8e8;font-weight:600;">{label}</div>
                    <div style="font-size:0.72rem;color:#3a5a7a;">{desc}</div>
                </div>
                <div style="font-family:'Rajdhani',sans-serif;font-size:1.2rem;
                            font-weight:700;color:{color};">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_comply:
        st.markdown('<div class="section-header">Compliance Checker</div>', unsafe_allow_html=True)

        compliance_items = get_compliance_status(profile, risk_result)
        pass_count = sum(1 for c in compliance_items if "OK"   in c["status"])
        warn_count = sum(1 for c in compliance_items if "RISK" in c["status"] or "REVIEW" in c["status"])
        fail_count = sum(1 for c in compliance_items if "FAIL" in c["status"])

        st.markdown(f"""
        <div style="display:flex;gap:1rem;margin-bottom:1rem;">
            <div style="flex:1;background:#060b14;border:1px solid #1a3a5f;border-radius:8px;
                        padding:0.8rem;text-align:center;">
                <div style="font-family:'Rajdhani',sans-serif;font-size:1.8rem;
                            font-weight:700;color:#00ff87;">{pass_count}</div>
                <div style="font-size:0.72rem;color:#3a5a7a;">Compliant</div>
            </div>
            <div style="flex:1;background:#060b14;border:1px solid #1a3a5f;border-radius:8px;
                        padding:0.8rem;text-align:center;">
                <div style="font-family:'Rajdhani',sans-serif;font-size:1.8rem;
                            font-weight:700;color:#f59e0b;">{warn_count}</div>
                <div style="font-size:0.72rem;color:#3a5a7a;">Review Needed</div>
            </div>
            <div style="flex:1;background:#060b14;border:1px solid #1a3a5f;border-radius:8px;
                        padding:0.8rem;text-align:center;">
                <div style="font-family:'Rajdhani',sans-serif;font-size:1.8rem;
                            font-weight:700;color:#ff4757;">{fail_count}</div>
                <div style="font-size:0.72rem;color:#3a5a7a;">Non-Compliant</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        for item in compliance_items:
            crit_badge = (
                '<span style="background:rgba(255,71,87,0.15);color:#ff4757;'
                'font-size:0.6rem;padding:0.1rem 0.35rem;border-radius:3px;'
                'margin-left:0.4rem;border:1px solid rgba(255,71,87,0.3);">MANDATORY</span>'
                if item["critical"] else ""
            )
            st.markdown(f"""
            <div style="background:#0d1627;border:1px solid #1a3a5f;border-radius:8px;
                        padding:0.8rem 1rem;margin-bottom:0.5rem;
                        border-left:3px solid {item['color']};">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                        <div style="font-size:0.9rem;font-weight:700;color:#c8d8e8;">
                            {item['standard']}{crit_badge}
                        </div>
                        <div style="font-size:0.75rem;color:#5a7a9a;">{item['area']}</div>
                    </div>
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.78rem;
                                font-weight:600;color:{item['color']};white-space:nowrap;
                                margin-left:0.5rem;">{item['status']}</div>
                </div>
                <div style="font-size:0.75rem;color:#3a5a7a;margin-top:0.3rem;">{item['note']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="font-size:0.72rem;color:#3a5a7a;margin-top:0.5rem;font-style:italic;
                    padding:0.5rem;border:1px solid #1a3a5f;border-radius:6px;">
            ⚠️ This is an AI risk assessment, not a legal compliance audit.
            Always verify with a certified auditor for regulatory submissions.
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Industry-Weighted Risk Analysis</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:0.82rem;color:#5a7a9a;margin-bottom:1rem;">
        Standard risks re-weighted for <b style="color:#00d4ff;">{profile['name']}</b>.
        A risk rated "Medium" globally can be "Critical" in your industry if it hits a key cost driver.
    </div>
    """, unsafe_allow_html=True)

    weighted_risks = get_weighted_risks(risk_result["risks"], profile)
    level_color    = {"low": "#00ff87", "medium": "#f59e0b", "high": "#ff6b35", "critical": "#ff4757"}

    wc1, wc2 = st.columns(2)
    for i, wr in enumerate(weighted_risks):
        col    = wc1 if i % 2 == 0 else wc2
        std_lvl = wr["level"]
        w_lvl   = wr["weighted_level"]
        escalated = (
            {"low": 0, "medium": 1, "high": 2, "critical": 3}[w_lvl] >
            {"low": 0, "medium": 1, "high": 2, "critical": 3}[std_lvl]
        )
        escalation_html = (
            f'<span style="font-size:0.7rem;color:#f59e0b;"> ↑ escalated for {profile["name"]}</span>'
            if escalated else ""
        )
        with col:
            st.markdown(f"""
            <div style="background:#0d1627;border:1px solid #1a3a5f;border-radius:8px;
                        padding:0.9rem 1.1rem;margin-bottom:0.7rem;
                        border-left:3px solid {level_color[w_lvl]};">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div style="font-size:0.9rem;font-weight:700;color:#c8d8e8;">
                        {wr['icon']} {wr['name']}
                    </div>
                    <div>
                        <span style="font-family:'Rajdhani',sans-serif;font-weight:700;
                                     color:{level_color[w_lvl]};">{w_lvl.upper()}</span>
                        <span style="font-size:0.7rem;color:#3a5a7a;margin-left:0.3rem;">
                            (weight: {wr['weight']:.1f}x)
                        </span>
                    </div>
                </div>
                {escalation_html}
            </div>
            """, unsafe_allow_html=True)

    col_fail, col_tip = st.columns([1, 1])

    with col_fail:
        st.markdown('<div class="section-header">Typical Failure Modes</div>', unsafe_allow_html=True)
        failures = profile.get("typical_failures", [])
        colors_f = ["#ff4757", "#ff6b35", "#f59e0b", "#00d4ff", "#5a7a9a"]

        labels, values = [], []
        for f in failures:
            try:
                parts = f.rsplit("(", 1)
                labels.append(parts[0].strip())
                values.append(float(parts[1].replace("%)", "")))
            except Exception:
                labels.append(f)
                values.append(20)

        fig_f = go.Figure(go.Bar(
            x=values, y=labels, orientation="h",
            marker_color=colors_f[:len(labels)],
            marker_line_width=0,
            text=[f"{v:.0f}%" for v in values],
            textposition="outside",
            textfont={"color": "#a0b8d0", "size": 11, "family": "IBM Plex Mono"}
        ))
        fig_f.update_layout(
            paper_bgcolor="#0d1627", plot_bgcolor="#0d1627",
            xaxis={"visible": False},
            yaxis={"tickfont": {"color": "#a0b8d0", "size": 11, "family": "IBM Plex Sans"},
                   "gridcolor": "#1a3a5f"},
            height=220, margin=dict(t=10, b=10, l=10, r=50),
            showlegend=False
        )
        st.plotly_chart(fig_f, use_container_width=True)

    with col_tip:
        st.markdown('<div class="section-header">Industry Intelligence Tip</div>',
                    unsafe_allow_html=True)
        tip  = profile.get("industry_tip", "")
        kpis = profile.get("key_kpis", [])
        st.markdown(f"""
        <div style="background:#0d1627;border:1px solid #1a3a5f;border-radius:12px;
                    padding:1.5rem;height:100%;">
            <div style="font-size:0.9rem;color:#a0b8d0;line-height:1.7;margin-bottom:1.2rem;">
                💡 {tip}
            </div>
            <div style="border-top:1px solid #1a3a5f;padding-top:1rem;">
                <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;
                            color:#3a5a7a;margin-bottom:0.5rem;">Key KPIs to Track</div>
                <div style="display:flex;flex-wrap:wrap;gap:0.4rem;">
                    {''.join(f"""<span style="background:#060b14;border:1px solid #1a3a5f;
                        border-radius:4px;padding:0.2rem 0.6rem;font-size:0.78rem;
                        color:#00d4ff;font-family:'IBM Plex Mono',monospace;">{kpi}</span>"""
                        for kpi in kpis)}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
