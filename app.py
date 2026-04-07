import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys, os, datetime, random, shutil

sys.path.insert(0, os.path.dirname(__file__))

from config import FACTORY_PRESETS, RISK_COLORS, RISK_EMOJIS, CURRENCIES
from tab_industry import render_industry_tab
from risk_engine import score_risks, calculate_oee, calculate_production_targets, calculate_shift_plan
from action_planner import generate_action_plan
from profit_calculator import compare_with_without_plan, calculate_profit
from report import generate_report
from ml_engine import MLEngine
from api_fetcher import fetch_all, CITY_COORDINATES
from history import HistoryDB, render_history_tab
from _visual_engine import inject as _ve_inject

st.set_page_config(
    page_title="FactoryIQ — AI Operations Advisor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

_ve_inject()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

:root {
    --cyan:    #00d4ff;
    --green:   #00ff87;
    --amber:   #f59e0b;
    --red:     #ff4757;
    --orange:  #ff6b35;
    --navy:    #060b14;
    --card:    #0d1627;
    --border:  #1a3a5f;
    --text:    #c8d8e8;
    --muted:   #5a7a9a;
    --dimmed:  #3a5a7a;
}

*, html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    box-sizing: border-box;
}

.stApp {
    background: var(--navy);
    color: var(--text);
}

#fiq-bg {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}
#fiq-bg::before {
    content: '';
    position: absolute;
    inset: -40px;
    background-image:
        linear-gradient(rgba(0,212,255,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,0.04) 1px, transparent 1px);
    background-size: 44px 44px;
    animation: grid-drift 18s linear infinite;
}
#fiq-bg::after {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse 60% 40% at 20% 50%, rgba(0,119,255,0.06) 0%, transparent 70%),
        radial-gradient(ellipse 50% 35% at 80% 30%, rgba(0,212,255,0.04) 0%, transparent 70%),
        radial-gradient(ellipse 40% 50% at 50% 90%, rgba(0,255,135,0.03) 0%, transparent 70%);
    animation: ambient-pulse 8s ease-in-out infinite alternate;
}
@keyframes grid-drift {
    0%   { transform: translateY(0) translateX(0); }
    100% { transform: translateY(44px) translateX(0); }
}
@keyframes ambient-pulse {
    0%   { opacity: 0.6; }
    100% { opacity: 1.2; }
}

[data-testid="stSidebar"] {
    background: #080f1e !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }
[data-testid="stSidebar"] * { color: #a0b8d0 !important; }
[data-testid="stSidebar"] label {
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--muted) !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stNumberInput input,
[data-testid="stSidebar"] .stTextInput input {
    background: #0d1a2e !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 6px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div:focus-within,
[data-testid="stSidebar"] .stNumberInput input:focus,
[data-testid="stSidebar"] .stTextInput input:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 2px rgba(0,212,255,0.12) !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #00d4ff 0%, #0077ff 100%) !important;
    color: #000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 0.7rem !important;
    width: 100% !important;
    transition: all 0.25s !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.3) !important;
    position: relative !important;
    overflow: hidden !important;
}
[data-testid="stSidebar"] .stButton > button::after {
    content: '' !important;
    position: absolute !important;
    inset: 0 !important;
    background: linear-gradient(105deg, transparent 35%, rgba(255,255,255,0.25) 50%, transparent 65%) !important;
    transform: translateX(-100%) !important;
    transition: transform 0.5s !important;
}
[data-testid="stSidebar"] .stButton > button:hover::after {
    transform: translateX(100%) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    box-shadow: 0 0 40px rgba(0,212,255,0.7) !important;
    transform: translateY(-2px) !important;
}


.stTabs [data-baseweb="tab-list"] {
    background: #080f1e;
    border-bottom: 1px solid var(--border);
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    padding: 0.8rem 1.5rem !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.25s !important;
    position: relative !important;
}
.stTabs [data-baseweb="tab"]::after {
    content: '' !important;
    position: absolute !important;
    bottom: 0; left: 50%; right: 50% !important;
    height: 2px !important;
    background: var(--cyan) !important;
    transition: left 0.3s, right 0.3s !important;
}
.stTabs [aria-selected="true"] {
    color: var(--cyan) !important;
    border-bottom-color: var(--cyan) !important;
}


.metric-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.3s cubic-bezier(0.23,1,0.32,1), box-shadow 0.3s;
    animation: card-enter 0.6s cubic-bezier(0.23,1,0.32,1) both;
}
.metric-card:nth-child(1) { animation-delay: 0.05s; }
.metric-card:nth-child(2) { animation-delay: 0.12s; }
.metric-card:nth-child(3) { animation-delay: 0.19s; }
.metric-card:nth-child(4) { animation-delay: 0.26s; }

@keyframes card-enter {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}

.metric-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--accent, var(--cyan));
    transition: width 0.3s;
}
.metric-card:hover::before { width: 5px; }

.metric-card::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(105deg,
        transparent 35%,
        rgba(255,255,255,0.025) 50%,
        transparent 65%);
    transform: translateX(-150%);
    transition: transform 0.7s ease;
    pointer-events: none;
}
.metric-card:hover::after  { transform: translateX(150%); }
.metric-card:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 12px 40px rgba(0,0,0,0.5), 0 0 20px rgba(0,212,255,0.08);
    border-color: rgba(0,212,255,0.3);
}

.metric-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--muted);
    margin-bottom: 0.4rem;
}
.metric-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: var(--accent, var(--cyan));
    line-height: 1;
    margin-bottom: 0.3rem;
    animation: num-pop 0.5s cubic-bezier(0.23,1,0.32,1) both;
    animation-delay: 0.3s;
}
@keyframes num-pop {
    from { opacity: 0; transform: scale(0.85); }
    to   { opacity: 1; transform: scale(1); }
}
.metric-sub { font-size: 0.82rem; color: var(--muted); }


.section-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: var(--text);
    padding-bottom: 0.6rem;
    margin-bottom: 1.2rem;
    margin-top: 1rem;
    position: relative;
}
.section-header::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0;
    height: 1px;
    width: 0%;
    background: linear-gradient(90deg, var(--cyan), transparent);
    animation: header-line 0.8s 0.2s cubic-bezier(0.23,1,0.32,1) forwards;
}
@keyframes header-line {
    to { width: 100%; }
}


