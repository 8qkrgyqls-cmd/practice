import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, csv
from collections import defaultdict
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="한강 수질 분석 · 2020–2050",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
* { font-family: 'Noto Sans KR', sans-serif !important; }
.block-container { padding: 1.5rem 2rem 3rem; max-width: 1400px; }

/* expander 화살표·이모지 겹침 수정 */
[data-testid="stExpander"] summary {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #1e293b !important;
    line-height: 1.4 !important;
}
[data-testid="stExpander"] summary p {
    margin: 0 !important;
    display: inline !important;
}
[data-testid="stExpander"] summary svg {
    flex-shrink: 0 !important;
    margin-right: 4px !important;
}
[data-testid="stExpander"] {
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    margin-bottom: 10px !important;
    overflow: hidden !important;
}

.hero {
    background: linear-gradient(135deg, #0c1e3c 0%, #0f3460 55%, #16547a 100%);
    border-radius: 20px; padding: 40px 48px 36px;
    margin-bottom: 28px; position: relative; overflow: hidden;
}
.hero::before {
    content: ''; position: absolute; top: -40px; right: -40px;
    width: 260px; height: 260px; border-radius: 50%;
    background: rgba(255,255,255,0.04);
}
.hero-title { font-size: 30px; font-weight: 900; color: #fff; letter-spacing: -0.5px; margin: 0 0 8px; }
.hero-sub   { font-size: 14px; color: rgba(255,255,255,0.65); margin: 0; line-height: 1.6; }
.hero-tags  { margin-top: 18px; display: flex; gap: 8px; flex-wrap: wrap; }
.hero-tag {
    background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.2);
    color: rgba(255,255,255,0.85); border-radius: 20px; padding: 4px 14px;
    font-size: 12px; font-weight: 500;
}
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }
.kpi {
    background: #fff; border-radius: 14px; padding: 18px 20px 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-top: 3px solid #2563eb;
}
.kpi.orange { border-top-color: #ea580c; }
.kpi.teal   { border-top-color: #0891b2; }
.kpi.amber  { border-top-color: #d97706; }
.kpi-label  { font-size: 11.5px; color: #6b7280; font-weight: 500; letter-spacing: 0.04em; margin-bottom: 6px; }
.kpi-value  { font-size: 28px; font-weight: 800; color: #111827; line-height: 1; }
.kpi-unit   { font-size: 13px; font-weight: 400; color: #6b7280; margin-left: 2px; }
.kpi-range  { font-size: 11px; color: #9ca3af; margin-top: 5px; }

.sec-hd {
    font-size: 16px; font-weight: 700; color: #0c1e3c;
    border-left: 4px solid #2563eb; padding-left: 12px;
    margin: 28px 0 14px;
}
.chart-wrap {
    background: #fff; border-radius: 16px; padding: 8px 12px 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 16px;
}
.ins-card {
    background: #fff; border-radius: 14px; padding: 20px 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 14px;
    border-left: 4px solid #e5e7eb;
}
.ins-card.blue   { border-left-color: #3b82f6; }
.ins-card.red    { border-left-color: #ef4444; }
.ins-card.green  { border-left-color: #22c55e; }
.ins-card.orange { border-left-color: #f97316; }
.ins-card.purple { border-left-color: #a855f7; }
.ins-card.indigo { border-left-color: #6366f1; }
.ins-card.teal   { border-left-color: #0891b2; }
.ins-card.rose   { border-left-color: #f43f5e; }
.ins-card.sky    { border-left-color: #0ea5e9; }
.ins-title { font-size: 14.5px; font-weight: 700; color: #1e293b; margin-bottom: 10px; }
.ins-body  { font-size: 13.5px; color: #374151; line-height: 1.85; }

.badge { display: inline-block; border-radius: 20px; padding: 2px 10px; font-size: 11.5px; font-weight: 600; margin: 0 2px; }
.b-blue   { background:#dbeafe; color:#1d4ed8; }
.b-red    { background:#fee2e2; color:#b91c1c; }
.b-green  { background:#dcfce7; color:#15803d; }
.b-orange { background:#ffedd5; color:#c2410c; }
.b-gray   { background:#f3f4f6; color:#374151; }
.b-purple { background:#f3e8ff; color:#7e22ce; }
.b-teal   { background:#ccfbf1; color:#0f766e; }
.b-sky    { background:#e0f2fe; color:#0369a1; }

.warn-box {
    background: #fef9c3; border: 1px solid #fde047; border-radius: 10px;
    padding: 12px 18px; font-size: 13px; color: #713f12; margin-bottom: 16px;
}
.grade-table { width:100%; border-collapse:collapse; font-size:13px; }
.grade-table th, .grade-table td { padding: 8px 12px; border: 1px solid #e5e7eb; text-align:left; }
.grade-table th { background: #f9fafb; font-weight: 600; color: #374151; }
.grade-table tr:nth-child(even) td { background: #f9fafb; }

/* 정책 카드 */
.policy-card {
    background: #fff; border-radius: 14px; padding: 22px 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07); margin-bottom: 16px;
    border-top: 3px solid #2563eb;
}
.policy-card.green  { border-top-color: #22c55e; }
.policy-card.orange { border-top-color: #f97316; }
.policy-card.purple { border-top-color: #a855f7; }
.policy-card.teal   { border-top-color: #0891b2; }
.policy-card.red    { border-top-color: #ef4444; }
.policy-num {
    display: inline-flex; align-items: center; justify-content: center;
    width: 26px; height: 26px; border-radius: 50%;
    background: #2563eb; color: #fff; font-size: 12px; font-weight: 700;
    margin-right: 8px; flex-shrink: 0;
}
.policy-num.green  { background: #22c55e; }
.policy-num.orange { background: #f97316; }
.policy-num.purple { background: #a855f7; }
.policy-num.teal   { background: #0891b2; }
.policy-num.red    { background: #ef4444; }
.policy-title { font-size: 15px; font-weight: 700; color: #1e293b; display: flex; align-items: center; margin-bottom: 12px; }
.policy-body  { font-size: 13.5px; color: #374151; line-height: 1.85; }
.policy-row   { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 10px; }
.policy-sub   { background: #f9fafb; border-radius: 8px; padding: 12px 14px; }
.policy-sub-title { font-size: 12px; font-weight: 700; color: #6b7280; margin-bottom: 6px; letter-spacing: 0.05em; }
.policy-sub-body  { font-size: 13px; color: #374151; line-height: 1.7; }

/* ── 수질 해석 탭 달력형 ─────────────────────────────────────────────────── */
.cal-wrap{background:#fff;border-radius:20px;box-shadow:0 4px 24px rgba(0,0,0,0.08);overflow:hidden;margin-bottom:24px}
.cal-header{background:linear-gradient(135deg,#0c1e3c,#1e4d7b);padding:20px 28px 16px;display:flex;align-items:center;justify-content:space-between}
.cal-header-title{font-size:18px;font-weight:900;color:#fff;letter-spacing:-0.3px}
.cal-header-sub{font-size:12px;color:rgba(255,255,255,0.55);margin-top:3px}
.cal-legend{display:flex;gap:12px;flex-wrap:wrap}
.cal-legend-item{display:flex;align-items:center;gap:5px;font-size:11px;color:rgba(255,255,255,0.75);font-weight:600}
.cal-legend-dot{width:10px;height:10px;border-radius:50%}
.cal-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:0}
.cal-month{padding:18px 20px;border-right:1px solid #f1f5f9;border-bottom:1px solid #f1f5f9;transition:background 0.15s;position:relative}
.cal-month:hover{background:#f8fafc}
.cal-month:nth-child(4n){border-right:none}
.cal-month:nth-child(n+9){border-bottom:none}
.cal-month-name{font-size:11px;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;color:#94a3b8;margin-bottom:10px}
.cal-vals{display:flex;flex-direction:column;gap:6px;margin-bottom:10px}
.cal-val-row{display:flex;align-items:center;justify-content:space-between}
.cal-val-label{font-size:10.5px;color:#94a3b8;font-weight:600}
.cal-val-num{font-size:15px;font-weight:900;line-height:1}
.cal-val-unit{font-size:9px;font-weight:500;color:#94a3b8;margin-left:1px}
.cal-do-bar-wrap{height:4px;background:#f1f5f9;border-radius:99px;margin:8px 0 6px;overflow:hidden}
.cal-do-bar{height:100%;border-radius:99px}
.cal-tag{display:inline-block;font-size:10px;font-weight:700;padding:2px 7px;border-radius:99px;margin-top:4px}
.cal-insight-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-top:20px}
.cal-insight-card{border-radius:14px;padding:18px 20px;border-left:4px solid #e5e7eb}
.cal-insight-card.spring{background:#fefce8;border-left-color:#eab308}
.cal-insight-card.summer{background:#fff1f2;border-left-color:#f43f5e}
.cal-insight-card.autumn{background:#fff7ed;border-left-color:#f97316}
.cal-insight-card.winter{background:#eff6ff;border-left-color:#3b82f6}
.cal-insight-title{font-size:13px;font-weight:800;color:#1e293b;margin-bottom:8px}
.cal-insight-body{font-size:12.5px;color:#475569;line-height:1.75}

/* ── 수질 정책 탭 카드형 ─────────────────────────────────────────────────── */
.policy-intro{background:linear-gradient(135deg,#0c1e3c 0%,#134e7a 100%);border-radius:20px;padding:36px 44px;margin-bottom:40px;position:relative;overflow:hidden}
.policy-intro::after{content:'한강';position:absolute;right:-10px;top:-20px;font-size:160px;font-weight:900;color:rgba(255,255,255,0.04);line-height:1;pointer-events:none}
.policy-intro-label{font-size:11px;font-weight:700;letter-spacing:0.18em;color:#38bdf8;text-transform:uppercase;margin-bottom:10px}
.policy-intro-title{font-size:26px;font-weight:900;color:#fff;line-height:1.3;margin-bottom:14px}
.policy-intro-body{font-size:13.5px;color:rgba(255,255,255,0.65);line-height:1.85;max-width:680px}
.policy-intro-stats{display:flex;gap:32px;margin-top:24px;flex-wrap:wrap}
.policy-intro-stat-val{font-size:28px;font-weight:900;color:#fff;line-height:1}
.policy-intro-stat-label{font-size:11px;color:rgba(255,255,255,0.5);margin-top:4px}
.phase-header{display:flex;align-items:center;gap:14px;margin:44px 0 20px}
.phase-pill{display:inline-flex;align-items:center;gap:8px;padding:6px 16px;border-radius:99px;font-size:12px;font-weight:700;letter-spacing:0.04em}
.phase-pill.short{background:#dbeafe;color:#1d4ed8}
.phase-pill.mid{background:#dcfce7;color:#15803d}
.phase-pill.long{background:#f3e8ff;color:#7e22ce}
.phase-line{flex:1;height:1px;background:linear-gradient(to right,#e5e7eb,transparent)}
.pcard-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:12px}
.pcard-grid.two{grid-template-columns:repeat(2,1fr)}
.pcard{background:#fff;border-radius:16px;padding:0;box-shadow:0 2px 12px rgba(0,0,0,0.07);overflow:hidden;transition:transform 0.18s ease,box-shadow 0.18s ease;position:relative}
.pcard:hover{transform:translateY(-4px);box-shadow:0 10px 32px rgba(0,0,0,0.13)}
.pcard-accent{height:4px;width:100%}
.pcard-inner{padding:20px 22px 22px}
.pcard-icon-row{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.pcard-icon{width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:22px}
.pcard-num{font-size:11px;font-weight:800;letter-spacing:0.1em;color:#9ca3af}
.pcard-title{font-size:14.5px;font-weight:800;color:#111827;line-height:1.4;margin-bottom:10px}
.pcard-detail{font-size:12.5px;color:#6b7280;line-height:1.7;margin-bottom:16px}
.pcard-divider{height:1px;background:#f3f4f6;margin-bottom:14px}
.pcard-effect-label{font-size:10px;font-weight:700;letter-spacing:0.12em;color:#9ca3af;margin-bottom:6px;text-transform:uppercase}
.pcard-effect{font-size:13px;font-weight:700;line-height:1.5}
.pcard-do-row{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}
.pcard-do-chip{font-size:11.5px;font-weight:700;padding:3px 10px;border-radius:99px}
.roadmap-wrap{background:#f8fafc;border-radius:18px;padding:32px 36px;margin:36px 0 28px}
.roadmap-title{font-size:13px;font-weight:700;letter-spacing:0.1em;color:#64748b;text-transform:uppercase;margin-bottom:28px}
.roadmap-timeline{display:flex;gap:0;position:relative}
.roadmap-timeline::before{content:'';position:absolute;top:22px;left:22px;right:22px;height:2px;background:linear-gradient(to right,#2563eb,#0891b2,#22c55e);z-index:0}
.roadmap-phase{flex:1;position:relative;z-index:1;text-align:center;padding:0 8px}
.roadmap-dot{width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:18px;margin:0 auto 12px;border:3px solid white}
.roadmap-dot.short{background:#eff6ff;color:#2563eb;box-shadow:0 0 0 3px #2563eb}
.roadmap-dot.mid{background:#f0fdfa;color:#0891b2;box-shadow:0 0 0 3px #0891b2}
.roadmap-dot.long{background:#f0fdf4;color:#22c55e;box-shadow:0 0 0 3px #22c55e}
.roadmap-phase-label{font-size:12px;font-weight:800;margin-bottom:4px}
.roadmap-phase-period{font-size:11px;color:#94a3b8;margin-bottom:10px}
.roadmap-items{display:flex;flex-direction:column;gap:4px}
.roadmap-item{font-size:11.5px;color:#475569;background:white;border-radius:6px;padding:4px 10px;text-align:left;box-shadow:0 1px 3px rgba(0,0,0,0.06)}
.roadmap-target{margin-top:10px;font-size:11px;font-weight:700;padding:4px 10px;border-radius:6px;display:inline-block}
.roadmap-target.short{background:#dbeafe;color:#1d4ed8}
.roadmap-target.mid{background:#ccfbf1;color:#0f766e}
.roadmap-target.long{background:#dcfce7;color:#15803d}
.map-section-hd{display:flex;align-items:center;gap:12px;background:linear-gradient(135deg,#0f172a,#1e3a5f);border-radius:14px;padding:20px 24px;margin:36px 0 20px}
.map-section-hd-icon{font-size:28px}
.map-section-hd-title{font-size:17px;font-weight:800;color:#fff}
.map-section-hd-sub{font-size:12.5px;color:rgba(255,255,255,0.55);margin-top:2px}
</style>
""", unsafe_allow_html=True)


# ── 지도용 상수 ───────────────────────────────────────────────────────────────
STATIONS = {
    "노량진": {"lat": 37.5110, "lon": 126.9333},
    "선유":   {"lat": 37.5330, "lon": 126.8780},
}
HANGANG = [
    [37.513, 126.958],[37.515, 126.940],[37.516, 126.920],
    [37.518, 126.900],[37.523, 126.878],[37.528, 126.858],
]

# ── 미래 예측 데이터 ──────────────────────────────────────────────────────────
FUTURE = {
    "year": [2026, 2030, 2040, 2050],
    "SSP245_노량진_DO": [8.26, 7.93, 7.43, 6.96],
    "SSP245_선유_DO":   [8.04, 7.73, 7.24, 6.77],
    "SSP245_노량진_pH": [7.275, 7.267, 7.247, 7.227],
    "SSP245_선유_pH":   [7.305, 7.297, 7.277, 7.257],
    "SSP585_노량진_DO": [8.11, 7.51, 6.51, 5.54],
    "SSP585_선유_DO":   [7.90, 7.31, 6.34, 5.37],
    "SSP585_노량진_pH": [7.275, 7.257, 7.207, 7.137],
    "SSP585_선유_pH":   [7.305, 7.287, 7.237, 7.167],
}
df_future = pd.DataFrame(FUTURE)

# ── 정책 데이터 ───────────────────────────────────────────────────────────────
MAP_POLICIES = [
    {
        "phase": "단기", "phase_label": "단기 (2026~2030)",
        "badge": "badge-short", "card": "short", "icon": "🌬️",
        "title": "폭기(曝氣) 시설 확충",
        "effect": "DO 최솟값 +2~4 mg/L 즉각 상승",
        "detail": "수중 산기관·폭기 선박 상시 운영으로 여름철 DO 급락 긴급 대응",
        "do_impact_nry": 2.5, "do_impact_syu": 2.0,
    },
    {
        "phase": "단기", "phase_label": "단기 (2026~2030)",
        "badge": "badge-short", "card": "short", "icon": "📡",
        "title": "실시간 모니터링 고도화",
        "effect": "DO 위험 6~12시간 전 조기 경보",
        "detail": "AI 예측 모델 + IoT 센서망으로 10분 단위 수질 수집 및 자동 경보",
        "do_impact_nry": 0.3, "do_impact_syu": 0.3,
    },
    {
        "phase": "단기", "phase_label": "단기 (2026~2030)",
        "badge": "badge-short", "card": "short", "icon": "🌧️",
        "title": "초기 우수 저류조 설치",
        "effect": "강우 후 DO 급락 30~50% 완충",
        "detail": "강변 초기 우수 저류조·투수성 포장재 확대로 도시 오염 유출 차단",
        "do_impact_nry": 0.8, "do_impact_syu": 1.2,
    },
    {
        "phase": "중기", "phase_label": "중기 (2031~2040)",
        "badge": "badge-mid", "card": "mid", "icon": "🏭",
        "title": "하수처리장 고도화",
        "effect": "총인 50% 감소 → DO +1.0~1.5 mg/L",
        "detail": "중랑·탄천 처리장 고도처리(A²O, MBR) 도입, 방류수 총인 0.2mg/L 이하",
        "do_impact_nry": 1.2, "do_impact_syu": 1.5,
    },
    {
        "phase": "중기", "phase_label": "중기 (2031~2040)",
        "badge": "badge-mid", "card": "mid", "icon": "🌿",
        "title": "생태습지·수변완충구역 확대",
        "effect": "수온 1~2°C 냉각, 질소 최대 500kg/ha 제거",
        "detail": "한강변 정수식물 군락 복원, 수변 완충 녹지대(30m) 지정 및 생태공원 확대",
        "do_impact_nry": 0.6, "do_impact_syu": 0.9,
    },
    {
        "phase": "장기", "phase_label": "장기 (2041~2050)",
        "badge": "badge-long", "card": "long", "icon": "🌳",
        "title": "도시 열섬 완화·탄소 감축",
        "effect": "열섬 1°C 완화 → DO +0.1~0.16 mg/L",
        "detail": "옥상 녹화·도시 숲·바람길 조성으로 서울 열섬 완화, 한강 수온을 기후정책 공식 지표 채택",
        "do_impact_nry": 0.5, "do_impact_syu": 0.4,
    },
]

POLICY_MARKERS = {
    "폭기(曝氣) 시설 확충": [
        {"lat": 37.513, "lon": 126.920, "icon": "🌬️", "label": "폭기시설", "color": "#3498DB"},
        {"lat": 37.524, "lon": 126.888, "icon": "🌬️", "label": "폭기시설", "color": "#3498DB"},
    ],
    "실시간 모니터링 고도화": [
        {"lat": 37.516, "lon": 126.935, "icon": "📡", "label": "모니터링", "color": "#8E44AD"},
        {"lat": 37.526, "lon": 126.875, "icon": "📡", "label": "모니터링", "color": "#8E44AD"},
    ],
    "초기 우수 저류조 설치": [
        {"lat": 37.510, "lon": 126.930, "icon": "🌧️", "label": "저류조",   "color": "#2980B9"},
        {"lat": 37.530, "lon": 126.870, "icon": "🌧️", "label": "저류조",   "color": "#2980B9"},
    ],
    "하수처리장 고도화": [
        {"lat": 37.520, "lon": 126.960, "icon": "🏭", "label": "고도처리장","color": "#27AE60"},
    ],
    "생태습지·수변완충구역 확대": [
        {"lat": 37.512, "lon": 126.910, "icon": "🌿", "label": "생태습지", "color": "#2ECC71"},
        {"lat": 37.528, "lon": 126.865, "icon": "🌿", "label": "생태습지", "color": "#2ECC71"},
    ],
    "도시 열섬 완화·탄소 감축": [
        {"lat": 37.516, "lon": 126.945, "icon": "🌳", "label": "도시숲",   "color": "#1E8449"},
        {"lat": 37.522, "lon": 126.895, "icon": "🌳", "label": "도시숲",   "color": "#1E8449"},
    ],
}

# ── 지도 헬퍼 함수 ────────────────────────────────────────────────────────────
def do_color(val):
    if val >= 7.5:   return "#2ECC71"
    elif val >= 5.0: return "#F39C12"
    elif val >= 2.0: return "#E67E22"
    else:            return "#E74C3C"

def do_grade_label(val):
    if val >= 7.5:   return "🟢 1등급"
    elif val >= 5.0: return "🟡 2~3등급"
    elif val >= 2.0: return "🟠 4등급"
    else:            return "🔴 5등급↓"

def build_map(center, do_nry, do_syu, ph_nry, ph_syu, year, label, policy_markers=None):
    m = folium.Map(location=center, zoom_start=13, tiles="CartoDB positron")
    folium.PolyLine(HANGANG, color="#4A90D9", weight=8, opacity=0.35, tooltip="한강").add_to(m)
    for name, lat, lon, do_val, ph_val in [
        ("노량진", STATIONS["노량진"]["lat"], STATIONS["노량진"]["lon"], do_nry, ph_nry),
        ("선유",   STATIONS["선유"]["lat"],   STATIONS["선유"]["lon"],   do_syu, ph_syu),
    ]:
        color = do_color(do_val)
        grade = do_grade_label(do_val)
        popup_html = f"""
        <div style='font-family:Arial;min-width:190px'>
            <h4 style='color:{color};margin:0 0 6px 0'>📍 {name} 측정소</h4>
            <hr style='margin:4px 0'>
            <b>조건:</b> {label}<br><b>연도:</b> {year}년<br>
            <hr style='margin:4px 0'>
            <b>DO:</b> <span style='color:{color};font-size:15px;font-weight:700'>{do_val:.2f} mg/L</span><br>
            <b>pH:</b> {ph_val:.3f}<br><b>등급:</b> {grade}
        </div>"""
        folium.CircleMarker(
            location=[lat, lon],
            radius=max(14 + (do_val - 5) * 2.5, 10),
            color=color, fill=True, fill_color=color, fill_opacity=0.75,
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=f"{name} | DO {do_val:.2f} mg/L | {grade}"
        ).add_to(m)
        folium.Marker(
            location=[lat + 0.0028, lon],
            icon=folium.DivIcon(html=f"""
                <div style='background:{color};color:white;padding:3px 8px;
                border-radius:6px;font-size:12px;font-weight:700;
                box-shadow:0 2px 5px rgba(0,0,0,0.25);white-space:nowrap'>
                {name} {do_val:.1f} mg/L</div>""")
        ).add_to(m)
    if policy_markers:
        for pm in policy_markers:
            folium.Marker(
                location=[pm["lat"], pm["lon"]],
                icon=folium.DivIcon(html=f"""
                    <div style='background:white;border:2px solid {pm["color"]};
                    color:{pm["color"]};padding:3px 7px;border-radius:8px;
                    font-size:11px;font-weight:700;
                    box-shadow:0 2px 5px rgba(0,0,0,0.2);white-space:nowrap'>
                    {pm["icon"]} {pm["label"]}</div>"""),
                tooltip=pm["label"]
            ).add_to(m)
    legend = f"""
    <div style='position:fixed;bottom:20px;left:20px;z-index:1000;
    background:white;padding:10px 14px;border-radius:10px;
    box-shadow:0 2px 8px rgba(0,0,0,0.18);font-family:Arial;font-size:12px'>
    <b>DO 등급</b><br>
    <span style='color:#2ECC71'>●</span> 1등급 ≥7.5<br>
    <span style='color:#F39C12'>●</span> 2~3등급 ≥5.0<br>
    <span style='color:#E67E22'>●</span> 4등급 ≥2.0<br>
    <span style='color:#E74C3C'>●</span> 5등급 &lt;2.0
    </div>"""
    m.get_root().html.add_child(folium.Element(legend))
    return m

# ── 데이터 로드 ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    ph_candidates = [
        os.path.join(base, 'ph.csv'),
        os.path.join(base, '수소이온농도.csv'),
        os.path.join(base, 'data', '수소이온농도.csv'),
    ]
    do_candidates = [
        os.path.join(base, 'do.csv'),
        os.path.join(base, '용존산소.csv'),
        os.path.join(base, 'data', '용존산소.csv'),
    ]

    def find_file(candidates):
        for p in candidates:
            if os.path.exists(p):
                return p
        raise FileNotFoundError(
            "데이터 파일을 찾을 수 없습니다.\n"
            "ph.csv 와 do.csv 를 app.py 와 같은 폴더에 놓아 주세요."
        )

    def read_csv(path):
        for enc in ['utf-8', 'utf-8-sig', 'cp949', 'euc-kr']:
            try:
                rows = []
                with open(path, encoding=enc, errors='strict') as f:
                    reader = csv.DictReader(f)
                    if reader.fieldnames is None:
                        continue
                    for row in reader:
                        rows.append(row)
                if rows:
                    return rows
            except Exception:
                continue
        raise ValueError(f"파일을 읽을 수 없습니다: {path}")

    def daily_means(rows, col):
        daily = defaultdict(list)
        for r in rows:
            v = r.get(col, '').strip()
            if v and v != '-':
                try:
                    daily[r['일시'].split(' ')[0]].append(float(v))
                except Exception:
                    pass
        return {d: round(sum(vs) / len(vs), 3) for d, vs in daily.items()}

    ph_rows = read_csv(find_file(ph_candidates))
    do_rows = read_csv(find_file(do_candidates))

    ph_ny = daily_means(ph_rows, '노량진')
    ph_sy = daily_means(ph_rows, '선유')
    do_ny = daily_means(do_rows, '노량진')
    do_sy = daily_means(do_rows, '선유')

    dates = sorted(set(list(ph_ny) + list(ph_sy) + list(do_ny) + list(do_sy)))
    return pd.DataFrame({
        'date':      pd.to_datetime(dates),
        'pH_노량진': [ph_ny.get(d) for d in dates],
        'pH_선유':   [ph_sy.get(d) for d in dates],
        'DO_노량진': [do_ny.get(d) for d in dates],
        'DO_선유':   [do_sy.get(d) for d in dates],
    })


try:
    df = load_data()
except FileNotFoundError as e:
    st.error(f"📂 **파일을 찾을 수 없습니다**\n\n{e}")
    st.stop()
except Exception as e:
    st.error(f"❌ **데이터 로드 오류**: {e}")
    st.stop()


# ── Hero & KPI ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">🌊 한강 수질 분석 대시보드</div>
  <div class="hero-sub">
    노량진 · 선유 측정소 &nbsp;|&nbsp; 수소이온농도(pH) &amp; 용존산소(DO) 시간별 데이터 (2020년)<br>
    실측 데이터 기반 분석 및 기후변화 시나리오 적용 2050년 수질 예측
  </div>
  <div class="hero-tags">
    <span class="hero-tag">📅 2020.01.01 – 2020.12.31</span>
    <span class="hero-tag">📍 노량진 · 선유</span>
    <span class="hero-tag">⏱ 8,784 시간별 측정</span>
    <span class="hero-tag">🔮 2030 · 2040 · 2050 수질 예측</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="kpi-grid">
  <div class="kpi">
    <div class="kpi-label">pH 연평균 · 노량진</div>
    <div class="kpi-value">7.29</div>
    <div class="kpi-range">범위 6.80 ~ 8.30</div>
  </div>
  <div class="kpi orange">
    <div class="kpi-label">pH 연평균 · 선유</div>
    <div class="kpi-value">7.32</div>
    <div class="kpi-range">범위 6.60 ~ 8.40</div>
  </div>
  <div class="kpi teal">
    <div class="kpi-label">DO 연평균 · 노량진</div>
    <div class="kpi-value">8.46<span class="kpi-unit"> mg/L</span></div>
    <div class="kpi-range">범위 2.1 ~ 12.3</div>
  </div>
  <div class="kpi amber">
    <div class="kpi-label">DO 연평균 · 선유</div>
    <div class="kpi-value">8.26<span class="kpi-unit"> mg/L</span></div>
    <div class="kpi-range">범위 2.0 ~ 12.5</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── 탭 ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 시계열 분석", "📅 월별 패턴", "🔗 상관관계",
    "🔬 수질 해석", "🔮 미래 예측", "📋 수질 정책",
])

COLORS = {
    '노량진_pH': '#2563eb', '선유_pH': '#ea580c',
    '노량진_DO': '#0891b2', '선유_DO': '#d97706',
}
MLBs = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월']


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 : 시계열
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(
        '<p style="font-size:17px; font-weight:700; color:#0c1e3c; '
        'border-left:4px solid #2563eb; padding-left:12px; margin-bottom:6px;">'
        '📈 날짜별 수질 시계열</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-size:14px; color:#4b5563; margin-bottom:20px;">'
        '아래 옵션에서 <b>지표</b>와 <b>측정 지점</b>을 선택하면 해당 그래프만 표시됩니다.</p>',
        unsafe_allow_html=True,
    )

    # ── 컨트롤 ──────────────────────────────────────────────────────────────
    ctrl1, ctrl2, ctrl3 = st.columns([2, 2, 2])
    with ctrl1:
        t1_indicator = st.selectbox(
            "📊 표시할 지표",
            ["DO (용존산소)와 pH 모두", "DO (용존산소)만", "pH만"],
            key="t1_indicator",
        )
    with ctrl2:
        t1_stations = st.multiselect(
            "📍 측정 지점",
            ["노량진", "선유"],
            default=["노량진", "선유"],
            key="t1_stations",
        )
    with ctrl3:
        t1_date = st.date_input(
            "📅 기간 선택",
            value=(df['date'].min().date(), df['date'].max().date()),
            min_value=df['date'].min().date(),
            max_value=df['date'].max().date(),
            key="t1_date",
        )

    if not t1_stations:
        st.warning("⚠️ 측정 지점을 하나 이상 선택해 주세요.")
        st.stop()

    # 날짜 필터
    if isinstance(t1_date, (list, tuple)) and len(t1_date) == 2:
        mask = (df['date'].dt.date >= t1_date[0]) & (df['date'].dt.date <= t1_date[1])
        dff = df[mask].copy()
    else:
        dff = df.copy()

    show_do = t1_indicator in ["DO (용존산소)와 pH 모두", "DO (용존산소)만"]
    show_ph = t1_indicator in ["DO (용존산소)와 pH 모두", "pH만"]
    is_dual = show_do and show_ph

    # ── 컬러 정의 ─────────────────────────────────────────────────────────
    C = {
        '노량진_DO': '#0891b2', '선유_DO': '#d97706',
        '노량진_pH': '#2563eb', '선유_pH': '#ea580c',
    }

    def _line(fig, x, y, name, color, row=None):
        kw = dict(
            x=x, y=y, name=name, mode='lines',
            line=dict(color=color, width=2.2),
            hovertemplate=f"<b>{name}</b><br>날짜: %{{x|%Y-%m-%d}}<br>값: %{{y:.3f}}<extra></extra>",
        )
        if row:
            fig.add_trace(go.Scatter(**kw), row=row, col=1)
        else:
            fig.add_trace(go.Scatter(**kw))

    # ── DO 단독 ───────────────────────────────────────────────────────────
    if show_do and not show_ph:
        st.markdown(
            '<p style="font-size:15px;font-weight:600;color:#0891b2;margin:12px 0 4px;">💧 용존산소 (DO)</p>',
            unsafe_allow_html=True,
        )
        fig_do = go.Figure()
        for s in t1_stations:
            _line(fig_do, dff['date'], dff[f'DO_{s}'], f'{s} DO', C[f'{s}_DO'])
        fig_do.add_hline(
            y=5.0, line_dash='dot', line_color='#dc2626',
            annotation_text='🚨 수생태계 위험 하한 5.0 mg/L',
            annotation_font_color='#dc2626', annotation_font_size=12,
        )
        fig_do.add_hline(
            y=7.5, line_dash='dot', line_color='#16a34a',
            annotation_text='✅ 1등급 기준 7.5 mg/L',
            annotation_font_color='#16a34a', annotation_font_size=12,
        )
        fig_do.update_layout(
            height=400, plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10, r=10, t=20, b=10), hovermode='x unified',
            yaxis=dict(title='DO (mg/L)', title_font=dict(size=13)),
            xaxis=dict(title='날짜', title_font=dict(size=13)),
            legend=dict(orientation='h', y=1.06, xanchor='right', x=1,
                        font=dict(size=13), bgcolor='rgba(255,255,255,0.8)'),
        )
        fig_do.update_xaxes(showgrid=True, gridcolor='#f3f4f6')
        fig_do.update_yaxes(showgrid=True, gridcolor='#f3f4f6')
        st.plotly_chart(fig_do, use_container_width=True,
                        config={'modeBarButtonsToRemove': ['lasso2d','select2d'], 'displaylogo': False})

    # ── pH 단독 ───────────────────────────────────────────────────────────
    elif show_ph and not show_do:
        st.markdown(
            '<p style="font-size:15px;font-weight:600;color:#2563eb;margin:12px 0 4px;">🔵 수소이온농도 (pH)</p>',
            unsafe_allow_html=True,
        )
        fig_ph = go.Figure()
        for s in t1_stations:
            _line(fig_ph, dff['date'], dff[f'pH_{s}'], f'{s} pH', C[f'{s}_pH'])
        fig_ph.add_hline(
            y=6.5, line_dash='dot', line_color='#6b7280',
            annotation_text='환경부 하한 6.5', annotation_font_size=12,
        )
        fig_ph.add_hline(
            y=8.5, line_dash='dot', line_color='#6b7280',
            annotation_text='환경부 상한 8.5', annotation_font_size=12,
        )
        fig_ph.update_layout(
            height=400, plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10, r=10, t=20, b=10), hovermode='x unified',
            yaxis=dict(title='pH', range=[6.0, 9.2], title_font=dict(size=13)),
            xaxis=dict(title='날짜', title_font=dict(size=13)),
            legend=dict(orientation='h', y=1.06, xanchor='right', x=1,
                        font=dict(size=13), bgcolor='rgba(255,255,255,0.8)'),
        )
        fig_ph.update_xaxes(showgrid=True, gridcolor='#f3f4f6')
        fig_ph.update_yaxes(showgrid=True, gridcolor='#f3f4f6')
        st.plotly_chart(fig_ph, use_container_width=True,
                        config={'modeBarButtonsToRemove': ['lasso2d','select2d'], 'displaylogo': False})

    # ── DO + pH 동시 (상하 두 개) ─────────────────────────────────────────
    else:
        # DO 그래프
        st.markdown(
            '<p style="font-size:15px;font-weight:600;color:#0891b2;margin:12px 0 4px;">💧 용존산소 (DO)</p>',
            unsafe_allow_html=True,
        )
        fig_do2 = go.Figure()
        for s in t1_stations:
            _line(fig_do2, dff['date'], dff[f'DO_{s}'], f'{s} DO', C[f'{s}_DO'])
        fig_do2.add_hline(y=5.0, line_dash='dot', line_color='#dc2626',
                          annotation_text='🚨 위험 하한 5.0 mg/L',
                          annotation_font_color='#dc2626', annotation_font_size=12)
        fig_do2.add_hline(y=7.5, line_dash='dot', line_color='#16a34a',
                          annotation_text='✅ 1등급 7.5 mg/L',
                          annotation_font_color='#16a34a', annotation_font_size=12)
        fig_do2.update_layout(
            height=360, plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10, r=10, t=16, b=10), hovermode='x unified',
            yaxis=dict(title='DO (mg/L)', title_font=dict(size=13)),
            xaxis=dict(showticklabels=False),
            legend=dict(orientation='h', y=1.06, xanchor='right', x=1,
                        font=dict(size=13), bgcolor='rgba(255,255,255,0.8)'),
        )
        fig_do2.update_xaxes(showgrid=True, gridcolor='#f3f4f6')
        fig_do2.update_yaxes(showgrid=True, gridcolor='#f3f4f6')
        st.plotly_chart(fig_do2, use_container_width=True,
                        config={'modeBarButtonsToRemove': ['lasso2d','select2d'], 'displaylogo': False})

        # pH 그래프
        st.markdown(
            '<p style="font-size:15px;font-weight:600;color:#2563eb;margin:12px 0 4px;">🔵 수소이온농도 (pH)</p>',
            unsafe_allow_html=True,
        )
        fig_ph2 = go.Figure()
        for s in t1_stations:
            _line(fig_ph2, dff['date'], dff[f'pH_{s}'], f'{s} pH', C[f'{s}_pH'])
        fig_ph2.add_hline(y=6.5, line_dash='dot', line_color='#6b7280',
                          annotation_text='환경부 하한 6.5', annotation_font_size=12)
        fig_ph2.add_hline(y=8.5, line_dash='dot', line_color='#6b7280',
                          annotation_text='환경부 상한 8.5', annotation_font_size=12)
        fig_ph2.update_layout(
            height=360, plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10, r=10, t=16, b=10), hovermode='x unified',
            yaxis=dict(title='pH', range=[6.0, 9.2], title_font=dict(size=13)),
            xaxis=dict(title='날짜', title_font=dict(size=13)),
            legend=dict(orientation='h', y=1.06, xanchor='right', x=1,
                        font=dict(size=13), bgcolor='rgba(255,255,255,0.8)'),
        )
        fig_ph2.update_xaxes(showgrid=True, gridcolor='#f3f4f6')
        fig_ph2.update_yaxes(showgrid=True, gridcolor='#f3f4f6')
        st.plotly_chart(fig_ph2, use_container_width=True,
                        config={'modeBarButtonsToRemove': ['lasso2d','select2d'], 'displaylogo': False})

    st.caption("💡 그래프를 드래그하면 확대, 더블클릭하면 초기화됩니다.")

    with st.expander("📋 원시 데이터 보기 / CSV 다운로드"):
        cols_show = ['date'] + [f'pH_{s}' for s in t1_stations] + [f'DO_{s}' for s in t1_stations]
        disp = dff[cols_show].copy()
        disp['date'] = disp['date'].dt.strftime('%Y-%m-%d')
        disp.columns = (
            ['날짜']
            + [f'pH ({s})' for s in t1_stations]
            + [f'DO ({s}) mg/L' for s in t1_stations]
        )
        st.dataframe(disp, use_container_width=True, height=260)
        st.download_button(
            "⬇️ CSV 다운로드",
            disp.to_csv(index=False).encode('utf-8-sig'),
            file_name="hangang_2020.csv", mime="text/csv",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 : 월별 패턴
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(
        '<p style="font-size:17px; font-weight:700; color:#0c1e3c; '
        'border-left:4px solid #2563eb; padding-left:12px; margin-bottom:6px;">'
        '📅 월별 수질 패턴</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-size:14px; color:#4b5563; margin-bottom:20px;">'
        '월별 평균값과 최솟값·최댓값 범위를 함께 확인할 수 있습니다. '
        '측정 지점을 선택해 원하는 데이터만 비교해 보세요.</p>',
        unsafe_allow_html=True,
    )

    df['month'] = df['date'].dt.month
    monthly = df.groupby('month').agg(
        ph_ny_mean=('pH_노량진', 'mean'), ph_sy_mean=('pH_선유', 'mean'),
        ph_ny_min=('pH_노량진', 'min'),   ph_sy_min=('pH_선유', 'min'),
        ph_ny_max=('pH_노량진', 'max'),   ph_sy_max=('pH_선유', 'max'),
        do_ny_mean=('DO_노량진', 'mean'), do_sy_mean=('DO_선유', 'mean'),
        do_ny_min=('DO_노량진', 'min'),   do_sy_min=('DO_선유', 'min'),
        do_ny_max=('DO_노량진', 'max'),   do_sy_max=('DO_선유', 'max'),
    ).reset_index()

    # ── 지점 선택 컨트롤 ────────────────────────────────────────────────
    t2_stations = st.multiselect(
        "📍 비교할 측정 지점 선택",
        ["노량진", "선유"],
        default=["노량진", "선유"],
        key="t2_stations",
    )
    if not t2_stations:
        st.warning("⚠️ 측정 지점을 하나 이상 선택해 주세요.")
        st.stop()

    # 지점별 색상
    ST_COLORS = {
        'DO': {'노량진': '#0891b2', '선유': '#d97706'},
        'pH': {'노량진': '#2563eb', '선유': '#ea580c'},
    }
    ST_COLS = {
        'DO': {'노량진': ('do_ny_max', 'do_ny_min', 'do_ny_mean'),
               '선유':   ('do_sy_max', 'do_sy_min', 'do_sy_mean')},
        'pH': {'노량진': ('ph_ny_max', 'ph_ny_min', 'ph_ny_mean'),
               '선유':   ('ph_sy_max', 'ph_sy_min', 'ph_sy_mean')},
    }

    def band_trace(x, hi, lo, color_hex, name):
        r, g, b = int(color_hex[1:3], 16), int(color_hex[3:5], 16), int(color_hex[5:7], 16)
        return go.Scatter(
            x=x + x[::-1], y=list(hi) + list(lo)[::-1],
            fill='toself', fillcolor=f'rgba({r},{g},{b},0.10)',
            line=dict(color='rgba(255,255,255,0)'), showlegend=False, name=f'{name} 범위',
            hoverinfo='skip',
        )

    subtab1, subtab2 = st.tabs(["💧 DO (용존산소)", "🔵 pH (수소이온농도)"])

    with subtab1:
        fig_do_m = go.Figure()
        for s in t2_stations:
            c_max, c_min, c_mean = ST_COLS['DO'][s]
            clr = ST_COLORS['DO'][s]
            fig_do_m.add_trace(band_trace(MLBs, monthly[c_max], monthly[c_min], clr, s))
            fig_do_m.add_trace(go.Scatter(
                x=MLBs, y=monthly[c_mean].round(2),
                name=f'{s} 평균', mode='lines+markers',
                line=dict(color=clr, width=2.8),
                marker=dict(size=9),
                hovertemplate=f'<b>{s}</b><br>%{{x}}<br>평균 DO: %{{y:.2f}} mg/L<extra></extra>',
            ))
        fig_do_m.add_hline(
            y=5.0, line_dash='dot', line_color='#dc2626',
            annotation_text='🚨 수생태계 위험 하한 5.0 mg/L',
            annotation_font_color='#dc2626', annotation_font_size=12,
        )
        fig_do_m.add_hline(
            y=7.5, line_dash='dot', line_color='#16a34a',
            annotation_text='✅ 1등급 기준 7.5 mg/L',
            annotation_font_color='#16a34a', annotation_font_size=12,
        )
        fig_do_m.update_layout(
            height=400, plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10, r=10, t=20, b=10),
            yaxis=dict(range=[0, 14], title='DO (mg/L)', title_font=dict(size=14),
                       tickfont=dict(size=12)),
            xaxis=dict(title='월', title_font=dict(size=14), tickfont=dict(size=13)),
            legend=dict(orientation='h', y=1.08, xanchor='right', x=1,
                        font=dict(size=13), bgcolor='rgba(255,255,255,0.8)'),
            hovermode='x unified',
        )
        fig_do_m.update_xaxes(showgrid=True, gridcolor='#f3f4f6')
        fig_do_m.update_yaxes(showgrid=True, gridcolor='#f3f4f6')
        st.plotly_chart(fig_do_m, use_container_width=True, config={'displaylogo': False})
        st.caption("💡 색 밴드는 월별 최솟값~최댓값 범위를 나타냅니다.")

    with subtab2:
        fig_ph_m = go.Figure()
        for s in t2_stations:
            c_max, c_min, c_mean = ST_COLS['pH'][s]
            clr = ST_COLORS['pH'][s]
            fig_ph_m.add_trace(band_trace(MLBs, monthly[c_max], monthly[c_min], clr, s))
            fig_ph_m.add_trace(go.Scatter(
                x=MLBs, y=monthly[c_mean].round(3),
                name=f'{s} 평균', mode='lines+markers',
                line=dict(color=clr, width=2.8),
                marker=dict(size=9),
                hovertemplate=f'<b>{s}</b><br>%{{x}}<br>평균 pH: %{{y:.3f}}<extra></extra>',
            ))
        fig_ph_m.add_hline(
            y=6.5, line_dash='dot', line_color='#6b7280',
            annotation_text='환경부 하한 6.5', annotation_font_size=12,
        )
        fig_ph_m.add_hline(
            y=8.5, line_dash='dot', line_color='#6b7280',
            annotation_text='환경부 상한 8.5', annotation_font_size=12,
        )
        fig_ph_m.update_layout(
            height=400, plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10, r=10, t=20, b=10),
            yaxis=dict(range=[6.0, 9.2], title='pH', title_font=dict(size=14),
                       tickfont=dict(size=12)),
            xaxis=dict(title='월', title_font=dict(size=14), tickfont=dict(size=13)),
            legend=dict(orientation='h', y=1.08, xanchor='right', x=1,
                        font=dict(size=13), bgcolor='rgba(255,255,255,0.8)'),
            hovermode='x unified',
        )
        fig_ph_m.update_xaxes(showgrid=True, gridcolor='#f3f4f6')
        fig_ph_m.update_yaxes(showgrid=True, gridcolor='#f3f4f6')
        st.plotly_chart(fig_ph_m, use_container_width=True, config={'displaylogo': False})
        st.caption("💡 색 밴드는 월별 최솟값~최댓값 범위를 나타냅니다.")

    # 수치표
    st.markdown(
        '<p style="font-size:16px; font-weight:700; color:#0c1e3c; '
        'border-left:4px solid #2563eb; padding-left:12px; margin:28px 0 12px;">'
        '📋 월별 상세 수치표</p>',
        unsafe_allow_html=True,
    )
    tbl_cols = {'월': MLBs}
    for s in t2_stations:
        if 'DO' in ['DO']:
            tbl_cols[f'DO {s} 평균'] = monthly[ST_COLS['DO'][s][2]].round(2)
            tbl_cols[f'DO {s} 최솟값'] = monthly[ST_COLS['DO'][s][1]].round(2)
        tbl_cols[f'pH {s} 평균'] = monthly[ST_COLS['pH'][s][2]].round(3)
    st.dataframe(pd.DataFrame(tbl_cols), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 : 상관관계
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown(
        '<p style="font-size:17px; font-weight:700; color:#0c1e3c; '
        'border-left:4px solid #2563eb; padding-left:12px; margin-bottom:6px;">'
        '🔗 pH – DO 상관관계 분석</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-size:14px; color:#4b5563; margin-bottom:20px;">'
        'x축은 pH, y축은 DO(용존산소)입니다. 각 점은 하루의 일평균 데이터이며, '
        '점들이 오른쪽 위 방향으로 모일수록 두 지표가 함께 높아지는 경향이 강하다는 뜻입니다.</p>',
        unsafe_allow_html=True,
    )

    # ── 산점도 ────────────────────────────────────────────────────────────
    fig_s = go.Figure()
    corrs = {}
    for nm, pc, dc, clr in [
        ('노량진', 'pH_노량진', 'DO_노량진', '#2563eb'),
        ('선유',   'pH_선유',   'DO_선유',   '#ea580c'),
    ]:
        tmp = df[[pc, dc, 'date']].dropna()
        fig_s.add_trace(go.Scatter(
            x=tmp[pc], y=tmp[dc], mode='markers', name=f'{nm} 일별 데이터',
            marker=dict(color=clr, size=6, opacity=0.45),
            hovertemplate=(
                f"<b>{nm}</b><br>"
                f"pH: %{{x:.3f}}<br>"
                f"DO: %{{y:.3f}} mg/L<extra></extra>"
            ),
        ))
        z = np.polyfit(tmp[pc], tmp[dc], 1)
        xr = np.linspace(tmp[pc].min(), tmp[pc].max(), 100)
        fig_s.add_trace(go.Scatter(
            x=xr, y=np.polyval(z, xr), mode='lines',
            name=f'{nm} 추세선 (r={tmp[[pc,dc]].corr().iloc[0,1]:.3f})',
            line=dict(color=clr, width=2.5, dash='dash'),
        ))
        corrs[nm] = tmp[[pc, dc]].corr().iloc[0, 1]

    fig_s.update_layout(
        height=440, plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(
            title='pH (일평균)',
            title_font=dict(size=14),
            tickfont=dict(size=12),
            showgrid=True, gridcolor='#f3f4f6',
        ),
        yaxis=dict(
            title='DO mg/L (일평균)',
            title_font=dict(size=14),
            tickfont=dict(size=12),
            showgrid=True, gridcolor='#f3f4f6',
        ),
        legend=dict(
            orientation='h', y=1.06, xanchor='right', x=1,
            font=dict(size=13), bgcolor='rgba(255,255,255,0.85)',
        ),
    )
    st.plotly_chart(fig_s, use_container_width=True, config={'displaylogo': False})

    # ── 상관계수 카드 ─────────────────────────────────────────────────────
    m1, m2 = st.columns(2)
    with m1:
        st.metric(
            label="노량진 피어슨 상관계수 (r)",
            value=f"{corrs['노량진']:.3f}",
            delta="강한 양의 상관관계",
        )
    with m2:
        st.metric(
            label="선유 피어슨 상관계수 (r)",
            value=f"{corrs['선유']:.3f}",
            delta="중간-강한 양의 상관관계",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 그래프 읽는 법 ────────────────────────────────────────────────────
    st.markdown(
        '<p style="font-size:16px; font-weight:700; color:#1e3a5f; margin-bottom:10px;">'
        '📌 이 그래프를 읽는 방법</p>',
        unsafe_allow_html=True,
    )
    st.markdown("""
    <div style="background:#eff6ff; border-left:4px solid #2563eb; border-radius:0 10px 10px 0;
                padding:16px 20px; margin-bottom:16px; font-size:14px; line-height:1.85; color:#1e293b;">
        <b>각 점(●) 하나 = 하루의 측정값</b><br>
        x축(가로)은 그날의 pH 평균, y축(세로)은 DO 평균입니다.<br><br>
        <b>추세선(점선)</b>은 전체 데이터의 경향을 한 줄로 요약한 것입니다.
        추세선이 오른쪽 위를 향할수록 "pH가 높은 날은 DO도 높다"는 경향이 뚜렷하다는 뜻입니다.<br><br>
        <b>상관계수 r</b>은 -1에서 +1 사이의 값입니다.
        +1에 가까울수록 두 지표가 완벽하게 같이 움직이고, 0에 가까울수록 관련이 없습니다.
        저희 데이터의 경우 노량진 0.767, 선유 0.648로 <b>두 지표가 꽤 강하게 연동</b>된다는 것을 보여줍니다.
    </div>
    """, unsafe_allow_html=True)

    # ── 상관관계가 의미하는 것 ────────────────────────────────────────────
    st.markdown(
        '<p style="font-size:16px; font-weight:700; color:#1e3a5f; margin-bottom:10px;">'
        '🌊 이 상관관계가 의미하는 것</p>',
        unsafe_allow_html=True,
    )
    st.markdown("""
    <div style="background:#f0fdfa; border-left:4px solid #0891b2; border-radius:0 10px 10px 0;
                padding:16px 20px; margin-bottom:14px; font-size:14px; line-height:1.9; color:#1e293b;">
        pH와 DO는 서로 별개의 지표처럼 보이지만, 사실 <b>강 생태계의 생물학적 활동이라는 하나의 공통 원인</b>으로
        함께 움직입니다.<br><br>
        <b>🌸 봄 (3–4월) — pH ↑, DO ↑</b><br>
        수온이 오르면 식물성 플랑크톤이 폭발적으로 증식하고 활발하게 광합성을 합니다.
        광합성은 물속의 이산화탄소(CO₂)를 소비하는데, CO₂가 줄면 물이 알칼리성으로 변해 pH가 올라갑니다.
        동시에 광합성의 산물로 산소(O₂)가 생성되므로 DO도 함께 올라갑니다.<br><br>
        <b>☀️ 여름 (6–8월) — pH ↓, DO ↓</b><br>
        봄에 번성했던 플랑크톤이 죽어 분해되면서 박테리아가 산소를 대량으로 소비합니다.
        이 과정에서 CO₂가 다시 방출되어 pH가 낮아지고, 산소도 급격히 줄어 DO가 동반 하락합니다.
        이것이 한강에서 여름철마다 DO 위기가 반복되는 핵심 이유입니다.<br><br>
        <b>❄️ 겨울 (11–12월) — pH 안정, DO ↑</b><br>
        수온이 낮아지면 생물 활동이 줄고, 차가운 물은 산소를 더 많이 녹일 수 있어 DO가 연중 최고치를 기록합니다.
    </div>
    """, unsafe_allow_html=True)

    # ── 두 지점 차이 설명 ────────────────────────────────────────────────
    st.markdown("""
    <div style="background:#fff7ed; border-left:4px solid #f97316; border-radius:0 10px 10px 0;
                padding:16px 20px; font-size:14px; line-height:1.85; color:#1e293b;">
        <b>📍 노량진(r=0.767)이 선유(r=0.648)보다 상관계수가 높은 이유</b><br><br>
        선유는 한강 하류 방향으로 유속이 느리고 퇴적물·유기물이 더 많이 쌓이는 지점입니다.
        퇴적 유기물은 플랑크톤 활동과는 별도로 DO를 추가로 낮추는 역할을 합니다.
        즉 선유에서는 pH와 무관한 요인(퇴적물 분해)이 DO를 더 낮추기 때문에,
        pH와 DO의 연동이 노량진만큼 깔끔하게 나타나지 않습니다.<br><br>
        <b>결론:</b> 두 지점 모두 pH가 높은 날은 DO도 높고, pH가 낮은 날은 DO도 낮은 경향이 뚜렷합니다.
        이 패턴을 이용하면 pH 데이터만으로도 DO 위험 상황을 어느 정도 예측할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)



# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 : 수질 해석 (달력형 — 첨부 파일 버전)
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    # ── 월별 실제 데이터 집계 ─────────────────────────────────────────────────
    df['month'] = df['date'].dt.month
    cal_monthly = df.groupby('month').agg(
        do_ny=('DO_노량진', 'mean'), do_sy=('DO_선유',   'mean'),
        ph_ny=('pH_노량진', 'mean'), ph_sy=('pH_선유',   'mean'),
        do_ny_min=('DO_노량진', 'min'), do_sy_min=('DO_선유', 'min'),
    ).reset_index()

    t4_station = st.radio(
        "기준 측정소", ["노량진", "선유", "두 지점 평균"],
        horizontal=True, key="t4_station"
    )

    def get_do(row):
        if t4_station == "노량진": return row['do_ny']
        elif t4_station == "선유": return row['do_sy']
        else: return (row['do_ny'] + row['do_sy']) / 2

    def get_ph(row):
        if t4_station == "노량진": return row['ph_ny']
        elif t4_station == "선유": return row['ph_sy']
        else: return (row['ph_ny'] + row['ph_sy']) / 2

    def do_grade_color(v):
        if v >= 7.5:   return "#22c55e", "#dcfce7", "🟢 1등급",   100
        elif v >= 5.0: return "#f59e0b", "#fef3c7", "🟡 2~3등급", int((v-5)/2.5*100)
        elif v >= 2.0: return "#f97316", "#ffedd5", "🟠 4등급",   int((v-2)/3*100)
        else:           return "#ef4444", "#fee2e2", "🔴 5등급↓",  10

    def ph_color(v):
        if 7.0 <= v <= 8.0: return "#2563eb"
        elif v > 8.0:        return "#7c3aed"
        else:                return "#dc2626"

    MONTH_NAMES = ['','JAN','FEB','MAR','APR','MAY','JUN',
                   'JUL','AUG','SEP','OCT','NOV','DEC']
    MONTH_KO    = ['','1월','2월','3월','4월','5월','6월',
                   '7월','8월','9월','10월','11월','12월']
    EVENTS = {
        1:  ("❄️ DO 최고",   "#dbeafe","#1d4ed8"),
        2:  ("❄️ DO 안정",   "#dbeafe","#1d4ed8"),
        3:  ("🌸 pH 급등",   "#fae8ff","#9333ea"),
        4:  ("🌸 pH 최고",   "#fae8ff","#9333ea"),
        5:  ("⚠️ DO 하락",   "#fef3c7","#b45309"),
        6:  ("🚨 DO 위기",   "#fee2e2","#dc2626"),
        7:  ("🚨 DO 최저",   "#fee2e2","#dc2626"),
        8:  ("🚨 센서 결측", "#fee2e2","#dc2626"),
        9:  ("🍂 DO 회복",   "#ffedd5","#c2410c"),
        10: ("✅ 1등급",      "#dcfce7","#15803d"),
        11: ("✅ 최적 환경", "#dcfce7","#15803d"),
        12: ("❄️ DO 최고치", "#dbeafe","#1d4ed8"),
    }
    do_max = 12.5

    # ── 달력 HTML 생성 ────────────────────────────────────────────────────────
    cal_html = '<div class="cal-wrap">'
    cal_html += f"""
    <div class="cal-header">
        <div>
            <div class="cal-header-title">📅 2020 한강 수질 월별 달력</div>
            <div class="cal-header-sub">기준 측정소: {t4_station} · pH 및 DO(mg/L) 월평균</div>
        </div>
        <div class="cal-legend">
            <div class="cal-legend-item"><div class="cal-legend-dot" style="background:#22c55e"></div>1등급 ≥7.5</div>
            <div class="cal-legend-item"><div class="cal-legend-dot" style="background:#f59e0b"></div>2~3등급 ≥5.0</div>
            <div class="cal-legend-item"><div class="cal-legend-dot" style="background:#f97316"></div>4등급 ≥2.0</div>
            <div class="cal-legend-item"><div class="cal-legend-dot" style="background:#ef4444"></div>5등급↓</div>
        </div>
    </div>
    <div class="cal-grid">"""

    for _, row in cal_monthly.iterrows():
        m = int(row['month'])
        do_v = get_do(row)
        ph_v = get_ph(row)
        do_col, do_bg, grade_label, bar_pct = do_grade_color(do_v)
        ph_col = ph_color(ph_v)
        ev_label, ev_bg, ev_col = EVENTS.get(m, ("", "#f3f4f6", "#64748b"))
        bar_w = int(do_v / do_max * 100)
        cal_html += f"""
        <div class="cal-month">
            <div class="cal-month-name">{MONTH_NAMES[m]} · {MONTH_KO[m]}</div>
            <div class="cal-vals">
                <div class="cal-val-row">
                    <span class="cal-val-label">DO</span>
                    <span><span class="cal-val-num" style="color:{do_col}">{do_v:.2f}</span><span class="cal-val-unit">mg/L</span></span>
                </div>
                <div class="cal-do-bar-wrap"><div class="cal-do-bar" style="width:{bar_w}%;background:{do_col}"></div></div>
                <div class="cal-val-row">
                    <span class="cal-val-label">pH</span>
                    <span><span class="cal-val-num" style="color:{ph_col}">{ph_v:.2f}</span></span>
                </div>
            </div>
            <span class="cal-tag" style="background:{ev_bg};color:{ev_col}">{ev_label}</span>
        </div>"""

    cal_html += '</div></div>'
    st.markdown(cal_html, unsafe_allow_html=True)

    # ── 계절별 인사이트 ────────────────────────────────────────────────────────
    st.markdown('<div class="sec-hd">계절별 수질 해석</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="cal-insight-grid">
        <div class="cal-insight-card spring">
            <div class="cal-insight-title">🌸 봄 (3–5월) — pH 급등 구간</div>
            <div class="cal-insight-body">수온 상승 → 플랑크톤 폭발 증식 → 광합성 왕성 → CO₂ 소비 → pH 상승의 연쇄.
            노량진 <b>8.3</b>, 선유 <b>8.4</b>로 연중 최고치를 기록합니다.
            봄철 오후 14–18시에 일중 pH 편차가 최대 <b>1.0 이상</b> 벌어집니다.</div>
        </div>
        <div class="cal-insight-card summer">
            <div class="cal-insight-title">☀️ 여름 (6–8월) — DO 위기 구간</div>
            <div class="cal-insight-body">노량진 6월 평균 DO <b>5.95 mg/L</b>, 선유 <b>5.51 mg/L</b>로 급락.
            순간 최솟값 노량진 <b>2.1</b>, 선유 <b>2.0 mg/L</b>.
            수온 상승 → 산소 용해도 감소(20°C: 9.1 → 30°C: 7.5 mg/L).
            플랑크톤 사체 분해 시 박테리아 대량 산소 소비가 복합적으로 작용합니다.
            8월 선유 센서 결측률 <b>58%</b> 주의.</div>
        </div>
        <div class="cal-insight-card autumn">
            <div class="cal-insight-title">🍂 가을 (9–10월) — 회복 구간</div>
            <div class="cal-insight-body">수온 하강 → DO 서서히 회복. 10월부터 DO ≥ 7.5 mg/L 달성,
            환경부 <b>1등급</b> 수준으로 회복됩니다.
            pH도 7.4–7.5로 중성 범위에 안정되며 수생태계에 쾌적한 환경입니다.</div>
        </div>
        <div class="cal-insight-card winter">
            <div class="cal-insight-title">❄️ 겨울 (11–12월) — DO 최고 구간</div>
            <div class="cal-insight-body">노량진 12월 평균 <b>11.17 mg/L</b>, 선유 <b>10.91 mg/L</b>로 연중 최고.
            저수온일수록 기체 용해도가 높아져 DO가 포화 상태를 유지합니다.
            pH는 7.4–7.5로 가장 안정적이며, 연중 수질이 가장 쾌적한 시기입니다.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 환경부 등급 요약 ──────────────────────────────────────────────────────
    st.markdown('<div class="sec-hd" style="margin-top:24px">환경부 수질 등급 기준 대조</div>', unsafe_allow_html=True)
    grade_cols = st.columns(4)
    grades = [
        ("🟢 1등급","매우 좋음","DO ≥ 7.5","pH 6.5–8.5","상수원·자연보전","10월–4월","#dcfce7","#15803d"),
        ("🟡 2~3등급","좋음·보통","DO ≥ 5.0","pH 6.5–8.5","정수처리·농업용수","봄·가을","#fef3c7","#b45309"),
        ("🟠 4등급","나쁨","DO ≥ 2.0","pH 6.0–8.5","공업용수","여름 순간값","#ffedd5","#c2410c"),
        ("🔴 5등급↓","매우 나쁨","DO < 2.0","pH <6.0 or >8.5","용도 제한","극한 상황","#fee2e2","#b91c1c"),
    ]
    for col, (grade, status, do_crit, ph_crit, use, when, bg, fc) in zip(grade_cols, grades):
        with col:
            st.markdown(f"""
            <div style="background:{bg};border-radius:12px;padding:16px 18px">
                <div style="font-size:16px;font-weight:900;color:{fc};margin-bottom:4px">{grade}</div>
                <div style="font-size:11px;font-weight:700;color:{fc};margin-bottom:10px;opacity:0.8">{status}</div>
                <div style="font-size:12px;color:#374151;line-height:1.8">
                    <b>DO:</b> {do_crit}<br><b>pH:</b> {ph_crit}<br>
                    <b>용도:</b> {use}<br><b>2020 한강:</b> {when}
                </div>
            </div>
            """, unsafe_allow_html=True)



# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 : 미래 예측 (슬라이드형 — 첨부 파일 버전)
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    import json
    import numpy as np
    import streamlit.components.v1 as components

    SCENARIOS = {
        'SSP2-4.5': {'temp_2050': 1.5, 'do_per_c': 0.20, 'summer_penalty': 0.08, 'ph_per_yr': -0.002},
        'SSP5-8.5': {'temp_2050': 3.0, 'do_per_c': 0.22, 'summer_penalty': 0.18, 'ph_per_yr': -0.005},
    }
    BASE = {'do_ny': 8.463, 'do_sy': 8.260, 'ph_ny': 7.287, 'ph_sy': 7.317}
    future_years_arr = list(range(2020, 2051))

    def forecast(base, sc, kind='do'):
        vals = []
        for y in future_years_arr:
            frac = (y - 2020) / 30
            if kind == 'do':
                val = base - sc['do_per_c'] * sc['temp_2050'] * frac - sc['summer_penalty'] * frac
            else:
                val = base + sc['ph_per_yr'] * (y - 2020)
            vals.append(round(val, 3))
        return vals

    sc245 = SCENARIOS['SSP2-4.5']; sc585 = SCENARIOS['SSP5-8.5']
    do_ny_245 = forecast(BASE['do_ny'], sc245, 'do')
    do_sy_245 = forecast(BASE['do_sy'], sc245, 'do')
    ph_ny_245 = forecast(BASE['ph_ny'], sc245, 'ph')
    ph_sy_245 = forecast(BASE['ph_sy'], sc245, 'ph')
    do_ny_585 = forecast(BASE['do_ny'], sc585, 'do')
    do_sy_585 = forecast(BASE['do_sy'], sc585, 'do')
    ph_ny_585 = forecast(BASE['ph_ny'], sc585, 'ph')
    ph_sy_585 = forecast(BASE['ph_sy'], sc585, 'ph')

    KEY_YEARS  = [2026, 2030, 2040, 2050]
    KEY_LABELS = ["현재", "단기 목표", "중기 전환점", "장기 목표"]
    KEY_DESCS  = [
        "기후변화 영향이 서서히 시작되는 시점",
        "단기 정책(폭기·모니터링) 효과가 나타나는 시점",
        "하수처리장 고도화·생태습지 정책 완료 후의 수질",
        "기후변화 대응 정책의 최종 성과가 결정되는 시점",
    ]
    KEY_ICONS = ["📍", "⚡", "🔧", "🌍"]

    slides_data = []
    for i, yr in enumerate(KEY_YEARS):
        idx = yr - 2020
        v245n = do_ny_245[idx]; v245s = do_sy_245[idx]
        v585n = do_ny_585[idx]; v585s = do_sy_585[idx]
        p245n = ph_ny_245[idx]; p245s = ph_sy_245[idx]
        p585n = ph_ny_585[idx]; p585s = ph_sy_585[idx]
        dn245 = v245n - BASE['do_ny']; dn585 = v585n - BASE['do_ny']

        def grade(v):
            if v >= 7.5: return "#22c55e"
            elif v >= 5.0: return "#f59e0b"
            elif v >= 2.0: return "#f97316"
            else: return "#ef4444"

        warn_v = min(v245n, v585n)
        if warn_v < 5.0:   state="🚨 위험 임박"; sc_key="danger"; sc_color="#dc2626"
        elif warn_v < 6.5: state="⚠️ 주의 필요"; sc_key="caution"; sc_color="#d97706"
        else:               state="✅ 양호";       sc_key="ok";      sc_color="#16a34a"

        warn_msgs = {
            "ok":      f"✅ {yr}년 DO는 두 시나리오 모두 안전 범위(5.0 mg/L)를 유지합니다.",
            "caution": f"⚠️ {yr}년 일부 시나리오에서 DO가 경계 수준(6.5 mg/L)에 근접합니다.",
            "danger":  f"🚨 {yr}년 SSP5-8.5에서 DO가 위험 임계치(5.0 mg/L)에 근접합니다.",
        }
        slides_data.append({
            "year": yr, "label": KEY_LABELS[i], "desc": KEY_DESCS[i], "icon": KEY_ICONS[i],
            "state": state, "state_color": sc_color, "warn_cls": sc_key,
            "warn_msg": warn_msgs[sc_key],
            "v245n": v245n, "v245s": v245s, "p245n": p245n, "p245s": p245s,
            "v585n": v585n, "v585s": v585s, "p585n": p585n, "p585s": p585s,
            "dn245": dn245, "dn585": dn585,
            "c245n": grade(v245n), "c245s": grade(v245s),
            "c585n": grade(v585n), "c585s": grade(v585s),
            "bar245n": int(v245n/12.5*100), "bar245s": int(v245s/12.5*100),
            "bar585n": int(v585n/12.5*100), "bar585s": int(v585s/12.5*100),
        })

    slides_json = json.dumps(slides_data, ensure_ascii=False)

    components.html(f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
*{{box-sizing:border-box;margin:0;padding:0;font-family:'Noto Sans KR',sans-serif}}
body{{background:#f8fafc;padding:16px}}
.ctrl{{display:flex;gap:10px;align-items:center;margin-bottom:14px}}
.ap-btn{{padding:8px 20px;border-radius:8px;border:none;cursor:pointer;font-size:13px;font-weight:700;transition:all 0.2s;background:#2563eb;color:white}}
.ap-btn.playing{{background:#dc2626}}
.scen-sel{{padding:7px 12px;border-radius:8px;border:1px solid #e2e8f0;font-size:13px;font-weight:600;color:#374151;background:white;cursor:pointer}}
.step-info{{margin-left:auto;font-size:12px;color:#94a3b8;font-weight:600}}
.prog-wrap{{height:4px;background:#e2e8f0;border-radius:99px;overflow:hidden;margin-bottom:12px}}
.prog-bar{{height:100%;background:#2563eb;border-radius:99px;width:0%}}
.timeline{{background:#0c1e3c;border-radius:14px 14px 0 0;padding:16px 24px;display:flex;align-items:center}}
.tl-step{{flex:1;display:flex;flex-direction:column;align-items:center;position:relative}}
.tl-step:not(:last-child)::after{{content:'';position:absolute;top:13px;left:50%;width:100%;height:2px;background:rgba(255,255,255,0.15);z-index:0}}
.tl-dot{{width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;position:relative;z-index:1;border:2px solid rgba(255,255,255,0.2);color:rgba(255,255,255,0.4);transition:all 0.4s ease}}
.tl-dot.active{{background:#2563eb;border-color:#60a5fa;color:#fff;box-shadow:0 0 0 3px rgba(37,99,235,0.4)}}
.tl-dot.passed{{background:#1e3a8a;border-color:#3b82f6;color:#93c5fd}}
.tl-lbl{{font-size:10px;color:rgba(255,255,255,0.35);margin-top:5px;font-weight:700;transition:color 0.4s}}
.tl-lbl.active{{color:#93c5fd}}.tl-lbl.passed{{color:rgba(255,255,255,0.6)}}
.slide-wrap{{background:white;border-radius:0 0 14px 14px;padding:24px 28px;min-height:260px;position:relative;overflow:hidden}}
.slide{{position:absolute;top:24px;left:28px;right:28px;opacity:0;transform:translateX(40px);transition:opacity 0.5s ease,transform 0.5s ease;pointer-events:none}}
.slide.active{{opacity:1;transform:translateX(0);pointer-events:auto;position:relative;top:auto;left:auto;right:auto}}
.yr-hd{{display:flex;align-items:flex-end;gap:14px;margin-bottom:8px}}
.yr-num{{font-size:52px;font-weight:900;letter-spacing:-2px;color:#0c1e3c;line-height:1}}
.yr-sub{{padding-bottom:6px}}
.yr-lbl{{font-size:10px;font-weight:800;letter-spacing:.12em;color:#94a3b8;text-transform:uppercase;margin-bottom:3px}}
.yr-state{{font-size:15px;font-weight:800}}
.yr-desc{{font-size:13px;color:#64748b;margin-bottom:18px;line-height:1.7}}
.metrics{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px}}
.mcard{{background:#f8fafc;border-radius:12px;padding:16px 18px;border:1px solid #f1f5f9}}
.mcard-top{{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}}
.mcard-title{{font-size:10.5px;font-weight:800;letter-spacing:.1em;color:#94a3b8;text-transform:uppercase}}
.mbadge{{font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px}}
.mrow{{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px}}
.mstation{{font-size:12px;color:#64748b;font-weight:600}}
.mval{{font-size:20px;font-weight:900;line-height:1}}
.munit{{font-size:10px;color:#94a3b8}}
.mdelta{{font-size:11px;color:#64748b;margin-left:4px}}
.mbar-w{{height:5px;background:#e2e8f0;border-radius:99px;margin:4px 0 10px;overflow:hidden}}
.mbar{{height:100%;border-radius:99px;transition:width 0.6s ease}}
.mph{{font-size:11px;color:#64748b;margin-top:6px}}
.warn{{border-radius:9px;padding:10px 14px;font-size:13px;font-weight:600;line-height:1.6}}
.warn.ok{{background:#f0fdf4;color:#166534;border:1px solid #86efac}}
.warn.caution{{background:#fffbeb;color:#92400e;border:1px solid #fcd34d}}
.warn.danger{{background:#fff1f2;color:#9f1239;border:1px solid #fda4af}}
</style></head><body>
<div class="ctrl">
  <button class="ap-btn" id="apBtn" onclick="togglePlay()">⏵ 자동재생</button>
  <select class="scen-sel" id="scenSel" onchange="renderSlide()">
    <option value="both">양쪽 비교</option>
    <option value="245">SSP2-4.5</option>
    <option value="585">SSP5-8.5</option>
  </select>
  <span class="step-info" id="stepInfo">1 / 4</span>
</div>
<div class="prog-wrap"><div class="prog-bar" id="progBar"></div></div>
<div class="timeline" id="timeline"></div>
<div class="slide-wrap" id="slideWrap"></div>
<script>
const SLIDES={slides_json};
let cur=0,playing=false,progInterval=null,progPct=0;
function togglePlay(){{playing=!playing;const btn=document.getElementById('apBtn');
  if(playing){{btn.textContent='⏹ 정지';btn.className='ap-btn playing';
    if(cur>=SLIDES.length-1){{cur=0;goTo(0);}}startProgress();}}
  else{{btn.textContent='⏵ 자동재생';btn.className='ap-btn';stopProgress();}}}}
function startProgress(){{progPct=0;const bar=document.getElementById('progBar');
  bar.style.transition='none';bar.style.width='0%';clearInterval(progInterval);
  progInterval=setInterval(()=>{{progPct++;bar.style.width=Math.min(progPct,100)+'%';
    if(progPct>=100){{progPct=0;bar.style.width='0%';nextSlide();}}}},50);}}
function stopProgress(){{clearInterval(progInterval);progInterval=null;
  document.getElementById('progBar').style.width='0%';}}
function nextSlide(){{if(cur<SLIDES.length-1){{goTo(cur+1);}}
  else{{playing=false;stopProgress();const btn=document.getElementById('apBtn');
    btn.textContent='⏵ 자동재생';btn.className='ap-btn';}}}}
function goTo(idx){{cur=idx;renderTimeline();renderSlide();
  document.getElementById('stepInfo').textContent=(idx+1)+' / '+SLIDES.length;}}
function renderTimeline(){{const tl=document.getElementById('timeline');
  tl.innerHTML=SLIDES.map((s,i)=>{{const cls=i===cur?'active':(i<cur?'passed':'');
    return `<div class="tl-step"><div class="tl-dot ${{cls}}">${{i+1}}</div>
      <div class="tl-lbl ${{cls}}">${{s.year}}</div></div>`;}}).join('');}}
function renderSlide(){{const s=SLIDES[cur];const mode=document.getElementById('scenSel').value;
  const wrap=document.getElementById('slideWrap');let cards='';
  if(mode==='both'||mode==='245'){{cards+=`<div class="mcard">
    <div class="mcard-top"><span class="mcard-title">DO · SSP2-4.5</span>
      <span class="mbadge" style="background:#dbeafe;color:#1d4ed8">중위</span></div>
    <div class="mrow"><span class="mstation">노량진</span>
      <span><span class="mval" style="color:${{s.c245n}}">${{s.v245n.toFixed(2)}}</span>
      <span class="munit"> mg/L</span>
      <span class="mdelta">(${{s.dn245>=0?'+':''}}${{s.dn245.toFixed(2)}})</span></span></div>
    <div class="mbar-w"><div class="mbar" style="width:${{s.bar245n}}%;background:${{s.c245n}}"></div></div>
    <div class="mrow"><span class="mstation">선유</span>
      <span><span class="mval" style="color:${{s.c245s}}">${{s.v245s.toFixed(2)}}</span><span class="munit"> mg/L</span></span></div>
    <div class="mbar-w"><div class="mbar" style="width:${{s.bar245s}}%;background:${{s.c245s}}"></div></div>
    <div class="mph">pH 노량진 <b style="color:#2563eb">${{s.p245n.toFixed(3)}}</b> | 선유 <b style="color:#2563eb">${{s.p245s.toFixed(3)}}</b></div>
    </div>`;}}
  if(mode==='both'||mode==='585'){{cards+=`<div class="mcard">
    <div class="mcard-top"><span class="mcard-title">DO · SSP5-8.5</span>
      <span class="mbadge" style="background:#fee2e2;color:#b91c1c">고위</span></div>
    <div class="mrow"><span class="mstation">노량진</span>
      <span><span class="mval" style="color:${{s.c585n}}">${{s.v585n.toFixed(2)}}</span>
      <span class="munit"> mg/L</span>
      <span class="mdelta">(${{s.dn585>=0?'+':''}}${{s.dn585.toFixed(2)}})</span></span></div>
    <div class="mbar-w"><div class="mbar" style="width:${{s.bar585n}}%;background:${{s.c585n}}"></div></div>
    <div class="mrow"><span class="mstation">선유</span>
      <span><span class="mval" style="color:${{s.c585s}}">${{s.v585s.toFixed(2)}}</span><span class="munit"> mg/L</span></span></div>
    <div class="mbar-w"><div class="mbar" style="width:${{s.bar585s}}%;background:${{s.c585s}}"></div></div>
    <div class="mph">pH 노량진 <b style="color:#dc2626">${{s.p585n.toFixed(3)}}</b> | 선유 <b style="color:#dc2626">${{s.p585s.toFixed(3)}}</b></div>
    </div>`;}}
  wrap.innerHTML=`<div class="slide active">
    <div class="yr-hd"><div class="yr-num">${{s.year}}</div>
      <div class="yr-sub"><div class="yr-lbl">IPCC 예측 시점 · ${{s.label}}</div>
      <div class="yr-state" style="color:${{s.state_color}}">${{s.state}}</div></div></div>
    <div class="yr-desc">${{s.icon}} ${{s.desc}}</div>
    <div class="metrics">${{cards}}</div>
    <div class="warn ${{s.warn_cls}}">${{s.warn_msg}}</div></div>`;}}
renderTimeline();renderSlide();
</script></body></html>
""", height=560)

    st.divider()
    with st.expander("📈 2020–2050 전체 DO 추이 그래프 보기", expanded=False):
        future_years_np = np.arange(2020, 2051)
        fig_full = go.Figure()
        def make_band(years, vals, hex_color, label):
            r,g,b = int(hex_color[1:3],16),int(hex_color[3:5],16),int(hex_color[5:7],16)
            noise = np.array([0.3+0.5*(y-2020)/30 for y in years])
            v = np.array(vals)
            band = go.Scatter(x=list(years)+list(years[::-1]),y=list(v+noise)+list((v-noise)[::-1]),
                              fill='toself',fillcolor=f'rgba({r},{g},{b},0.08)',
                              line=dict(color='rgba(255,255,255,0)'),showlegend=False)
            line = go.Scatter(x=years,y=np.round(v,3),name=label,mode='lines',
                              line=dict(color=hex_color,width=2.2))
            return band, line
        b1,l1=make_band(future_years_np,do_ny_245,'#2563eb','노량진 SSP2-4.5')
        b2,l2=make_band(future_years_np,do_sy_245,'#7dd3fc','선유 SSP2-4.5')
        b3,l3=make_band(future_years_np,do_ny_585,'#dc2626','노량진 SSP5-8.5')
        b4,l4=make_band(future_years_np,do_sy_585,'#fca5a5','선유 SSP5-8.5')
        fig_full.add_traces([b1,b2,b3,b4,l1,l2])
        l3.update(line_dash='dot'); l4.update(line_dash='dot')
        fig_full.add_traces([l3,l4])
        fig_full.add_hline(y=7.5,line_dash='dot',line_color='#16a34a',
                           annotation_text='1등급 7.5',annotation_font_color='#16a34a',annotation_font_size=10)
        fig_full.add_hline(y=5.0,line_dash='dot',line_color='#dc2626',
                           annotation_text='위험 5.0',annotation_font_color='#dc2626',annotation_font_size=10)
        fig_full.add_vline(x=2026,line_dash='dot',line_color='#94a3b8',
                           annotation_text='현재(2026)',annotation_font_size=10)
        fig_full.update_layout(height=360,plot_bgcolor='white',paper_bgcolor='white',
                               margin=dict(l=10,r=10,t=16,b=10),
                               xaxis=dict(title='연도',showgrid=True,gridcolor='#f8fafc',
                                          tickvals=[2020,2026,2030,2040,2050]),
                               yaxis=dict(title='DO (mg/L)',range=[3.0,13.0],showgrid=True,gridcolor='#f8fafc'),
                               legend=dict(orientation='h',y=1.06,xanchor='right',x=1,font=dict(size=11)))
        st.plotly_chart(fig_full,use_container_width=True,config={'displaylogo':False})

    with st.expander("📋 연도별 예측 수치표", expanded=False):
        all_miles=[2026,2030,2035,2040,2045,2050]
        all_idxs=[y-2020 for y in all_miles]
        pred_tbl=pd.DataFrame({
            '연도':all_miles,
            'DO 노량진 SSP2-4.5':[f"{do_ny_245[i]:.2f}" for i in all_idxs],
            'DO 선유 SSP2-4.5':  [f"{do_sy_245[i]:.2f}" for i in all_idxs],
            'DO 노량진 SSP5-8.5':[f"{do_ny_585[i]:.2f}" for i in all_idxs],
            'DO 선유 SSP5-8.5':  [f"{do_sy_585[i]:.2f}" for i in all_idxs],
            '상태':['🚨 위험' if min(do_ny_585[i],do_sy_585[i])<5.0
                   else ('⚠️ 주의' if min(do_ny_245[i],do_ny_585[i])<6.5 else '✅ 양호')
                   for i in all_idxs],
        })
        st.dataframe(pred_tbl,use_container_width=True,hide_index=True)

    st.markdown("""
    <div class="warn-box" style="margin-top:8px">
    ⚠️ <b>예측 모델 안내</b>: 2020년 실측 데이터 기반 통계 외삽 모델.
    Henry's Law + 도시 비점오염 보정 적용. 실제 수질은 정책·인프라·강수량에 따라 달라질 수 있습니다.
    </div>
    """, unsafe_allow_html=True)



# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 : 수질 정책 (카드형 + 지도 — 첨부 파일 버전)
# ═══════════════════════════════════════════════════════════════════════════════
with tab6:

    PHASE_STYLES = {
        "단기": {"pill":"short","accent":"linear-gradient(90deg,#2563eb,#3b82f6)",
                 "icon_bg":"#eff6ff","effect_color":"#1d4ed8",
                 "do_chip_bg":"#dbeafe","do_chip_color":"#1d4ed8"},
        "중기": {"pill":"mid","accent":"linear-gradient(90deg,#059669,#10b981)",
                 "icon_bg":"#f0fdf4","effect_color":"#059669",
                 "do_chip_bg":"#dcfce7","do_chip_color":"#15803d"},
        "장기": {"pill":"long","accent":"linear-gradient(90deg,#7c3aed,#a855f7)",
                 "icon_bg":"#faf5ff","effect_color":"#7c3aed",
                 "do_chip_bg":"#f3e8ff","do_chip_color":"#7e22ce"},
    }

    # ── ① 인트로 배너 ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="policy-intro">
        <div class="policy-intro-label">Action Plan · 2026 – 2050</div>
        <div class="policy-intro-title">한강을 지키는<br>6가지 핵심 정책</div>
        <div class="policy-intro-body">
            2020년 실측 데이터는 여름철 DO가 수생태계 위험 기준(5 mg/L)에 근접하거나 하회하는 구간이
            반복됨을 보여줍니다. 기후변화 SSP5-8.5 경로가 지속되면 2050년 한강 생태계의 구조적 붕괴가
            우려됩니다. 단기 즉각 대응부터 장기 구조 전환까지, 3단계 로드맵이 필요합니다.
        </div>
        <div class="policy-intro-stats">
            <div><div class="policy-intro-stat-val">2.1</div>
                 <div class="policy-intro-stat-label">mg/L · 2020 여름 DO 최솟값</div></div>
            <div><div class="policy-intro-stat-val">5.54</div>
                 <div class="policy-intro-stat-label">mg/L · SSP5-8.5 2050 예측</div></div>
            <div><div class="policy-intro-stat-val">6개</div>
                 <div class="policy-intro-stat-label">단계별 핵심 정책</div></div>
            <div><div class="policy-intro-stat-val">25년</div>
                 <div class="policy-intro-stat-label">정책 로드맵 기간</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── ② 정책 카드 — 페이즈별 ──────────────────────────────────────────────
    phases = [
        {"key":"단기","label":"단기 집중 대응","period":"2026 – 2030","pill":"short","emoji":"⚡","target":"DO 최솟값 3.0 mg/L 이상 유지"},
        {"key":"중기","label":"구조적 수질 개선","period":"2031 – 2040","pill":"mid","emoji":"🔧","target":"DO 연평균 8.0 mg/L 이상 유지"},
        {"key":"장기","label":"기후 구조 전환","period":"2041 – 2050","pill":"long","emoji":"🌍","target":"1등급 수질 연중 60% 이상"},
    ]
    for phase in phases:
        phase_policies = [p for p in MAP_POLICIES if p["phase"] == phase["key"]]
        st_obj = PHASE_STYLES[phase["key"]]
        n = len(phase_policies)
        grid_class = "pcard-grid" if n == 3 else "pcard-grid two"
        st.markdown(f"""
        <div class="phase-header">
            <span class="phase-pill {st_obj['pill']}">{phase['emoji']} {phase['label']}</span>
            <span style="font-size:12px;color:#94a3b8;font-weight:600">{phase['period']}</span>
            <div class="phase-line"></div>
            <span style="font-size:11.5px;color:#64748b;background:#f1f5f9;
            padding:4px 12px;border-radius:99px;white-space:nowrap">🎯 {phase['target']}</span>
        </div>
        """, unsafe_allow_html=True)
        cards_html = f'<div class="{grid_class}">'
        for p in phase_policies:
            global_num = MAP_POLICIES.index(p) + 1
            nry_str = f"+{p['do_impact_nry']:.1f}"
            syu_str = f"+{p['do_impact_syu']:.1f}"
            cards_html += f"""
            <div class="pcard">
                <div class="pcard-accent" style="background:{st_obj['accent']}"></div>
                <div class="pcard-inner">
                    <div class="pcard-icon-row">
                        <div class="pcard-icon" style="background:{st_obj['icon_bg']}">{p['icon']}</div>
                        <span class="pcard-num">POLICY {global_num:02d}</span>
                    </div>
                    <div class="pcard-title">{p['title']}</div>
                    <div class="pcard-detail">{p['detail']}</div>
                    <div class="pcard-divider"></div>
                    <div class="pcard-effect-label">기대 효과</div>
                    <div class="pcard-effect" style="color:{st_obj['effect_color']}">{p['effect']}</div>
                    <div class="pcard-do-row">
                        <span class="pcard-do-chip" style="background:{st_obj['do_chip_bg']};color:{st_obj['do_chip_color']}">노량진 {nry_str} mg/L</span>
                        <span class="pcard-do-chip" style="background:{st_obj['do_chip_bg']};color:{st_obj['do_chip_color']}">선유 {syu_str} mg/L</span>
                    </div>
                </div>
            </div>"""
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)

    # ── ③ 로드맵 타임라인 ───────────────────────────────────────────────────
    st.markdown("""
    <div class="roadmap-wrap">
        <div class="roadmap-title">📍 정책 우선순위 로드맵</div>
        <div class="roadmap-timeline">
            <div class="roadmap-phase">
                <div class="roadmap-dot short">⚡</div>
                <div class="roadmap-phase-label" style="color:#2563eb">단기</div>
                <div class="roadmap-phase-period">2026 – 2030</div>
                <div class="roadmap-items">
                    <div class="roadmap-item">🌬️ 폭기 시설 확충</div>
                    <div class="roadmap-item">📡 모니터링 고도화</div>
                    <div class="roadmap-item">🌧️ 초기 우수 저류조</div>
                </div>
                <div class="roadmap-target short">DO 최솟값 3.0+</div>
            </div>
            <div class="roadmap-phase">
                <div class="roadmap-dot mid">🔧</div>
                <div class="roadmap-phase-label" style="color:#0891b2">중기</div>
                <div class="roadmap-phase-period">2031 – 2040</div>
                <div class="roadmap-items">
                    <div class="roadmap-item">🏭 하수처리장 고도화</div>
                    <div class="roadmap-item">🌿 생태습지 확대</div>
                    <div class="roadmap-item">🚫 비점오염 관리</div>
                </div>
                <div class="roadmap-target mid">DO 연평균 8.0+</div>
            </div>
            <div class="roadmap-phase">
                <div class="roadmap-dot long">🌍</div>
                <div class="roadmap-phase-label" style="color:#22c55e">장기</div>
                <div class="roadmap-phase-period">2041 – 2050</div>
                <div class="roadmap-items">
                    <div class="roadmap-item">🌳 탄소 감축 달성</div>
                    <div class="roadmap-item">🏙️ 도시 열섬 완화</div>
                    <div class="roadmap-item">🏞️ 자연형 하천 복원</div>
                </div>
                <div class="roadmap-target long">1등급 연중 60%+</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── ④ 정책 전/후 비교 지도 ──────────────────────────────────────────────
    st.markdown("""
    <div class="map-section-hd">
        <div class="map-section-hd-icon">🗺️</div>
        <div>
            <div class="map-section-hd-title">정책 실행 전 vs 후 — DO 수질 지도 비교</div>
            <div class="map-section-hd-sub">정책을 선택하고 연도를 설정하면 DO 등급 변화를 지도로 확인할 수 있습니다</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    pc1, pc2, pc3 = st.columns([2, 2, 1])
    with pc1:
        selected_policies = st.multiselect(
            "적용할 정책 선택 (복수 선택 가능)",
            options=[p["title"] for p in MAP_POLICIES],
            default=["폭기(曝氣) 시설 확충", "하수처리장 고도화"],
        )
    with pc2:
        map_scenario = st.selectbox(
            "기후 시나리오",
            ["SSP5-8.5 (고위 — 현재 추세)", "SSP2-4.5 (중위 — 감축 지속)"],
            key="map_scen"
        )
        map_scen_key = "SSP585" if "SSP5-8.5" in map_scenario else "SSP245"
    with pc3:
        map_year = st.select_slider("예측 연도", options=[2026,2030,2040,2050], value=2040, key="map_year")

    base_row    = df_future[df_future["year"] == map_year].iloc[0]
    base_do_nry = base_row[f"{map_scen_key}_노량진_DO"]
    base_do_syu = base_row[f"{map_scen_key}_선유_DO"]
    base_ph_nry = base_row[f"{map_scen_key}_노량진_pH"]
    base_ph_syu = base_row[f"{map_scen_key}_선유_pH"]
    total_imp_nry = sum(p["do_impact_nry"] for p in MAP_POLICIES if p["title"] in selected_policies)
    total_imp_syu = sum(p["do_impact_syu"] for p in MAP_POLICIES if p["title"] in selected_policies)
    after_do_nry  = min(base_do_nry + total_imp_nry, 12.0)
    after_do_syu  = min(base_do_syu + total_imp_syu, 12.0)
    imp_nry = after_do_nry - base_do_nry
    imp_syu = after_do_syu - base_do_syu
    scen_label2 = "SSP5-8.5" if map_scen_key == "SSP585" else "SSP2-4.5"
    active_markers = []
    for title in selected_policies:
        active_markers.extend(POLICY_MARKERS.get(title, []))

    st.markdown(f"""
    <div style='display:flex;gap:14px;margin:12px 0 16px;flex-wrap:wrap'>
        <div style='flex:1;min-width:220px;background:#fefce8;border:1px solid #fde047;
        padding:12px 16px;border-radius:12px'>
            <div style='font-size:11px;font-weight:700;color:#a16207;letter-spacing:.06em;margin-bottom:6px'>❌ 정책 미실행 · {scen_label2} {map_year}년</div>
            <div style='font-size:15px;font-weight:800;color:{do_color(base_do_nry)}'>노량진 {base_do_nry:.2f} mg/L</div>
            <div style='font-size:15px;font-weight:800;color:{do_color(base_do_syu)}'>선유&nbsp;&nbsp;&nbsp;&nbsp; {base_do_syu:.2f} mg/L</div>
        </div>
        <div style='flex:1;min-width:220px;background:#f0fdf4;border:1px solid #86efac;
        padding:12px 16px;border-radius:12px'>
            <div style='font-size:11px;font-weight:700;color:#166534;letter-spacing:.06em;margin-bottom:6px'>✅ 정책 실행 후 · {len(selected_policies)}개 정책 적용</div>
            <div style='font-size:15px;font-weight:800;color:{do_color(after_do_nry)}'>노량진 {after_do_nry:.2f} mg/L <span style='font-size:12px;color:#15803d'>(+{imp_nry:.2f})</span></div>
            <div style='font-size:15px;font-weight:800;color:{do_color(after_do_syu)}'>선유&nbsp;&nbsp;&nbsp;&nbsp; {after_do_syu:.2f} mg/L <span style='font-size:12px;color:#15803d'>(+{imp_syu:.2f})</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    center = [37.522, 126.906]
    map_col1, map_col2 = st.columns(2)
    with map_col1:
        st.markdown("**❌ 정책 미실행**")
        m_before = build_map(center, base_do_nry, base_do_syu, base_ph_nry, base_ph_syu,
                             map_year, f"미실행 ({scen_label2})")
        st_folium(m_before, width=None, height=400, key="map_before")
    with map_col2:
        st.markdown("**✅ 정책 실행 후**")
        m_after = build_map(center, after_do_nry, after_do_syu, base_ph_nry, base_ph_syu,
                            map_year, f"실행 후 ({scen_label2})", policy_markers=active_markers)
        st_folium(m_after, width=None, height=400, key="map_after")

    st.divider()
    sg1, sg2 = st.columns(2)
    with sg1:
        st.metric("노량진 DO", f"{after_do_nry:.2f} mg/L", delta=f"+{imp_nry:.2f} mg/L",
                  help=f"미실행: {base_do_nry:.2f} → 실행 후: {after_do_nry:.2f}")
        st.caption(f"등급 변화: {do_grade_label(base_do_nry)} → {do_grade_label(after_do_nry)}")
    with sg2:
        st.metric("선유 DO", f"{after_do_syu:.2f} mg/L", delta=f"+{imp_syu:.2f} mg/L",
                  help=f"미실행: {base_do_syu:.2f} → 실행 후: {after_do_syu:.2f}")
        st.caption(f"등급 변화: {do_grade_label(base_do_syu)} → {do_grade_label(after_do_syu)}")

    if map_scen_key == "SSP585" and map_year >= 2040:
        st.error(f"🚨 SSP5-8.5 {map_year}년: DO 위험 임계치(5.0 mg/L) 근접! 정책 실행이 시급합니다.")
    elif map_scen_key == "SSP585" and map_year >= 2030:
        st.warning("⚠️ SSP5-8.5 시나리오 — 2030년 이후 DO 감소 추세 본격화. 단기 정책 선행 필요.")
    else:
        st.success(f"✅ {map_year}년 {scen_label2} — 정책 실행 시 수질 관리 가능 범위 유지")


# 푸터
st.markdown("""
<div style="text-align:center;font-size:12px;color:#9ca3af;margin-top:40px;padding:16px 0;border-top:1px solid #f3f4f6;">
    데이터 출처: 서울 열린데이터 광장 · 서울시 요일별 한강 수질 현황 (2020) &nbsp;|&nbsp;
    노량진 · 선유 측정소 시간별 실측값 일평균 &nbsp;|&nbsp;
    예측: IPCC AR6 SSP2-4.5 / SSP5-8.5 시나리오 적용
</div>
""", unsafe_allow_html=True)
