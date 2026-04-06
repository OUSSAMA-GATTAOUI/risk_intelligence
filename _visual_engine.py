import streamlit as st


FONTS = """
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');
"""


BASE_CSS = """
:root {
    --bg-deep:    #03080f;
    --bg-panel:   #060e1c;
    --bg-card:    #0a1628;
    --bg-border:  #0d2240;
    --cyan:       #00d4ff;
    --cyan-dim:   rgba(0,212,255,0.12);
    --green:      #00ff87;
    --green-dim:  rgba(0,255,135,0.10);
    --amber:      #f59e0b;
    --amber-dim:  rgba(245,158,11,0.10);
    --red:        #ff4757;
    --red-dim:    rgba(255,71,87,0.10);
    --orange:     #ff6b35;
    --text-hi:    #e2f0ff;
    --text-mid:   #7a9ab8;
    --text-lo:    #2e4a6a;
}

*, html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    box-sizing: border-box;
}

.stApp {
    background: var(--bg-deep) !important;
    color: #c8d8e8;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #050c18 !important;
    border-right: 1px solid #0d2240;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }
[data-testid="stSidebar"] * { color: #a0b8d0 !important; }
[data-testid="stSidebar"] label {
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #3a5a7a !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stNumberInput input,
[data-testid="stSidebar"] .stTextInput input {
    background: #070f1e !important;
    border: 1px solid #1a3a5f !important;
    color: #c8d8e8 !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #00d4ff 0%, #0066dd 100%) !important;
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
    transition: all 0.3s !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.25) !important;
    animation: btnPulse 3s ease-in-out infinite !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    box-shadow: 0 0 40px rgba(0,212,255,0.55) !important;
    transform: translateY(-2px) !important;
    animation: none !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: #04080f;
    border-bottom: 1px solid #0d2240;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #3a5a7a !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    padding: 0.8rem 1.5rem !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.3s !important;
    position: relative;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #00d4ff !important;
}
.stTabs [aria-selected="true"] {
    color: #00d4ff !important;
    border-bottom-color: #00d4ff !important;
}

/* ── METRIC CARDS ── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--bg-border);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.3s;
    animation: cardSlideIn 0.5s ease-out both;
}
.metric-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--accent, var(--cyan));
}
.metric-card::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, transparent 60%, rgba(var(--accent-rgb,0,212,255),0.04) 100%);
    pointer-events: none;
}
.metric-card:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 12px 40px rgba(0,0,0,0.5), 0 0 20px rgba(var(--accent-rgb,0,212,255),0.08);
    border-color: rgba(var(--accent-rgb,0,212,255),0.3);
}

/* Sweep shimmer on hover */
.metric-card .shimmer {
    position: absolute;
    top: 0; left: -100%;
    width: 60%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
    transition: left 0.6s ease;
    pointer-events: none;
}
.metric-card:hover .shimmer { left: 140%; }

.metric-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #3a5a7a;
    margin-bottom: 0.4rem;
}
.metric-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: var(--accent, var(--cyan));
    line-height: 1;
    margin-bottom: 0.3rem;
}
.metric-sub { font-size: 0.82rem; color: #3a5a7a; }

/* ── SECTION HEADER ── */
.section-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: #7a9ab8;
    border-bottom: 1px solid #0d2240;
    padding-bottom: 0.6rem;
    margin-bottom: 1.2rem;
    margin-top: 1rem;
    position: relative;
}
.section-header::after {
    content: "";
    position: absolute;
    bottom: -1px; left: 0;
    width: 40px; height: 1px;
    background: var(--cyan);
    animation: lineGrow 0.6s ease-out both;
}

/* ── RISK CARDS ── */
.risk-card {
    background: var(--bg-card);
    border: 1px solid var(--bg-border);
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    transition: all 0.25s;
    animation: cardSlideIn 0.4s ease-out both;
}
.risk-card:hover { border-color: #1a4a7f; transform: translateX(3px); }
.risk-card.risk-critical {
    border-left: 3px solid var(--red);
    background: #0e070d;
    animation: criticalPulse 2.5s ease-in-out infinite, cardSlideIn 0.4s ease-out both;
}
.risk-card.risk-high     { border-left: 3px solid var(--orange); }
.risk-card.risk-medium   { border-left: 3px solid var(--amber); }
.risk-card.risk-low      { border-left: 3px solid var(--green); }

/* ── RISK BADGES ── */
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
.badge-critical {
    background: rgba(255,71,87,0.15);
    color: var(--red);
    border: 1px solid rgba(255,71,87,0.4);
    animation: badgeFlash 2s ease-in-out infinite;
}
.badge-high     { background: rgba(255,107,53,0.15); color: var(--orange); border: 1px solid rgba(255,107,53,0.3); }
.badge-medium   { background: rgba(245,158,11,0.15); color: var(--amber);  border: 1px solid rgba(245,158,11,0.3); }
.badge-low      { background: rgba(0,255,135,0.12);  color: var(--green);  border: 1px solid rgba(0,255,135,0.3); }

/* ── ACTION CARDS ── */
.action-card {
    background: var(--bg-card);
    border: 1px solid var(--bg-border);
    border-radius: 10px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1);
    position: relative;
    overflow: hidden;
    animation: cardSlideIn 0.5s ease-out both;
}
.action-card:hover {
    border-color: #1a4a7f;
    transform: translateX(6px);
    box-shadow: -4px 0 20px rgba(0,0,0,0.3);
}
.action-urgent  { border-left: 4px solid var(--red);    }
.action-today   { border-left: 4px solid var(--amber);  }
.action-monitor { border-left: 4px solid var(--green);  }
.action-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-hi);
    margin-bottom: 0.35rem;
}
.action-detail { font-size: 0.88rem; color: var(--text-mid); line-height: 1.5; }
.action-saving {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    font-weight: 500;
    margin-top: 0.5rem;
}

/* ── OEE BARS ── */
.oee-bar-container {
    background: #03070e;
    border-radius: 6px;
    height: 10px;
    overflow: hidden;
    margin-top: 0.4rem;
}
.oee-bar-fill {
    height: 100%;
    border-radius: 6px;
    width: 0%;
    animation: barFill 1.2s cubic-bezier(0.34,1.1,0.64,1) forwards;
    position: relative;
}
.oee-bar-fill::after {
    content: "";
    position: absolute;
    right: 0; top: 0;
    width: 12px; height: 100%;
    background: rgba(255,255,255,0.3);
    filter: blur(4px);
    animation: barGlow 1.5s ease-in-out infinite alternate;
}

/* ── MACHINE GRID ── */
.machine-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding: 1rem 0;
}
.machine-dot {
    width: 32px; height: 32px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.65rem;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 500;
    cursor: default;
    transition: transform 0.2s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.2s;
    animation: dotReveal 0.4s ease-out both;
}
.machine-dot:hover { transform: scale(1.3); z-index: 10; }
.machine-ok       { background: rgba(0,255,135,0.12); color: var(--green);  border: 1px solid rgba(0,255,135,0.25); }
.machine-warn     { background: rgba(245,158,11,0.12); color: var(--amber); border: 1px solid rgba(245,158,11,0.25); animation: warnPulse 2s ease-in-out infinite, dotReveal 0.4s ease-out both; }
.machine-critical { background: rgba(255,71,87,0.12);  color: var(--red);   border: 1px solid rgba(255,71,87,0.3);  animation: critDot 1.5s ease-in-out infinite, dotReveal 0.4s ease-out both; }
.machine-off      { background: rgba(20,40,60,0.4);    color: #2e4a6a;      border: 1px solid rgba(30,60,90,0.2);  }

/* ── TOPBAR ── */
.topbar {
    background: linear-gradient(135deg, #07101f 0%, #0a1628 100%);
    border: 1px solid #0d2240;
    border-radius: 12px;
    padding: 1.2rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.topbar::before {
    content: "";
    position: absolute;
    top: 0; left: -100%;
    width: 200%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
    animation: scanLine 4s linear infinite;
}
.topbar-logo {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    background: linear-gradient(90deg, var(--cyan), #00aaff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ── SIM RESULT ── */
.sim-result {
    background: var(--bg-card);
    border: 1px solid var(--bg-border);
    border-radius: 10px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.2s;
}
.sim-result:hover { border-color: #1a4a7f; }
.sim-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.6rem;
    font-weight: 700;
    line-height: 1;
}

/* ── SHIFT CARDS ── */
.shift-card {
    background: var(--bg-card);
    border: 1px solid var(--bg-border);
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    text-align: center;
    transition: all 0.25s;
}
.shift-card:hover { transform: translateY(-3px); border-color: #1a4a7f; }
.shift-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--cyan);
    margin-bottom: 0.2rem;
}
.shift-time { font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: #3a5a7a; margin-bottom: 0.8rem; }
.shift-stat { font-size: 0.85rem; color: #7a9ab8; margin-bottom: 0.2rem; }
.shift-stat b { color: var(--text-hi); }

/* ── LANDING ── */
.landing-hero { text-align: center; padding: 5rem 2rem; }
.landing-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 4rem;
    font-weight: 700;
    letter-spacing: 5px;
    text-transform: uppercase;
    background: linear-gradient(135deg, #00d4ff, #0077ff, #00ff87);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1rem;
    animation: titleReveal 1s ease-out both;
}
.landing-sub {
    font-size: 1.1rem;
    color: #3a5a7a;
    max-width: 500px;
    margin: 0 auto 3rem;
    line-height: 1.6;
    animation: fadeUp 0.8s ease-out 0.3s both;
}
.landing-steps {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    flex-wrap: wrap;
    max-width: 900px;
    margin: 0 auto;
}
.landing-step {
    background: var(--bg-card);
    border: 1px solid var(--bg-border);
    border-radius: 12px;
    padding: 1.5rem;
    width: 220px;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
    animation: fadeUp 0.6s ease-out both;
}
.landing-step:nth-child(1) { animation-delay: 0.4s; }
.landing-step:nth-child(2) { animation-delay: 0.55s; }
.landing-step:nth-child(3) { animation-delay: 0.7s; }
.landing-step:nth-child(4) { animation-delay: 0.85s; }
.landing-step:hover {
    border-color: var(--cyan);
    box-shadow: 0 0 30px rgba(0,212,255,0.12);
    transform: translateY(-6px);
}
.step-num {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--cyan);
    line-height: 1;
    margin-bottom: 0.5rem;
}
.step-title { font-weight: 600; color: var(--text-hi); margin-bottom: 0.3rem; font-size: 0.95rem; }
.step-desc  { font-size: 0.82rem; color: #3a5a7a; }

/* ── SIDEBAR BRAND ── */
.sidebar-brand {
    background: linear-gradient(135deg, #070f1e 0%, #050c18 100%);
    border-bottom: 1px solid #0d2240;
    padding: 1.2rem 1rem;
    margin: -1rem -1rem 1rem -1rem;
    position: relative;
    overflow: hidden;
}
.sidebar-brand::before {
    content: "";
    position: absolute;
    bottom: 0; left: 0;
    width: 100%; height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
    animation: scanLine 3s linear infinite;
}
.sidebar-brand-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: 3px;
    color: var(--cyan);
    text-transform: uppercase;
}
.sidebar-brand-sub { font-size: 0.72rem; color: #1a3a5a; letter-spacing: 1px; }

/* ── MISC ── */
hr { border-color: #0d2240 !important; }
.stProgress > div > div > div { background: var(--cyan) !important; }
.stAlert { background: var(--bg-card) !important; border: 1px solid var(--bg-border) !important; color: #7a9ab8 !important; }
.js-plotly-plot .plotly, .js-plotly-plot .plotly * { font-family: 'IBM Plex Sans', sans-serif; }

/* ───── KEYFRAMES ───── */

@keyframes btnPulse {
    0%, 100% { box-shadow: 0 0 20px rgba(0,212,255,0.25) !important; }
    50%       { box-shadow: 0 0 35px rgba(0,212,255,0.50) !important; }
}

@keyframes cardSlideIn {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes titleReveal {
    from { opacity: 0; letter-spacing: 12px; }
    to   { opacity: 1; letter-spacing: 5px; }
}

@keyframes criticalPulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255,71,87,0); border-color: rgba(255,71,87,0.3); }
    50%       { box-shadow: 0 0 0 6px rgba(255,71,87,0.04), inset 0 0 20px rgba(255,71,87,0.04); border-color: rgba(255,71,87,0.6); }
}

@keyframes badgeFlash {
    0%, 90%, 100% { opacity: 1; }
    95%            { opacity: 0.5; }
}

@keyframes warnPulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(245,158,11,0); }
    50%       { box-shadow: 0 0 8px 2px rgba(245,158,11,0.15); }
}

@keyframes critDot {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255,71,87,0); }
    50%       { box-shadow: 0 0 10px 3px rgba(255,71,87,0.2); }
}

@keyframes dotReveal {
    from { opacity: 0; transform: scale(0.5); }
    to   { opacity: 1; transform: scale(1); }
}

@keyframes barFill {
    from { width: 0%; }
    to   { width: var(--target-width, 100%); }
}

@keyframes barGlow {
    from { opacity: 0.2; }
    to   { opacity: 0.7; }
}

@keyframes scanLine {
    0%   { left: -100%; }
    100% { left: 100%; }
}

@keyframes lineGrow {
    from { width: 0; }
    to   { width: 40px; }
}

@keyframes live-blink {
    0%, 100% { opacity: 1; box-shadow: 0 0 8px var(--green); }
    50%       { opacity: 0.2; box-shadow: none; }
}

.live-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: var(--green);
    border-radius: 50%;
    animation: live-blink 1.5s infinite;
    margin-right: 6px;
}
"""