.risk-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    transition: all 0.25s;
    animation: slide-in-left 0.5s cubic-bezier(0.23,1,0.32,1) both;
}
.risk-card:nth-child(odd)  { animation-delay: 0.05s; }
.risk-card:nth-child(even) { animation-delay: 0.12s; }
@keyframes slide-in-left {
    from { opacity: 0; transform: translateX(-16px); }
    to   { opacity: 1; transform: translateX(0); }
}
.risk-card:hover { border-color: #2a5a8f; transform: translateX(4px); }
.risk-card.risk-critical {
    border-left: 3px solid var(--red);
    background: #120810;
    animation: slide-in-left 0.5s both, critical-breathe 3s 1s ease-in-out infinite;
}
@keyframes critical-breathe {
    0%,100% { box-shadow: 0 0 0 rgba(255,71,87,0); border-left-color: var(--red); }
    50%     { box-shadow: 0 0 18px rgba(255,71,87,0.25); border-left-color: #ff6b6b; }
}
.risk-card.risk-high   { border-left: 3px solid var(--orange); }
.risk-card.risk-medium { border-left: 3px solid var(--amber); }
.risk-card.risk-low    { border-left: 3px solid var(--green); }

.risk-level-badge {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    padding: 0.15rem 0.5rem;
    border-radius: 3px;
    margin-bottom: 0.3rem;
}
.badge-critical { background: rgba(255,71,87,0.15); color: var(--red);    border: 1px solid rgba(255,71,87,0.3); }
.badge-high     { background: rgba(255,107,53,0.15); color: var(--orange); border: 1px solid rgba(255,107,53,0.3); }
.badge-medium   { background: rgba(245,158,11,0.15); color: var(--amber);  border: 1px solid rgba(245,158,11,0.3); }
.badge-low      { background: rgba(0,255,135,0.12);  color: var(--green);  border: 1px solid rgba(0,255,135,0.3); }


.action-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.25s cubic-bezier(0.23,1,0.32,1);
    position: relative;
    overflow: hidden;
    animation: slide-in-right 0.5s cubic-bezier(0.23,1,0.32,1) both;
}
.action-card:nth-child(1) { animation-delay: 0.05s; }
.action-card:nth-child(2) { animation-delay: 0.12s; }
.action-card:nth-child(3) { animation-delay: 0.19s; }
.action-card:nth-child(4) { animation-delay: 0.26s; }
.action-card:nth-child(5) { animation-delay: 0.33s; }
@keyframes slide-in-right {
    from { opacity: 0; transform: translateX(20px); }
    to   { opacity: 1; transform: translateX(0); }
}
.action-card:hover { border-color: #2a5a8f; transform: translateX(5px); box-shadow: -4px 0 20px rgba(0,212,255,0.06); }
.action-urgent {
    border-left: 4px solid var(--red);
    animation: slide-in-right 0.5s both, urgent-pulse 2.5s 0.8s ease-in-out infinite;
}
@keyframes urgent-pulse {
    0%,100% { border-left-color: var(--red); }
    50%     { border-left-color: #ff8a95; box-shadow: -3px 0 14px rgba(255,71,87,0.3); }
}
.action-today   { border-left: 4px solid var(--amber); }
.action-monitor { border-left: 4px solid var(--green); }

.action-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #e0eaf5;
    margin-bottom: 0.35rem;
}
.action-detail { font-size: 0.88rem; color: #7a9ab8; line-height: 1.5; }
.action-saving { font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem; font-weight: 500; margin-top: 0.5rem; }

.oee-bar-container {
    background: #060b14;
    border-radius: 6px;
    height: 10px;
    overflow: hidden;
    margin-top: 0.4rem;
}
.oee-bar-fill {
    height: 100%;
    border-radius: 6px;
    position: relative;
    overflow: hidden;
    animation: bar-grow 1.2s cubic-bezier(0.23,1,0.32,1) both;
}
@keyframes bar-grow {
    from { transform: scaleX(0); transform-origin: left; }
    to   { transform: scaleX(1); transform-origin: left; }
}
.oee-bar-fill::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%);
    animation: bar-shimmer 2.5s 1.5s linear infinite;
}
@keyframes bar-shimmer {
    0%   { transform: translateX(-100%); }
    100% { transform: translateX(200%); }
}

.machine-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding: 1rem 0;
}
.machine-dot {
    width: 34px;
    height: 34px;
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.6rem;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 500;
    cursor: default;
    transition: transform 0.2s cubic-bezier(0.23,1,0.32,1), box-shadow 0.2s;
    animation: dot-boot 0.4s cubic-bezier(0.23,1,0.32,1) both;
}
.machine-dot:hover { transform: scale(1.35) !important; z-index: 10; }
.machine-ok {
    background: rgba(0,255,135,0.12);
    color: var(--green);
    border: 1px solid rgba(0,255,135,0.25);
}
.machine-ok:hover { box-shadow: 0 0 16px rgba(0,255,135,0.5); }
.machine-warn {
    background: rgba(245,158,11,0.12);
    color: var(--amber);
    border: 1px solid rgba(245,158,11,0.3);
    animation: dot-boot 0.4s both, warn-flicker 4s ease-in-out infinite;
}
@keyframes warn-flicker {
    0%,92%,96%,100% { opacity: 1; }
    94% { opacity: 0.6; }
}
.machine-critical {
    background: rgba(255,71,87,0.15);
    color: var(--red);
    border: 1px solid rgba(255,71,87,0.4);
    animation: dot-boot 0.4s both, crit-pulse 2s ease-in-out infinite;
}
@keyframes crit-pulse {
    0%,100% { box-shadow: 0 0 0 0 rgba(255,71,87,0.5); }
    50%     { box-shadow: 0 0 0 5px rgba(255,71,87,0); }
}
.machine-critical:hover { box-shadow: 0 0 20px rgba(255,71,87,0.7) !important; }
.machine-off {
    background: rgba(90,122,154,0.07);
    color: var(--muted);
    border: 1px solid rgba(90,122,154,0.15);
}
@keyframes dot-boot {
    from { opacity: 0; transform: scale(0.4); }
    to   { opacity: 1; transform: scale(1); }
}


.topbar {
    background: linear-gradient(135deg, #0d1627 0%, #0a1422 100%);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    animation: card-enter 0.5s cubic-bezier(0.23,1,0.32,1) both;
}
.topbar::before {
    content: '';
    position: absolute;
    top: 0; left: -60%;
    width: 50%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
    animation: topbar-scan 4s linear infinite;
}
@keyframes topbar-scan {
    0%   { left: -60%; }
    100% { left: 120%; }
}
.topbar-logo {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    background: linear-gradient(90deg, var(--cyan), #60efff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ── LIVE DOT ────────────────────────────────────────── */
.live-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: var(--green);
    border-radius: 50%;
    margin-right: 6px;
    animation: live-pulse 1.5s ease-in-out infinite;
    box-shadow: 0 0 6px var(--green);
}
@keyframes live-pulse {
    0%,100% { opacity: 1;   box-shadow: 0 0 8px var(--green), 0 0 0 0 rgba(0,255,135,0.4); }
    50%     { opacity: 0.4; box-shadow: none; }
    70%     { box-shadow: 0 0 0 8px rgba(0,255,135,0); }
}

/* ── LANDING ─────────────────────────────────────────── */
.landing-hero {
    text-align: center;
    padding: 5rem 2rem;
    animation: card-enter 0.8s cubic-bezier(0.23,1,0.32,1) both;
}
.landing-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 4.5rem;
    font-weight: 700;
    letter-spacing: 8px;
    text-transform: uppercase;
    background: linear-gradient(135deg, var(--cyan) 0%, #0077ff 40%, var(--green) 100%);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradient-shift 5s ease infinite;
    margin-bottom: 1rem;
}
@keyframes gradient-shift {
    0%,100% { background-position: 0% 50%; }
    50%     { background-position: 100% 50%; }
}
.landing-sub {
    font-size: 1.1rem;
    color: var(--muted);
    max-width: 500px;
    margin: 0 auto 3rem;
    line-height: 1.7;
}
.landing-steps {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    flex-wrap: wrap;
    max-width: 950px;
    margin: 0 auto;
}
.landing-step {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.8rem 1.5rem;
    width: 220px;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.23,1,0.32,1);
    animation: card-enter 0.6s cubic-bezier(0.23,1,0.32,1) both;
    position: relative;
    overflow: hidden;
}
.landing-step:nth-child(1) { animation-delay: 0.1s; }
.landing-step:nth-child(2) { animation-delay: 0.2s; }
.landing-step:nth-child(3) { animation-delay: 0.3s; }
.landing-step:nth-child(4) { animation-delay: 0.4s; }
.landing-step:hover {
    border-color: var(--cyan);
    box-shadow: 0 0 30px rgba(0,212,255,0.12), 0 20px 40px rgba(0,0,0,0.3);
    transform: translateY(-6px);
}
.step-num {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: var(--cyan);
    line-height: 1;
    margin-bottom: 0.5rem;
}
.step-title { font-weight: 600; color: var(--text); margin-bottom: 0.3rem; font-size: 0.95rem; }
.step-desc  { font-size: 0.82rem; color: var(--muted); }

/* ── SHIFT CARDS ─────────────────────────────────────── */
.shift-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    text-align: center;
    transition: all 0.25s;
}
.shift-card:hover { border-color: var(--cyan); transform: translateY(-2px); }
.shift-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--cyan);
    margin-bottom: 0.2rem;
}
.shift-time { font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: var(--muted); margin-bottom: 0.8rem; }
.shift-stat { font-size: 0.85rem; color: #a0b8d0; margin-bottom: 0.2rem; }
.shift-stat b { color: var(--text); }

/* ── SIM RESULTS ─────────────────────────────────────── */
.sim-result {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.5rem;
    text-align: center;
    transition: border-color 0.25s, transform 0.25s;
}
.sim-result:hover { border-color: rgba(0,212,255,0.3); transform: translateY(-2px); }
.sim-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.6rem;
    font-weight: 700;
    line-height: 1;
}

/* ── MISC ────────────────────────────────────────────── */
.sidebar-brand {
    background: linear-gradient(135deg, #0d1e35 0%, #0a1525 100%);
    border-bottom: 1px solid var(--border);
    padding: 1.2rem 1rem;
    margin: -1rem -1rem 1rem -1rem;
    position: relative;
    overflow: hidden;
}
.sidebar-brand::after {
    content: '';
    position: absolute;
    bottom: 0; left: -100%;
    width: 50%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
    animation: topbar-scan 3s linear infinite;
}
.sidebar-brand-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: 3px;
    color: var(--cyan);
    text-transform: uppercase;
}
.sidebar-brand-sub { font-size: 0.72rem; color: var(--dimmed); letter-spacing: 1px; }

