"""
history.py — Session History & Trend Tracker
---------------------------------------------
Persists every analysis run to a local SQLite database so managers
can track risk evolution, OEE trends, and profit improvements over time.

Usage
-----
    from history import HistoryDB
    db = HistoryDB()                          # opens/creates risk_history.db
    db.save_session(risk_result, oee, profit) # call after each analysis
    df = db.load_sessions(days=7)             # returns last-7-days DataFrame
    db.close()

Tables
------
    sessions  — one row per analysis run
    risks     — one row per risk category per run (7 rows per session)
"""

import sqlite3
import json
import datetime
import os
import pandas as pd


DB_PATH = os.path.join(os.path.dirname(__file__), "risk_history.db")


class HistoryDB:
    """Lightweight SQLite wrapper for session history."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _create_tables(self):
        cur = self.conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp       TEXT    NOT NULL,
                factory_name    TEXT,
                industry        TEXT,
                overall_level   TEXT,
                health_score    REAL,
                oee             REAL,
                availability    REAL,
                performance     REAL,
                quality         REAL,
                profit_without  REAL,
                profit_with     REAL,
                profit_gain     REAL,
                critical_count  INTEGER,
                high_count      INTEGER,
                medium_count    INTEGER,
                low_count       INTEGER,
                energy_mult     REAL,
                demand_mult     REAL,
                mat_mult        REAL,
                extra_json      TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS risks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  INTEGER NOT NULL,
                name        TEXT,
                level       TEXT,
                raw_value   REAL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)

        self.conn.commit()

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def save_session(
        self,
        risk_result:      dict,
        oee_result:       dict,
        profit_comparison: dict,
        factory_name:     str  = "My Factory",
        industry:         str  = "custom",
        market_inputs:    dict = None,
        extra:            dict = None,
    ) -> int:
        """
        Persist one complete analysis run.

        Parameters
        ----------
        risk_result        : output of risk_engine.score_risks()
        oee_result         : output of risk_engine.calculate_oee()
        profit_comparison  : output of profit_calculator.compare_with_without_plan()
        factory_name       : free-text label shown in the UI
        industry           : industry key (e.g. "machining")
        market_inputs      : the market_inputs dict used for this run
        extra              : any additional JSON-serialisable dict (e.g. ML info)

        Returns
        -------
        session_id (int)
        """
        market = market_inputs or {}
        now    = datetime.datetime.now().isoformat()

        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO sessions (
                timestamp, factory_name, industry,
                overall_level, health_score,
                oee, availability, performance, quality,
                profit_without, profit_with, profit_gain,
                critical_count, high_count, medium_count, low_count,
                energy_mult, demand_mult, mat_mult, extra_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            now,
            factory_name,
            industry,
            risk_result.get("overall_level", "low"),
            risk_result.get("health_score", 100),
            oee_result.get("oee", 0),
            oee_result.get("availability", 0),
            oee_result.get("performance", 0),
            oee_result.get("quality", 0),
            profit_comparison.get("profit_without", 0),
            profit_comparison.get("profit_with", 0),
            profit_comparison.get("difference", 0),
            risk_result.get("critical_count", 0),
            risk_result.get("high_count", 0),
            risk_result.get("medium_count", 0),
            risk_result.get("low_count", 0),
            market.get("energy_cost_multiplier", 1.0),
            market.get("demand_multiplier", 1.0),
            market.get("material_cost_multiplier", 1.0),
            json.dumps(extra or {}),
        ))

        session_id = cur.lastrowid

        # Save individual risk rows
        for r in risk_result.get("risks", []):
            cur.execute("""
                INSERT INTO risks (session_id, name, level, raw_value)
                VALUES (?,?,?,?)
            """, (session_id, r.get("name"), r.get("level"), r.get("raw_value", 0)))

        self.conn.commit()
        return session_id

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def load_sessions(self, days: int = 30) -> pd.DataFrame:
        """
        Return the last `days` days of sessions as a DataFrame,
        newest first.
        """
        cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        df = pd.read_sql_query(
            "SELECT * FROM sessions WHERE timestamp >= ? ORDER BY timestamp DESC",
            self.conn,
            params=(cutoff,),
        )
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df

    def load_risk_trend(self, risk_name: str, days: int = 30) -> pd.DataFrame:
        """
        Return the historical level & raw_value for a specific risk category.
        """
        cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        df = pd.read_sql_query(
            """
            SELECT s.timestamp, r.level, r.raw_value
            FROM   risks r
            JOIN   sessions s ON r.session_id = s.id
            WHERE  r.name = ?
            AND    s.timestamp >= ?
            ORDER  BY s.timestamp ASC
            """,
            self.conn,
            params=(risk_name, cutoff),
        )
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df

    def session_count(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sessions")
        return cur.fetchone()[0]

    def latest_session(self) -> dict | None:
        """Return the most recent session row as a dict, or None."""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM sessions ORDER BY timestamp DESC LIMIT 1")
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def delete_old_sessions(self, keep_days: int = 90):
        """Remove sessions older than `keep_days` to keep the DB small."""
        cutoff = (datetime.datetime.now() - datetime.timedelta(days=keep_days)).isoformat()
        cur    = self.conn.cursor()
        cur.execute("DELETE FROM sessions WHERE timestamp < ?", (cutoff,))
        cur.execute(
            "DELETE FROM risks WHERE session_id NOT IN (SELECT id FROM sessions)"
        )
        self.conn.commit()

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


# ---------------------------------------------------------------------------
# Streamlit helper — call this once inside your app to render the history tab
# ---------------------------------------------------------------------------

def render_history_tab(db: HistoryDB, currency_symbol: str = "€"):
    """
    Drop-in Streamlit UI block for a 'History' tab.

    Call inside `with tab_history:` (or anywhere in your app):
        from history import HistoryDB, render_history_tab
        db = HistoryDB()
        render_history_tab(db, currency_symbol="€")
    """
    try:
        import streamlit as st
        import plotly.graph_objects as go
        import plotly.express as px
    except ImportError:
        return

    total = db.session_count()

    if total == 0:
        st.info("No sessions recorded yet. Run your first analysis to start tracking history.")
        return

    st.markdown(f"**{total} sessions recorded** in the database.")

    days = st.slider("Show last N days", 7, 90, 30, key="hist_days")
    df   = db.load_sessions(days=days)

    if df.empty:
        st.warning(f"No sessions in the last {days} days.")
        return

    # ── KPI summary ──────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sessions analysed",  len(df))
    c2.metric("Avg OEE",            f"{df['oee'].mean():.1f}%")
    c3.metric("Avg health score",   f"{df['health_score'].mean():.0f}/100")
    c4.metric(f"Avg profit gain",   f"{currency_symbol}{df['profit_gain'].mean():,.0f}")

    st.markdown("---")

    # ── OEE trend ────────────────────────────────────────────────────
    fig_oee = go.Figure()
    fig_oee.add_trace(go.Scatter(
        x=df["timestamp"], y=df["oee"],
        mode="lines+markers",
        line=dict(color="#00d4ff", width=2),
        marker=dict(size=6),
        name="OEE %",
        fill="tozeroy",
        fillcolor="rgba(0,212,255,0.06)",
    ))
    fig_oee.update_layout(
        title="OEE % over time",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c8d8e8"),
        height=280,
        margin=dict(l=40, r=20, t=40, b=30),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", range=[0, 105]),
    )
    st.plotly_chart(fig_oee, use_container_width=True)

    # ── Health score trend ───────────────────────────────────────────
    fig_hs = go.Figure()
    fig_hs.add_trace(go.Scatter(
        x=df["timestamp"], y=df["health_score"],
        mode="lines+markers",
        line=dict(color="#00ff87", width=2),
        marker=dict(size=6),
        name="Health Score",
    ))
    fig_hs.update_layout(
        title="Factory health score over time",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c8d8e8"),
        height=280,
        margin=dict(l=40, r=20, t=40, b=30),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", range=[0, 105]),
    )
    st.plotly_chart(fig_hs, use_container_width=True)

    # ── Risk level breakdown ─────────────────────────────────────────
    fig_risk = go.Figure()
    for col, color, label in [
        ("critical_count", "#ff4757", "Critical"),
        ("high_count",     "#ff6b35", "High"),
        ("medium_count",   "#f59e0b", "Medium"),
        ("low_count",      "#00ff87", "Low"),
    ]:
        fig_risk.add_trace(go.Bar(
            x=df["timestamp"], y=df[col],
            name=label,
            marker_color=color,
        ))
    fig_risk.update_layout(
        barmode="stack",
        title="Risk level breakdown per session",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c8d8e8"),
        height=280,
        margin=dict(l=40, r=20, t=40, b=30),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
    )
    st.plotly_chart(fig_risk, use_container_width=True)

    # ── Profit gain trend ────────────────────────────────────────────
    fig_profit = go.Figure()
    fig_profit.add_trace(go.Bar(
        x=df["timestamp"], y=df["profit_gain"],
        marker_color=[
            "#00ff87" if v >= 0 else "#ff4757"
            for v in df["profit_gain"]
        ],
        name="Profit gain",
    ))
    fig_profit.update_layout(
        title=f"Daily profit gain ({currency_symbol}) from AI plan",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c8d8e8"),
        height=280,
        margin=dict(l=40, r=20, t=40, b=30),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
    )
    st.plotly_chart(fig_profit, use_container_width=True)

    # ── Raw table ────────────────────────────────────────────────────
    with st.expander("Raw session data"):
        display_cols = [
            "timestamp", "factory_name", "industry", "overall_level",
            "health_score", "oee", "profit_without", "profit_with", "profit_gain",
        ]
        st.dataframe(
            df[display_cols].rename(columns={
                "timestamp":     "Date / Time",
                "factory_name":  "Factory",
                "industry":      "Industry",
                "overall_level": "Risk Level",
                "health_score":  "Health",
                "oee":           "OEE %",
                "profit_without": f"Profit w/o Plan ({currency_symbol})",
                "profit_with":    f"Profit w/ Plan ({currency_symbol})",
                "profit_gain":    f"Gain ({currency_symbol})",
            }),
            use_container_width=True,
        )