PARTICLE_JS = """
<canvas id="fiq-canvas" style="
    position:fixed;top:0;left:0;
    width:100%;height:100%;
    pointer-events:none;
    z-index:0;
    opacity:0.55;
"></canvas>

<div id="fiq-cursor" style="
    position:fixed;
    width:300px;height:300px;
    border-radius:50%;
    background:radial-gradient(circle, rgba(0,212,255,0.06) 0%, transparent 70%);
    pointer-events:none;
    z-index:1;
    transform:translate(-50%,-50%);
    transition:transform 0.05s linear;
    top:-999px;left:-999px;
"></div>

<script>
(function() {
  var canvas  = document.getElementById('fiq-canvas');
  var cursor  = document.getElementById('fiq-cursor');
  var ctx     = canvas.getContext('2d');
  var W, H, nodes, mouse = {x: -9999, y: -9999};

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function Node() {
    this.x  = Math.random() * W;
    this.y  = Math.random() * H;
    this.vx = (Math.random() - 0.5) * 0.3;
    this.vy = (Math.random() - 0.5) * 0.3;
    this.r  = Math.random() * 1.5 + 0.5;
    this.pulse = Math.random() * Math.PI * 2;
  }

  function initNodes() {
    nodes = [];
    var count = Math.floor((W * H) / 16000);
    for (var i = 0; i < count; i++) nodes.push(new Node());
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);

    var t = Date.now() * 0.001;

    for (var i = 0; i < nodes.length; i++) {
      var n = nodes[i];
      n.pulse += 0.018;
      n.x += n.vx;
      n.y += n.vy;
      if (n.x < 0) n.x = W;
      if (n.x > W) n.x = 0;
      if (n.y < 0) n.y = H;
      if (n.y > H) n.y = 0;

      var glow = 0.4 + 0.3 * Math.sin(n.pulse);
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r * glow, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(0,212,255,' + (0.3 * glow) + ')';
      ctx.fill();

      for (var j = i + 1; j < nodes.length; j++) {
        var m  = nodes[j];
        var dx = n.x - m.x;
        var dy = n.y - m.y;
        var d  = Math.sqrt(dx * dx + dy * dy);
        if (d < 120) {
          var alpha = (1 - d / 120) * 0.18;
          ctx.beginPath();
          ctx.moveTo(n.x, n.y);
          ctx.lineTo(m.x, m.y);
          ctx.strokeStyle = 'rgba(0,180,220,' + alpha + ')';
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }

      var mdx = n.x - mouse.x;
      var mdy = n.y - mouse.y;
      var md  = Math.sqrt(mdx * mdx + mdy * mdy);
      if (md < 180) {
        var malpha = (1 - md / 180) * 0.5;
        ctx.beginPath();
        ctx.moveTo(n.x, n.y);
        ctx.lineTo(mouse.x, mouse.y);
        ctx.strokeStyle = 'rgba(0,212,255,' + malpha + ')';
        ctx.lineWidth = 0.7;
        ctx.stroke();
      }
    }

    requestAnimationFrame(draw);
  }

  window.addEventListener('mousemove', function(e) {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
    if (cursor) {
      cursor.style.left = e.clientX + 'px';
      cursor.style.top  = e.clientY + 'px';
    }
  });

  window.addEventListener('resize', function() {
    resize();
    initNodes();
  });

  resize();
  initNodes();
  draw();
})();
</script>

<script>
/* ── Animated bar fills ── */
function animateBars() {
  document.querySelectorAll('.oee-bar-fill').forEach(function(bar) {
    var target = bar.getAttribute('data-width') || bar.style.width;
    if (target) {
      bar.style.setProperty('--target-width', target);
      bar.style.width = '0%';
      bar.style.animation = 'none';
      void bar.offsetWidth;
      bar.style.animation = 'barFill 1.2s cubic-bezier(0.34,1.1,0.64,1) forwards';
    }
  });
}

/* ── Counter animation ── */
function animateCounters() {
  document.querySelectorAll('.metric-value').forEach(function(el) {
    var text = el.innerText || el.textContent;
    var match = text.match(/([\+\-€£$]?)([\d,]+(\.\d+)?)(.*)/);
    if (!match) return;
    var prefix = match[1] || '';
    var target = parseFloat(match[2].replace(/,/g,''));
    var suffix = match[4] || '';
    if (isNaN(target) || target <= 0) return;
    var start   = 0;
    var duration = 1200;
    var startTime = null;
    var hasDec  = match[2].indexOf('.') !== -1 || match[3];
    function step(ts) {
      if (!startTime) startTime = ts;
      var progress = Math.min((ts - startTime) / duration, 1);
      var ease = 1 - Math.pow(1 - progress, 3);
      var current = ease * target;
      var formatted = hasDec ? current.toFixed(1) : Math.floor(current).toLocaleString();
      el.textContent = prefix + formatted + suffix;
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  });
}

/* ── Stagger card animations ── */
function staggerCards() {
  var cards = document.querySelectorAll('.metric-card, .action-card, .risk-card, .shift-card');
  cards.forEach(function(card, i) {
    card.style.animationDelay = (i * 60) + 'ms';
  });
}

/* ── Add shimmer divs ── */
function addShimmers() {
  document.querySelectorAll('.metric-card').forEach(function(card) {
    if (!card.querySelector('.shimmer')) {
      var s = document.createElement('div');
      s.className = 'shimmer';
      card.appendChild(s);
    }
  });
}

/* Run everything after Streamlit re-renders */
var _fiq_observer = new MutationObserver(function() {
  animateBars();
  staggerCards();
  addShimmers();
});
_fiq_observer.observe(document.body, {childList: true, subtree: true});

setTimeout(function() {
  animateBars();
  animateCounters();
  staggerCards();
  addShimmers();
}, 400);
</script>
"""


def inject():
    st.markdown(
        f"<style>{FONTS}{BASE_CSS}</style>",
        unsafe_allow_html=True
    )
    st.markdown(PARTICLE_JS, unsafe_allow_html=True)