hr { border-color: var(--border) !important; }
.stProgress > div > div > div { background: var(--cyan) !important; }
.stAlert { background: var(--card) !important; border: 1px solid var(--border) !important; color: #a0b8d0 !important; }
.js-plotly-plot .plotly, .js-plotly-plot .plotly * { font-family: 'IBM Plex Sans', sans-serif; }

/* ── STAT ROW ────────────────────────────────────────── */
.stat-row-item {
    transition: all 0.25s;
    border-radius: 8px;
    padding: 0.5rem 0.8rem;
}
.stat-row-item:hover { background: rgba(0,212,255,0.05); }

/* ── SCROLLBAR ───────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--navy); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2a5a8f; }

/* ── FAILURE DRIVER CARDS ────────────────────────────── */
.driver-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--cyan);
    border-radius: 8px;
    padding: 0.8rem 1.2rem;
    margin-bottom: 0.5rem;
    animation: slide-in-left 0.4s cubic-bezier(0.23,1,0.32,1) both;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="fiq-bg"></div>', unsafe_allow_html=True)


with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-title">⚡ FactoryIQ</div>
        <div class="sidebar-brand-sub">AI OPERATIONS ADVISOR</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("##### 🏭 Factory Profile")
    factory_name  = st.text_input("Factory name", "My Factory")
    factory_type  = st.selectbox("Factory type", list(FACTORY_PRESETS.keys()))
    preset        = FACTORY_PRESETS[factory_type]
    currency_name = st.selectbox("Currency", list(CURRENCIES.keys()), index=0)
    currency      = CURRENCIES[currency_name]
    sym           = currency["symbol"]

    st.markdown("---")
    st.markdown("##### ⚙️ Operations Data")

    col_m, col_w = st.columns(2)
    with col_m:
        machines = st.number_input("Machines", min_value=1, max_value=500, value=preset["machines"])
    with col_w:
        workers = st.number_input("Workers", min_value=1, max_value=1000, value=preset["workers"])

    hours = st.slider("Shift hours / day", 4, 24, preset["hours"])

    st.markdown("**Costs & Prices**")
    p_price  = st.number_input(f"Selling price / unit ({sym})", value=preset["product_price"], step=5.0)
    mat_cost = st.number_input(f"Material cost / unit ({sym})", value=preset["material_cost"], step=1.0)

    col_e, col_wc = st.columns(2)
    with col_e:
        e_cost = st.number_input(f"Energy {sym}/kWh", value=preset["energy_cost"], step=0.01, format="%.3f")
    with col_wc:
        w_cost = st.number_input(f"Wage {sym}/day", value=preset["worker_daily_cost"], step=5.0)

    st.markdown("---")
    st.markdown("##### 📡 Market Conditions")
    data_mode = st.radio("Source", ["🌐 Live APIs", "✏️ Manual"], horizontal=True)
    api_data  = st.session_state.get("api_data", None)

    if data_mode == "🌐 Live APIs":
        city          = st.selectbox("Factory location", list(CITY_COORDINATES.keys()))
        material_type = st.selectbox("Primary material", ["mixed", "aluminum", "copper", "steel"])
        if CITY_COORDINATES.get(city):
            lat, lon = CITY_COORDINATES[city]
        else:
            lat = st.number_input("Latitude",  value=48.85, format="%.4f")
            lon = st.number_input("Longitude", value=2.35,  format="%.4f")

        if st.button("🔄 Fetch Live Data", use_container_width=True):
            with st.spinner("Connecting to live APIs…"):
                try:
                    fetched = fetch_all(lat=lat, lon=lon, factory_material=material_type)
                    st.session_state["api_data"] = fetched
                    api_data = fetched
                    st.success("✅ Live data loaded")
                except Exception as e:
                    st.warning(f"Fetch failed: {e}")

        if api_data:
            m = api_data["multipliers"]
            st.caption(f"🌡️ **{m.get('temp_celsius','?')}°C**  ⚡ **{m.get('energy_cost_multiplier','?')}x**  📦 **{m.get('demand_multiplier','?')}x**")

        m             = api_data["multipliers"] if api_data else {}
        demand_mult   = st.slider("Demand tune",    0.3, 2.0, float(m.get("demand_multiplier",          1.0)), 0.05)
        energy_mult   = st.slider("Energy tune",    0.5, 3.0, float(m.get("energy_cost_multiplier",     1.0)), 0.05)
        material_mult = st.slider("Materials tune", 0.5, 3.0, float(m.get("material_cost_multiplier",   1.0)), 0.05)
    else:
        demand_mult   = st.select_slider("Customer demand",
            options=[0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.8,2.0], value=1.0,
            format_func=lambda x: f"{'🔻 Very Low' if x<=0.6 else '📉 Low' if x<=0.8 else '✅ Normal' if x<=1.2 else '📈 High' if x<=1.5 else '🚀 Very High'} ({x}x)")
        energy_mult   = st.select_slider("Energy prices",
            options=[0.5,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.5,1.7,2.0,2.5,3.0], value=1.0,
            format_func=lambda x: f"{'✅ Normal' if x<=1.1 else '⚠️ Elevated' if x<=1.5 else '🔴 Very High'} ({x}x)")
        material_mult = st.select_slider("Material costs",
            options=[0.5,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.5,1.7,2.0,2.5], value=1.0,
            format_func=lambda x: f"{'✅ Normal' if x<=1.1 else '⚠️ Elevated' if x<=1.5 else '🔴 Very High'} ({x}x)")

    st.markdown("---")
    st.markdown("##### 📂 Machine Data (Optional)")
    st.caption("Upload any sensor CSV — columns auto-detected")
    uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

    st.markdown("---")
    run_btn = st.button("⚡  ANALYSE MY FACTORY", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️  Clear Model Cache", use_container_width=True):
        cache_dir = os.path.join(os.path.dirname(__file__), ".model_cache")
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            st.sidebar.success("✅ Cache cleared — next run retrains from scratch.")
        else:
            st.sidebar.info("Cache is already empty.")


factory_inputs = {
    "machines":              machines,
    "workers":               workers,
    "hours":                 hours,
    "product_price":         p_price,
    "material_cost":         mat_cost,
    "energy_cost":           e_cost,
    "worker_daily_cost":     w_cost,
    "production_rate":       preset.get("production_rate",       10.0),
    "energy_kw_per_machine": preset.get("energy_kw_per_machine", 15.0),
}
market_inputs = {
    "demand_multiplier":        demand_mult,
    "energy_cost_multiplier":   energy_mult,
    "material_cost_multiplier": material_mult,
}

dataset_stats  = None
column_mapping = None
uploaded_df    = None

if uploaded:
    try:
        from data_adapter import detect_columns, adapt_dataset
        uploaded.seek(0)
        uploaded_df = pd.read_csv(uploaded)
        uploaded_df.columns = uploaded_df.columns.str.strip()
        auto_map   = detect_columns(uploaded_df)
        detected   = {k: v for k, v in auto_map.items() if v is not None}
        missing    = [k for k, v in auto_map.items() if v is None]
        confidence = len(detected) / max(1, len(auto_map))
        st.sidebar.success(f"✅ {len(uploaded_df):,} records — {int(confidence*100)}% confidence")
        if missing:
            with st.sidebar.expander("⚙️ Fix column mapping"):
                all_cols = ["(not available)"] + uploaded_df.columns.tolist()
                for feat in missing:
                    chosen = st.selectbox(f"{feat}", all_cols, key=f"map_{feat}")
                    if chosen != "(not available)":
                        auto_map[feat] = chosen
        column_mapping = auto_map
        adapted        = adapt_dataset(uploaded_df, column_mapping)
        dataset_stats  = adapted["adapted_stats"]
    except Exception as e:
        st.sidebar.error(f"Could not read file: {e}")


# ── Landing page (no analysis yet) ───────────────────────────────────────────
if not run_btn and "fiq_cache" not in st.session_state:
    st.markdown(f"""
    <div class="landing-hero">
        <div class="landing-title">FactoryIQ</div>
        <div class="landing-sub">
            Your AI operations advisor. Enter your factory parameters on the left
            and get a full risk analysis, OEE score, action plan, and profit impact — in seconds.
        </div>
        <div class="landing-steps">
            <div class="landing-step">
                <div class="step-num">01</div>
                <div class="step-title">Configure Your Factory</div>
                <div class="step-desc">Enter machines, workers, costs and today's market conditions in the sidebar.</div>
            </div>
            <div class="landing-step">
                <div class="step-num">02</div>
                <div class="step-title">AI Analyses Everything</div>
                <div class="step-desc">GBM + RL models score 7 risk categories and compute your OEE score.</div>
            </div>
            <div class="landing-step">
                <div class="step-num">03</div>
                <div class="step-title">Get Your Action Plan</div>
                <div class="step-desc">Prioritised actions with exact {sym} impact, shift plan, and PDF report.</div>
            </div>
            <div class="landing-step">
                <div class="step-num">04</div>
                <div class="step-title">Simulate What-Ifs</div>
                <div class="step-desc">Test "what if energy doubles?" or "what if 3 machines go down?" instantly.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── Analysis ──────────────────────────────────────────────────────────────────
if run_btn:
    with st.spinner("🤖 Training AI models and running analysis…"):
        engine       = MLEngine()
        ml_info      = engine.train(factory_inputs, df=uploaded_df, column_mapping=column_mapping, episodes=800)
        ml_rec       = engine.recommend(factory_inputs, market_inputs)
        risk_result  = score_risks(factory_inputs, market_inputs, dataset_stats)
        oee_data     = calculate_oee(factory_inputs, market_inputs, dataset_stats,
                                      machine_speed=ml_rec.get("machine_speed", 1.0))
        prod_targets = calculate_production_targets(factory_inputs, market_inputs, dataset_stats)
        shift_plan   = calculate_shift_plan(factory_inputs, market_inputs, dataset_stats)
        actions      = generate_action_plan(risk_result["risks"], factory_inputs, market_inputs, dataset_stats, ml_recommendation=ml_rec)
        profit_comp  = compare_with_without_plan(factory_inputs, market_inputs, actions, dataset_stats,
                                                  ml_recommendation=ml_rec)

        if "history_db" not in st.session_state:
            st.session_state["history_db"] = HistoryDB()
        st.session_state["history_db"].save_session(
            risk_result, oee_data, profit_comp,
            factory_name=factory_name,
            industry=factory_type,
            market_inputs=market_inputs,
        )

        st.session_state["fiq_cache"] = dict(
            engine=engine, ml_info=ml_info, ml_rec=ml_rec,
            risk_result=risk_result, oee_data=oee_data,
            prod_targets=prod_targets, shift_plan=shift_plan,
            actions=actions, profit_comp=profit_comp,
            factory_inputs=factory_inputs, market_inputs=market_inputs,
            factory_name=factory_name, factory_type=factory_type,
            currency=currency, sym=sym,
            machines=machines, workers=workers, hours=hours,
            p_price=p_price, mat_cost=mat_cost,
            e_cost=e_cost, w_cost=w_cost,
            demand_mult=demand_mult, energy_mult=energy_mult,
            material_mult=material_mult,
        )

        for _k in ("sim_d", "sim_e", "sim_m", "sim_sp", "sim_wk", "sim_md"):
            if _k in st.session_state:
                del st.session_state[_k]


_c           = st.session_state["fiq_cache"]
engine       = _c["engine"]
ml_info      = _c["ml_info"]
ml_rec       = _c["ml_rec"]
risk_result  = _c["risk_result"]
oee_data     = _c["oee_data"]
prod_targets = _c["prod_targets"]
shift_plan   = _c["shift_plan"]
actions      = _c["actions"]
profit_comp  = _c["profit_comp"]
factory_inputs  = _c["factory_inputs"]
market_inputs   = _c["market_inputs"]
factory_name    = _c["factory_name"]
factory_type    = _c["factory_type"]
currency        = _c["currency"]
sym             = _c["sym"]
machines        = _c["machines"]
workers         = _c["workers"]
hours           = _c["hours"]
p_price         = _c["p_price"]
mat_cost        = _c["mat_cost"]
e_cost          = _c["e_cost"]
w_cost          = _c["w_cost"]
demand_mult     = _c["demand_mult"]
energy_mult     = _c["energy_mult"]
material_mult   = _c["material_mult"]

now  = datetime.datetime.now()
diff = profit_comp["difference"]
pct  = profit_comp["improvement_pct"]

overall        = risk_result["overall_level"]
risk_color_map = {"low": "#00ff87", "medium": "#f59e0b", "high": "#ff6b35", "critical": "#ff4757"}
rc             = risk_color_map[overall]

gain_color  = "#00ff87" if diff >= 0 else "#ff4757"
gain_prefix = "+" if diff >= 0 else ""

st.markdown(f"""
<div class="topbar">
    <div>
        <div class="topbar-logo">⚡ FactoryIQ</div>
        <div style="font-size:0.75rem;color:#3a5a7a;letter-spacing:1px;margin-top:2px;">AI OPERATIONS ADVISOR</div>
    </div>
    <div style="display:flex;gap:2rem;align-items:center;flex-wrap:wrap;">
        <div class="stat-row-item" style="text-align:center;">
            <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:1px;color:#3a5a7a;">Factory</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.05rem;font-weight:700;color:#c8d8e8;">{factory_name}</div>
        </div>
        <div class="stat-row-item" style="text-align:center;">
            <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:1px;color:#3a5a7a;">OEE</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.05rem;font-weight:700;color:{oee_data['status_color']};
                        animation:num-pop 0.5s 0.4s both;">{oee_data['oee']}%</div>
        </div>
        <div class="stat-row-item" style="text-align:center;">
            <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:1px;color:#3a5a7a;">Risk</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.05rem;font-weight:700;color:{rc};
                        animation:num-pop 0.5s 0.5s both;">{overall.upper()}</div>
        </div>
        <div class="stat-row-item" style="text-align:center;">
            <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:1px;color:#3a5a7a;">AI Gain</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.05rem;font-weight:700;color:{gain_color};
                        animation:num-pop 0.5s 0.6s both;">{gain_prefix}{sym}{diff:,.0f}</div>
        </div>
        <div class="stat-row-item" style="text-align:center;">
            <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:1px;color:#3a5a7a;">Health</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.05rem;font-weight:700;color:{rc};
                        animation:num-pop 0.5s 0.7s both;">{risk_result['health_score']}/100</div>
        </div>
        <div style="text-align:right;padding-left:1rem;border-left:1px solid #1a3a5f;">
            <div style="font-size:0.72rem;color:#3a5a7a;letter-spacing:1px;">
                <span class="live-dot"></span>LIVE
            </div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#5a7a9a;margin-top:2px;" id="fiq-clock">
                {now.strftime('%H:%M — %d %b %Y')}
            </div>
        </div>
    </div>
</div>

<script>
(function() {{
    function tick() {{
        var el = document.getElementById('fiq-clock');
        if (el) {{
            var n = new Date();
            var pad = function(x) {{ return x < 10 ? '0'+x : x; }};
            var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
            el.textContent = pad(n.getHours()) + ':' + pad(n.getMinutes()) + ':' + pad(n.getSeconds()) + ' — ' + n.getDate() + ' ' + months[n.getMonth()] + ' ' + n.getFullYear();
        }}
    }}
    tick();
    setInterval(tick, 1000);
}})();
</script>
""", unsafe_allow_html=True)


tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊  Dashboard",
    "⚠️  Risk Analysis",
    "🎯  Action Plan",
    "🔮  What-If Simulator",
    "📋  Production Planning",
    "🏭  Industry Intelligence",
    "📈  History",
])


with tab1:
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        oee_color = oee_data["status_color"]
        st.markdown(f"""
        <div class="metric-card" style="--accent:{oee_color};">
            <div class="metric-label">OEE Score</div>
            <div class="metric-value">{oee_data['oee']}%</div>
            <div class="metric-sub">{oee_data['status']}</div>
            <div class="oee-bar-container" style="margin-top:0.7rem;">
                <div class="oee-bar-fill" style="width:{oee_data['oee']}%;background:{oee_color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        p_color = "#00ff87" if diff >= 0 else "#ff4757"
        st.markdown(f"""
        <div class="metric-card" style="--accent:{p_color};">
            <div class="metric-label">AI Profit Gain Today</div>
            <div class="metric-value">{gain_prefix}{sym}{abs(diff):,.0f}</div>
            <div class="metric-sub">{pct:+.1f}% vs no plan &nbsp;·&nbsp; {sym}{profit_comp['profit_with']:,.0f} with plan</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        health_score = risk_result["health_score"]
        st.markdown(f"""
        <div class="metric-card" style="--accent:{rc};">
            <div class="metric-label">Factory Health</div>
            <div class="metric-value" style="color:{rc};">{health_score}<span style="font-size:1.2rem;">/100</span></div>
            <div class="metric-sub">
                🔴 {risk_result['critical_count']} critical &nbsp;
                🟠 {risk_result['high_count']} high &nbsp;
                🟡 {risk_result['medium_count']} med
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        on_track_color = "#00ff87" if prod_targets["on_track"] else "#ff4757"
        on_track_label = "On Track ✅" if prod_targets["on_track"] else "Behind Target ⚠️"
        st.markdown(f"""
        <div class="metric-card" style="--accent:{on_track_color};">
            <div class="metric-label">Production Target</div>
            <div class="metric-value" style="color:{on_track_color};">{prod_targets['projected_units']:,}</div>
            <div class="metric-sub">{on_track_label} · break-even at {prod_targets['breakeven_units']:,} units</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_oee, col_profit = st.columns([1.1, 1])

    with col_oee:
        st.markdown('<div class="section-header">OEE Breakdown</div>', unsafe_allow_html=True)

        def svg_arc_gauge(value, label, color, delay=0):
            pct   = max(0, min(100, value))
            r     = 54
            cx, cy = 64, 68
            circ  = 2 * 3.14159 * r
            half  = circ / 2
            fill  = (pct / 100) * half
            gap   = half - fill
            if pct >= 85:   status_col = "#00ff87"
            elif pct >= 70: status_col = "#00d4ff"
            elif pct >= 50: status_col = color
            else:           status_col = "#ff4757"
            return f"""
            <div style="flex:1;text-align:center;padding:0 0.5rem;">
              <svg viewBox="0 0 128 80" style="width:100%;max-width:160px;overflow:visible;">
                <path d="M {cx-r} {cy} A {r} {r} 0 0 1 {cx+r} {cy}"
                      fill="none" stroke="#0d2040" stroke-width="10" stroke-linecap="round"/>
                <path d="M {cx-r} {cy} A {r} {r} 0 0 1 {cx+r} {cy}"
                      fill="none" stroke="{color}" stroke-width="10" stroke-linecap="round"
                      stroke-dasharray="{fill} {gap + half}"
                      style="filter:drop-shadow(0 0 6px {color}88);"/>
                <circle cx="{cx}" cy="{cy}" r="3"
                        fill="{color}" style="filter:drop-shadow(0 0 4px {color});"/>
                <text x="{cx}" y="{cy - 10}" text-anchor="middle"
                      font-family="Rajdhani,sans-serif" font-size="22" font-weight="700"
                      fill="{status_col}">{pct:.0f}%</text>
              </svg>
              <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:2px;
                          color:{color};font-weight:600;margin-top:-4px;">{label}</div>
              <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#3a5a7a;margin-top:2px;">
                  target: {'90' if label=='AVAILABILITY' else '95' if label=='PERFORMANCE' else '99'}%+
              </div>
            </div>"""

        gauges_html = f"""
        <div style="background:#0d1627;border:1px solid #1a3a5f;border-radius:12px;
                    padding:1.2rem 0.5rem 0.8rem;display:flex;justify-content:space-around;
                    align-items:flex-end;gap:0.5rem;">
            {svg_arc_gauge(oee_data['availability'], 'AVAILABILITY', '#00d4ff', 0.0)}
            {svg_arc_gauge(oee_data['performance'],  'PERFORMANCE',  '#f59e0b', 0.15)}
            {svg_arc_gauge(oee_data['quality'],      'QUALITY',      '#00ff87', 0.30)}
        </div>
        """
        components.html(gauges_html, height=220)

        st.markdown("""
        <div style="display:flex;gap:2rem;justify-content:center;margin-top:0.6rem;flex-wrap:wrap;">
            <span style="font-size:0.72rem;color:#3a5a7a;">
                <span style="color:#00d4ff;">Availability</span> = % uptime
            </span>
            <span style="font-size:0.72rem;color:#3a5a7a;">
                <span style="color:#f59e0b;">Performance</span> = actual vs rated speed
            </span>
            <span style="font-size:0.72rem;color:#3a5a7a;">
                <span style="color:#00ff87;">Quality</span> = good units / total
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col_profit:
        st.markdown('<div class="section-header">Daily Profit Comparison</div>', unsafe_allow_html=True)

        bar_colors = ["#1a3a5f", "#00d4ff" if diff >= 0 else "#ff4757"]
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(
            x=["Without AI Plan", "With AI Plan"],
            y=[profit_comp["profit_without"], profit_comp["profit_with"]],
            marker_color=bar_colors, marker_line_width=0,
            text=[f"{sym}{profit_comp['profit_without']:,.0f}", f"{sym}{profit_comp['profit_with']:,.0f}"],
            textposition="outside",
            textfont={"color": "#c8d8e8", "family": "Rajdhani", "size": 14}
        ))
        fig_p.update_layout(
            paper_bgcolor="#0d1627", plot_bgcolor="#0d1627",
            height=220, margin=dict(t=20, b=10, l=10, r=10),
            yaxis={"visible": False, "gridcolor": "#1a3a5f"},
            xaxis={"tickfont": {"color": "#a0b8d0", "size": 12, "family": "Rajdhani"}},
            bargap=0.4, showlegend=False
        )
        st.plotly_chart(fig_p, use_container_width=True)

        labels        = ["Materials", "Energy", "Labour", "Net Profit"]
        workers_cost  = workers * w_cost
        energy_exp    = machines * hours * 5 * e_cost * energy_mult
        mat_exp       = prod_targets["projected_units"] * mat_cost * material_mult
        total_rev     = prod_targets["daily_revenue_proj"]
        net_profit    = max(0, total_rev - mat_exp - energy_exp - workers_cost)
        values        = [max(0, mat_exp), max(0, energy_exp), max(0, workers_cost), max(0, net_profit)]
        donut_colors  = ["#1a3a5f", "#f59e0b", "#2a5a8f", "#00ff87"]

        fig_d = go.Figure(go.Pie(
            labels=labels, values=values, hole=0.65,
            marker={"colors": donut_colors, "line": {"color": "#060b14", "width": 2}},
            textfont={"size": 10, "family": "IBM Plex Sans", "color": "#a0b8d0"},
            hovertemplate="<b>%{label}</b><br>" + sym + "%{value:,.0f}<extra></extra>"
        ))
        fig_d.update_layout(
            paper_bgcolor="#0d1627", plot_bgcolor="#0d1627",
            height=200, margin=dict(t=5, b=5, l=5, r=5),
            showlegend=True,
            legend={"font": {"color": "#a0b8d0", "size": 10, "family": "IBM Plex Sans"}, "bgcolor": "rgba(0,0,0,0)"},
            annotations=[{"text": "Cost<br>Split", "font": {"size": 11, "color": "#5a7a9a", "family": "IBM Plex Sans"},
                          "showarrow": False, "x": 0.5, "y": 0.5}]
        )
        st.plotly_chart(fig_d, use_container_width=True)

    st.markdown('<div class="section-header">Machine Health Grid</div>', unsafe_allow_html=True)

    failure_rate = dataset_stats.get("failure_rate", 0.034) if dataset_stats else 0.034
    tool_wear_v  = dataset_stats.get("avg_tool_wear", 108)   if dataset_stats else 108

    machine_statuses = []
    seed_val = int(failure_rate * 1000) + machines
    random.seed(seed_val)
    for i in range(machines):
        h = (i * 2654435761) % (2**32)
        r = (h / 2**32 + random.random()) / 2
        if r < failure_rate * 1.5:
            machine_statuses.append(("critical", f"M{i+1}"))
        elif r < failure_rate * 4 or tool_wear_v > 160:
            machine_statuses.append(("warn", f"M{i+1}"))
        elif r < 0.05:
            machine_statuses.append(("off", f"M{i+1}"))
        else:
            machine_statuses.append(("ok", f"M{i+1}"))

    grid_html = '<div class="machine-grid">'
    for idx, (status, label) in enumerate(machine_statuses):
        css_class  = f"machine-{status}"
        tooltip    = {"ok": "Running ✅", "warn": "⚠️ Needs attention", "critical": "🔴 Risk of failure", "off": "⚫ Idle/Off"}[status]
        delay      = f"animation-delay:{idx * 0.025:.2f}s"
        grid_html += f'<div class="machine-dot {css_class}" title="{tooltip}" style="{delay}">{label}</div>'
    grid_html += "</div>"

    ok_count       = sum(1 for s, _ in machine_statuses if s == "ok")
    warn_count     = sum(1 for s, _ in machine_statuses if s == "warn")
    critical_count = sum(1 for s, _ in machine_statuses if s == "critical")
    off_count      = sum(1 for s, _ in machine_statuses if s == "off")

    st.markdown(f"""
    <div style="background:#0d1627;border:1px solid #1a3a5f;border-radius:14px;padding:1.4rem 1.6rem;
                animation:card-enter 0.6s 0.2s both;">
        <div style="display:flex;gap:2rem;margin-bottom:0.8rem;flex-wrap:wrap;align-items:center;">
            <span style="font-size:0.78rem;color:#5a7a9a;">
                <span style="color:#00ff87;font-weight:700;font-size:0.9rem;">{ok_count}</span> Running
            </span>
            <span style="font-size:0.78rem;color:#5a7a9a;">
                <span style="color:#f59e0b;font-weight:700;font-size:0.9rem;">{warn_count}</span> Warning
            </span>
            <span style="font-size:0.78rem;color:#5a7a9a;">
                <span style="color:#ff4757;font-weight:700;font-size:0.9rem;">{critical_count}</span> Critical
            </span>
            <span style="font-size:0.78rem;color:#5a7a9a;">
                <span style="color:#5a7a9a;font-weight:700;font-size:0.9rem;">{off_count}</span> Idle
            </span>
            <span style="font-size:0.72rem;color:#3a5a7a;margin-left:auto;
                         font-family:'IBM Plex Mono',monospace;">Hover = status</span>
        </div>
        {grid_html}
    </div>
    """, unsafe_allow_html=True)


# ── TAB 2: Risk Analysis ──────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">7-Category Risk Scorecard</div>', unsafe_allow_html=True)

    level_badge        = {"low": "badge-low", "medium": "badge-medium", "high": "badge-high", "critical": "badge-critical"}
    level_color        = {"low": "#00ff87", "medium": "#f59e0b", "high": "#ff6b35", "critical": "#ff4757"}
    level_action_label = {
        "low":      "✅ All good — no action needed",
        "medium":   "⚠️ Monitor closely — consider acting this week",
        "high":     "🔴 Act today — this is costing you money",
        "critical": "🚨 Act immediately — serious risk of losses",
    }

    col_risks_left, col_risks_right = st.columns(2)

    for i, r in enumerate(risk_result["risks"]):
        lvl      = r["level"]
        col      = col_risks_left if i % 2 == 0 else col_risks_right
        pct_fill = min(100, round((r["raw_value"] / max(0.001, r["max_value"])) * 100))

        with col:
            st.markdown(f"""
            <div class="risk-card risk-{lvl}">
                <div style="flex:1;">
                    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.4rem;">
                        <span style="font-size:1.2rem;">{r['icon']}</span>
                        <span style="font-family:'Rajdhani',sans-serif;font-size:1rem;font-weight:700;color:#e0eaf5;">{r['name']}</span>
                        <span class="risk-level-badge {level_badge[lvl]}">{lvl.upper()}</span>
                        <span style="font-family:'IBM Plex Mono',monospace;font-size:0.8rem;color:{level_color[lvl]};margin-left:auto;font-weight:600;">{r['value']}</span>
                    </div>
                    <div style="font-size:0.85rem;color:#7a9ab8;margin-bottom:0.4rem;">{r['description']}</div>
                    <div class="oee-bar-container">
                        <div class="oee-bar-fill" style="width:{pct_fill}%;background:{level_color[lvl]};"></div>
                    </div>
                    <div style="margin-top:0.6rem;font-size:0.8rem;">
                        <span style="color:{level_color[lvl]};font-weight:600;">{level_action_label[lvl]}</span>
                    </div>
                    <div style="margin-top:0.4rem;font-size:0.78rem;color:#5a7a9a;font-style:italic;">
                        💡 {r.get('fix','—')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Risk Radar</div>', unsafe_allow_html=True)
    scores_map    = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    radar_values  = [scores_map[r["level"]] for r in risk_result["risks"]]
    radar_labels  = [r["name"] for r in risk_result["risks"]]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=radar_values + [radar_values[0]],
        theta=radar_labels + [radar_labels[0]],
        fill="toself",
        fillcolor=f"rgba({','.join(str(int(level_color[overall].lstrip('#')[i:i+2], 16)) for i in (0,2,4))}, 0.10)",
        line={"color": level_color[overall], "width": 2},
        name="Risk Level"
    ))
    fig_radar.update_layout(
        polar={
            "bgcolor": "#060b14",
            "radialaxis": {"range": [0, 4], "visible": True, "tickmode": "array", "tickvals": [1,2,3,4],
                           "ticktext": ["Low","Med","High","Crit"], "tickfont": {"color": "#3a5a7a", "size": 9},
                           "gridcolor": "#1a3a5f", "linecolor": "#1a3a5f"},
            "angularaxis": {"tickfont": {"color": "#a0b8d0", "size": 10, "family": "IBM Plex Sans"},
                            "gridcolor": "#1a3a5f", "linecolor": "#1a3a5f"}
        },
        paper_bgcolor="#0d1627",
        font={"color": "#a0b8d0"},
        height=380, margin=dict(t=30, b=30, l=40, r=40),
        showlegend=False
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ── AI Failure Drivers ────────────────────────────────────────────
    drivers = engine.get_failure_drivers(n=3)
    if drivers:
        st.markdown('<div class="section-header">🤖 AI Failure Drivers</div>', unsafe_allow_html=True)
        for driver in drivers:
            st.markdown(f"""
            <div class="driver-card">
                <span style="font-family:'IBM Plex Mono',monospace;font-size:0.85rem;color:#00d4ff;">
                    {driver}
                </span>
            </div>
            """, unsafe_allow_html=True)


# ── TAB 3: Action Plan ────────────────────────────────────────────────────────
with tab3:
    urgent_count = sum(1 for a in actions if a["priority"] == 1)
    today_count  = sum(1 for a in actions if a["priority"] == 2)
    total_save   = sum(a["saving"] for a in actions if a["saving"] > 0)

    st.markdown(f"""
    <div style="background:#0d1627;border:1px solid #1a3a5f;border-radius:14px;
                padding:1.4rem 2rem;display:flex;gap:3rem;align-items:center;margin-bottom:1.5rem;
                flex-wrap:wrap;animation:card-enter 0.5s both;position:relative;overflow:hidden;">
        <div style="position:absolute;inset:0;pointer-events:none;
                    background:linear-gradient(135deg,rgba(255,71,87,0.03),transparent 50%,rgba(0,212,255,0.03));"></div>
        <div>
            <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:2px;color:#5a7a9a;">Urgent Now</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:2.2rem;font-weight:700;color:#ff4757;
                        animation:num-pop 0.5s 0.2s both;">{urgent_count}</div>
        </div>
        <div>
            <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:2px;color:#5a7a9a;">Do Today</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:2.2rem;font-weight:700;color:#f59e0b;
                        animation:num-pop 0.5s 0.3s both;">{today_count}</div>
        </div>
        <div>
            <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:2px;color:#5a7a9a;">Total AI Savings</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:2.2rem;font-weight:700;color:#00ff87;
                        animation:num-pop 0.5s 0.4s both;">{sym}{total_save:,.0f}</div>
        </div>
        <div style="margin-left:auto;background:#060b14;border:1px solid #1a3a5f;border-radius:10px;
                    padding:0.8rem 1.3rem;">
            <div style="font-size:0.68rem;color:#5a7a9a;text-transform:uppercase;letter-spacing:1px;">🤖 AI Model</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.78rem;color:#00d4ff;margin-top:0.2rem;">
                GBM ({ml_info['gbm']['failure_accuracy']}% acc) + RL ({ml_info['rl']['episodes']:,} eps)
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    urgency_config = {
        1: ("URGENT — DO THIS NOW", "#ff4757", "action-urgent"),
        2: ("DO TODAY",             "#f59e0b", "action-today"),
        3: ("KEEP IN MIND",         "#00ff87", "action-monitor"),
    }

    if not actions:
        st.markdown("""
        <div style="background:#0d1627;border:1px solid #1a3a5f;border-radius:12px;
                    padding:3rem;text-align:center;color:#5a7a9a;animation:card-enter 0.5s both;">
            <div style="font-size:2rem;margin-bottom:0.5rem;">✅</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.3rem;color:#00ff87;">All Systems Nominal</div>
            <div style="margin-top:0.5rem;">Your factory is running optimally under current conditions.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for i, action in enumerate(actions):
            p = action["priority"]
            urgency_label, urgency_color, card_css = urgency_config.get(p, urgency_config[3])
            saving_text = f"+{sym}{action['saving']:,.0f} saved/earned" if action["saving"] > 0 else "— Long-term health"
            ml_badge = (' <span style="background:#0d1e35;color:#00d4ff;font-size:0.63rem;padding:0.1rem 0.45rem;'
                        'border-radius:3px;border:1px solid #1a3a5f;letter-spacing:0.5px;">ML</span>'
                        if action.get("ml_powered") else "")
            st.markdown(f"""
            <div class="action-card {card_css}" style="animation-delay:{i*0.07}s;">
                <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;">
                    <div style="flex:1;">
                        <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;
                                    color:{urgency_color};margin-bottom:0.4rem;">{urgency_label}{ml_badge}</div>
                        <div class="action-title">{action['icon']} {action['title']}</div>
                        <div class="action-detail">{action['detail']}</div>
                    </div>
                    <div style="text-align:right;min-width:130px;">
                        <div class="action-saving" style="color:{urgency_color};">{saving_text}</div>
                        <div style="font-size:0.67rem;color:#3a5a7a;margin-top:0.3rem;
                                    font-family:'IBM Plex Mono',monospace;">PRIORITY #{p}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.spinner("Preparing PDF report…"):
        pdf = generate_report(
            factory_name, factory_type, risk_result, actions, profit_comp, market_inputs,
            currency_symbol=sym,
            oee_data=oee_data,
            shift_plan=shift_plan,
            prod_targets=prod_targets,
        )

    st.download_button(
        "📄  Download Full PDF Report",
        data=pdf,
        file_name=f"{factory_name.replace(' ','_')}_{now.strftime('%Y-%m-%d')}_briefing.pdf",
        mime="application/pdf",
        use_container_width=True
    )


# ── TAB 4: What-If Simulator ──────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-header">Scenario Simulator — Instant Profit Impact</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.85rem;color:#5a7a9a;margin-bottom:1.5rem;">
        Change any parameter below and see the profit impact <b style="color:#00d4ff;">instantly</b> — no re-training needed.
    </div>
    """, unsafe_allow_html=True)

    col_sim_l, col_sim_r = st.columns([1, 1])

    with col_sim_l:
        st.markdown("**Market Scenarios**")
        sim_demand   = st.slider("📦 Customer demand",  0.2, 2.5, demand_mult,           0.05, key="sim_d")
        sim_energy   = st.slider("⚡ Energy cost",      0.4, 4.0, energy_mult,            0.05, key="sim_e")
        sim_material = st.slider("🏗️ Material cost",   0.4, 3.5, material_mult,          0.05, key="sim_m")
        st.markdown("**Operations**")
        sim_speed         = st.slider("🚀 Machine speed",             0.4, 1.8, ml_rec["machine_speed"],    0.05, key="sim_sp")
        sim_workers       = st.slider("👷 Active workers",            int(workers * 0.3), workers, int(ml_rec["workers_active"]), 1, key="sim_wk")
        sim_machines_down = st.slider("🔧 Machines down (breakdown)", 0, max(1, machines // 2), 0, 1, key="sim_md")

    with col_sim_r:
        effective_machines = max(1, machines - sim_machines_down)
        sim_factory = {**factory_inputs, "machines": effective_machines}
        sim_market  = {
            "demand_multiplier":        sim_demand,
            "energy_cost_multiplier":   sim_energy,
            "material_cost_multiplier": sim_material,
            "failure_prob":             0.02
        }
        sim_profit  = calculate_profit(sim_factory, sim_market, machine_speed=sim_speed, workers_active=sim_workers, runs=30)
        base_profit = profit_comp["profit_without"]
        sim_diff    = sim_profit - base_profit
        sim_pct     = (sim_diff / abs(base_profit) * 100) if base_profit != 0 else 0
        sim_color   = "#00ff87" if sim_diff >= 0 else "#ff4757"
        sim_units   = effective_machines * sim_speed * hours * 10 * sim_demand

        st.markdown(f"""
        <div class="sim-result" style="margin-bottom:1rem;animation:card-enter 0.4s both;">
            <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:2px;color:#5a7a9a;margin-bottom:0.5rem;">
                Scenario Profit
            </div>
            <div class="sim-value" style="color:{sim_color};animation:num-pop 0.4s both;">{sym}{sim_profit:,.0f}</div>
            <div style="font-size:0.88rem;color:{sim_color};margin-top:0.3rem;font-weight:600;">
                {'+' if sim_diff>=0 else ''}{sym}{sim_diff:,.0f} ({sim_pct:+.1f}%) vs baseline
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.8rem;margin-bottom:1rem;">
            <div class="sim-result">
                <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:1px;color:#5a7a9a;">Proj. Units</div>
                <div class="sim-value" style="font-size:1.8rem;color:#00d4ff;">{int(sim_units):,}</div>
            </div>
            <div class="sim-result">
                <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:1px;color:#5a7a9a;">Active Machines</div>
                <div class="sim-value" style="font-size:1.8rem;color:{'#00ff87' if sim_machines_down==0 else '#ff4757'};">{effective_machines}</div>
            </div>
            <div class="sim-result">
                <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:1px;color:#5a7a9a;">Margin/Unit</div>
                <div class="sim-value" style="font-size:1.8rem;color:#f59e0b;">{sym}{p_price - mat_cost*sim_material:.0f}</div>
            </div>
            <div class="sim-result">
                <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:1px;color:#5a7a9a;">Workers Cost</div>
                <div class="sim-value" style="font-size:1.8rem;color:#a0b8d0;">{sym}{sim_workers*w_cost:,.0f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        fig_sim = go.Figure()
        fig_sim.add_trace(go.Bar(
            x=["Baseline\n(no plan)", "AI Plan\n(current)", "Your\nScenario"],
            y=[profit_comp["profit_without"], profit_comp["profit_with"], sim_profit],
            marker_color=["#1a3a5f", "#00d4ff", sim_color], marker_line_width=0,
            text=[f"{sym}{v:,.0f}" for v in [profit_comp["profit_without"], profit_comp["profit_with"], sim_profit]],
            textposition="outside",
            textfont={"color": "#c8d8e8", "family": "Rajdhani", "size": 13}
        ))
        fig_sim.update_layout(
            paper_bgcolor="#0d1627", plot_bgcolor="#0d1627",
            height=220, margin=dict(t=25, b=10, l=10, r=10),
            yaxis={"visible": False}, xaxis={"tickfont": {"color": "#a0b8d0", "size": 11}},
            bargap=0.35, showlegend=False
        )
        st.plotly_chart(fig_sim, use_container_width=True)

    st.markdown('<div class="section-header">Quick Scenarios — Click to Apply</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.8rem;color:#5a7a9a;margin-bottom:0.8rem;">Click any scenario to instantly load its values into the sliders above.</div>', unsafe_allow_html=True)

    _wk_min = int(workers * 0.3)
    _wk_max = workers
    _sc_defs = [
        ("sc_energy",    "⚡ Energy Crisis",    "#ff4757",
         "Energy 3× — reduce speed to save cost",
         {"sim_e": 3.0, "sim_sp": 0.8, "sim_wk": max(_wk_min, int(workers * 0.8))}),
        ("sc_demand",    "📉 Demand Crash",     "#f59e0b",
         "Orders −60% — go build-to-order only",
         {"sim_d": 0.4, "sim_sp": 0.7, "sim_wk": max(_wk_min, int(workers * 0.6))}),
        ("sc_breakdown", "🔧 5 Machines Down",  "#ff6b35",
         "Major breakdown — activate backup lines",
         {"sim_md": min(5, max(1, machines // 2))}),
        ("sc_fullspeed", "🚀 Full Speed Ahead", "#00ff87",
         "High demand + max speed — watch heat",
         {"sim_d": 1.5, "sim_sp": 1.4, "sim_wk": _wk_max, "sim_md": 0}),
    ]
    sc1, sc2, sc3, sc4 = st.columns(4)
    for _col, (_key, _name, _color, _desc, _vals) in zip([sc1, sc2, sc3, sc4], _sc_defs):
        with _col:
            if st.button(_name, key=f"btn_{_key}", use_container_width=True):
                for _sk, _sv in _vals.items():
                    st.session_state[_sk] = _sv
            st.markdown(
                f'<div style="text-align:center;font-size:0.75rem;color:#5a7a9a;'
                f'margin-top:0.4rem;padding:0 0.3rem;">{_desc}</div>',
                unsafe_allow_html=True,
            )


# ── TAB 5: Production Planning ────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-header">Daily Production Targets</div>', unsafe_allow_html=True)

    p1, p2, p3, p4 = st.columns(4)
    metrics = [
        ("Max Possible",     f"{prod_targets['max_units_possible']:,}", "units if running at 100%", "#5a7a9a"),
        ("Projected Today",  f"{prod_targets['projected_units']:,}",    "units based on conditions", "#00d4ff"),
        ("Break-Even Point", f"{prod_targets['breakeven_units']:,}",    "units to cover all costs",  "#f59e0b"),
        ("Margin / Unit",    f"{sym}{prod_targets['margin_per_unit']:,.2f}", "after materials cost",  "#00ff87"),
    ]
    for col, (label, value, sub, color) in zip([p1, p2, p3, p4], metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="--accent:{color};">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="font-size:1.9rem;">{value}</div>
                <div class="metric-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    be_pct   = min(100, prod_targets["breakeven_pct"])
    be_color = "#00ff87" if be_pct >= 120 else "#f59e0b" if be_pct >= 80 else "#ff4757"
    st.markdown(f"""
    <div style="background:#0d1627;border:1px solid #1a3a5f;border-radius:14px;
                padding:1.5rem;margin-bottom:1.5rem;animation:card-enter 0.5s 0.1s both;">
        <div style="display:flex;justify-content:space-between;margin-bottom:0.6rem;">
            <span style="font-family:'Rajdhani',sans-serif;font-size:0.9rem;font-weight:700;
                         text-transform:uppercase;letter-spacing:2px;color:#c8d8e8;">Break-Even Progress</span>
            <span style="font-family:'IBM Plex Mono',monospace;font-size:0.85rem;
                         color:{be_color};font-weight:600;">{be_pct:.0f}% of break-even covered</span>
        </div>
        <div style="background:#060b14;border-radius:8px;height:18px;overflow:hidden;position:relative;">
            <div style="width:{be_pct}%;background:linear-gradient(90deg,{be_color}88,{be_color});
                        height:100%;border-radius:8px;animation:bar-grow 1.4s 0.3s both;position:relative;overflow:hidden;">
                <div style="position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.25),transparent);
                            animation:bar-shimmer 2s 2s linear infinite;"></div>
            </div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:0.5rem;font-size:0.72rem;color:#3a5a7a;">
            <span>0 units</span>
            <span style="color:#f59e0b;">Break-even: {prod_targets['breakeven_units']:,}</span>
            <span style="color:#00ff87;">Target: {prod_targets['target_units']:,}</span>
            <span>Max: {prod_targets['max_units_possible']:,}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_costs, col_shifts = st.columns([1, 1])

    with col_costs:
        st.markdown('<div class="section-header">Today\'s Cost Breakdown</div>', unsafe_allow_html=True)

        workers_daily_cost = workers * w_cost
        energy_daily       = machines * hours * 5 * e_cost * energy_mult
        mat_daily          = prod_targets["projected_units"] * mat_cost * material_mult
        total_cost         = workers_daily_cost + energy_daily + mat_daily
        revenue_proj       = prod_targets["daily_revenue_proj"]
        gross_profit       = revenue_proj - total_cost

        for label, val, color in [
            ("👷 Labour",     workers_daily_cost, "#2a5a8f"),
            ("⚡ Energy",     energy_daily,       "#f59e0b"),
            ("🏗️ Materials", mat_daily,          "#1a3a5f"),
        ]:
            pct = (val / max(1, total_cost)) * 100
            st.markdown(f"""
            <div style="margin-bottom:0.8rem;">
                <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
                    <span style="font-size:0.85rem;color:#a0b8d0;">{label}</span>
                    <span style="font-family:'IBM Plex Mono',monospace;font-size:0.82rem;color:#c8d8e8;">
                        {sym}{val:,.0f} ({pct:.0f}%)
                    </span>
                </div>
                <div style="background:#060b14;border-radius:4px;height:7px;overflow:hidden;">
                    <div style="width:{pct}%;background:{color};height:100%;border-radius:4px;
                                animation:bar-grow 1s cubic-bezier(0.23,1,0.32,1) both;
                                position:relative;overflow:hidden;">
                        <div style="position:absolute;inset:0;
                                    background:linear-gradient(90deg,transparent,rgba(255,255,255,0.2),transparent);
                                    animation:bar-shimmer 2.5s 1.5s linear infinite;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#060b14;border:1px solid #1a3a5f;border-radius:10px;padding:1rem;margin-top:0.5rem;">
            <div style="display:flex;justify-content:space-between;margin-bottom:0.4rem;">
                <span style="color:#5a7a9a;font-size:0.85rem;">Total Costs</span>
                <span style="font-family:'IBM Plex Mono',monospace;color:#c8d8e8;">{sym}{total_cost:,.0f}</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:0.4rem;">
                <span style="color:#5a7a9a;font-size:0.85rem;">Projected Revenue</span>
                <span style="font-family:'IBM Plex Mono',monospace;color:#00d4ff;">{sym}{revenue_proj:,.0f}</span>
            </div>
            <hr style="border-color:#1a3a5f;margin:0.5rem 0;">
            <div style="display:flex;justify-content:space-between;">
                <span style="color:#5a7a9a;font-size:0.85rem;font-weight:600;">Gross Profit</span>
                <span style="font-family:'IBM Plex Mono',monospace;font-weight:700;
                             color:{'#00ff87' if gross_profit>=0 else '#ff4757'};">{sym}{gross_profit:,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_shifts:
        st.markdown('<div class="section-header">Shift Plan (AI Recommended)</div>', unsafe_allow_html=True)

        for shift in shift_plan:
            energy_label = "✅ Normal" if shift["energy_mult"] <= 1.1 else "⚠️ Elevated" if shift["energy_mult"] <= 1.5 else "🔴 High"
            speed_label  = f"{shift['recommended_speed']:.1f}x"
            st.markdown(f"""
            <div class="shift-card" style="margin-bottom:0.8rem;">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div>
                        <div class="shift-name">{shift['icon']} {shift['name']} Shift</div>
                        <div class="shift-time">{shift['time']}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-family:'Rajdhani',sans-serif;font-size:1.6rem;font-weight:700;color:#00d4ff;">{shift['workers']}</div>
                        <div style="font-size:0.7rem;color:#5a7a9a;">workers</div>
                    </div>
                </div>
                <div style="display:flex;gap:1.5rem;margin-top:0.7rem;flex-wrap:wrap;">
                    <div class="shift-stat">⚡ Energy: <b>{energy_label}</b></div>
                    <div class="shift-stat">🚀 Speed: <b>{speed_label}</b></div>
                    <div class="shift-stat">💰 Cost: <b>{shift['energy_mult']:.2f}x</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#060b14;border:1px solid #1a3a5f;border-radius:8px;padding:1rem;margin-top:0.5rem;">
            <div style="font-size:0.78rem;color:#5a7a9a;line-height:1.7;">
                💡 <b style="color:#c8d8e8;">Night shift tip:</b> Energy costs are ~25% lower after 22:00.
                Schedule energy-intensive operations overnight to save on your electricity bill.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── TAB 6: Industry Intelligence ──────────────────────────────────────────────
with tab6:
    render_industry_tab(factory_type, factory_inputs, market_inputs, risk_result, oee_data, currency)


# ── TAB 7: History ────────────────────────────────────────────────────────────
with tab7:
    if "history_db" not in st.session_state:
        st.session_state["history_db"] = HistoryDB()
    render_history_tab(st.session_state["history_db"], currency_symbol=sym)
