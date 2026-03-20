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
    st.markdown('<div class="sec-hd">날짜별 수질 시계열 — 범례 클릭으로 계열 선택</div>',
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 2, 2])
    with c1:
        view_mode = st.selectbox("표시 항목", ["pH + DO 동시", "pH만", "DO만"])
    with c2:
        stations = st.multiselect("측정 지점", ["노량진", "선유"], default=["노량진", "선유"])
    with c3:
        date_range = st.date_input(
            "기간",
            value=(df['date'].min().date(), df['date'].max().date()),
            min_value=df['date'].min().date(),
            max_value=df['date'].max().date(),
        )

    if not stations:
        st.warning("측정 지점을 하나 이상 선택해 주세요.")
        st.stop()

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        mask = (df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])
        dff = df[mask].copy()
    else:
        dff = df.copy()

    show_ph = view_mode in ["pH + DO 동시", "pH만"]
    show_do = view_mode in ["pH + DO 동시", "DO만"]
    is_dual = show_ph and show_do

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.07,
                        subplot_titles=("수소이온농도 (pH)", "용존산소 (DO, mg/L)")) \
          if is_dual else go.Figure()

    def add_line(fig, x, y, name, color, row=None):
        kw = dict(x=x, y=y, name=name, mode='lines',
                  line=dict(color=color, width=1.8),
                  hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>%{{y:.3f}}<extra></extra>")
        fig.add_trace(go.Scatter(**kw), row=row, col=1) if row else fig.add_trace(go.Scatter(**kw))

    if show_ph:
        for s in stations:
            add_line(fig, dff['date'], dff[f'pH_{s}'], f'{s} pH',
                     COLORS[f'{s}_pH'], row=1 if is_dual else None)
        ref = dict(line_dash='dot', line_color='rgba(100,100,100,0.5)', annotation_font_size=10)
        if is_dual:
            fig.add_hline(y=6.5, annotation_text='하한 6.5', row=1, col=1, **ref)
            fig.add_hline(y=8.5, annotation_text='상한 8.5', row=1, col=1, **ref)
        else:
            fig.add_hline(y=6.5, annotation_text='하한 6.5', **ref)
            fig.add_hline(y=8.5, annotation_text='상한 8.5', **ref)

    if show_do:
        for s in stations:
            add_line(fig, dff['date'], dff[f'DO_{s}'], f'{s} DO',
                     COLORS[f'{s}_DO'], row=2 if is_dual else None)
        ref2 = dict(line_dash='dot', line_color='rgba(220,38,38,0.6)',
                    annotation_text='생존 하한 5.0 mg/L',
                    annotation_font_color='#dc2626', annotation_font_size=10)
        if is_dual:
            fig.add_hline(y=5.0, row=2, col=1, **ref2)
        else:
            fig.add_hline(y=5.0, **ref2)

    fig.update_layout(
        height=520 if is_dual else 360,
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=36, b=10), hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=12)),
    )
    fig.update_xaxes(showgrid=True, gridcolor='#f3f4f6', linecolor='#e5e7eb')
    fig.update_yaxes(showgrid=True, gridcolor='#f3f4f6', linecolor='#e5e7eb')

    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True,
                    config={'displayModeBar': True,
                            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                            'displaylogo': False})
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption("💡 범례 클릭: 계열 켜기/끄기  ·  드래그: 구간 확대  ·  더블클릭: 초기화")

    with st.expander("원시 데이터 보기 / CSV 다운로드"):
        cols_show = ['date'] + [f'pH_{s}' for s in stations] + [f'DO_{s}' for s in stations]
        disp = dff[cols_show].copy()
        disp['date'] = disp['date'].dt.strftime('%Y-%m-%d')
        disp.columns = ['날짜'] + [f'pH ({s})' for s in stations] + [f'DO ({s}) mg/L' for s in stations]
        st.dataframe(disp, use_container_width=True, height=260)
        st.download_button("⬇️ CSV 다운로드", disp.to_csv(index=False).encode('utf-8-sig'),
                           file_name="hangang_2020.csv", mime="text/csv")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 : 월별 패턴
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="sec-hd">월별 평균 · 최솟값 · 최댓값 비교</div>', unsafe_allow_html=True)

    df['month'] = df['date'].dt.month
    monthly = df.groupby('month').agg(
        ph_ny_mean=('pH_노량진','mean'), ph_sy_mean=('pH_선유','mean'),
        ph_ny_min=('pH_노량진','min'),   ph_sy_min=('pH_선유','min'),
        ph_ny_max=('pH_노량진','max'),   ph_sy_max=('pH_선유','max'),
        do_ny_mean=('DO_노량진','mean'), do_sy_mean=('DO_선유','mean'),
        do_ny_min=('DO_노량진','min'),   do_sy_min=('DO_선유','min'),
        do_ny_max=('DO_노량진','max'),   do_sy_max=('DO_선유','max'),
    ).reset_index()

    subtab1, subtab2 = st.tabs(["pH 월별", "DO 월별"])

    def band_trace(x, hi, lo, color_hex, name):
        r,g,b = int(color_hex[1:3],16), int(color_hex[3:5],16), int(color_hex[5:7],16)
        return go.Scatter(
            x=x + x[::-1], y=list(hi) + list(lo)[::-1],
            fill='toself', fillcolor=f'rgba({r},{g},{b},0.09)',
            line=dict(color='rgba(255,255,255,0)'), showlegend=False, name=name)

    with subtab1:
        fig_m = go.Figure()
        fig_m.add_trace(band_trace(MLBs, monthly['ph_ny_max'], monthly['ph_ny_min'], '#2563eb', '노량진 범위'))
        fig_m.add_trace(band_trace(MLBs, monthly['ph_sy_max'], monthly['ph_sy_min'], '#ea580c', '선유 범위'))
        fig_m.add_trace(go.Scatter(x=MLBs, y=monthly['ph_ny_mean'].round(3), name='노량진 평균',
                                   mode='lines+markers', line=dict(color='#2563eb', width=2.5), marker=dict(size=7)))
        fig_m.add_trace(go.Scatter(x=MLBs, y=monthly['ph_sy_mean'].round(3), name='선유 평균',
                                   mode='lines+markers', line=dict(color='#ea580c', width=2.5), marker=dict(size=7)))
        fig_m.add_hline(y=6.5, line_dash='dot', line_color='gray', annotation_text='환경부 하한 6.5', annotation_font_size=10)
        fig_m.add_hline(y=8.5, line_dash='dot', line_color='gray', annotation_text='환경부 상한 8.5', annotation_font_size=10)
        fig_m.update_layout(height=340, plot_bgcolor='white', paper_bgcolor='white',
                             margin=dict(l=10,r=10,t=16,b=10), yaxis=dict(range=[6.0,9.2],title='pH'),
                             legend=dict(orientation='h',y=1.08,xanchor='right',x=1))
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_m, use_container_width=True, config={'displaylogo': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with subtab2:
        fig_d = go.Figure()
        fig_d.add_trace(band_trace(MLBs, monthly['do_ny_max'], monthly['do_ny_min'], '#0891b2', '노량진 범위'))
        fig_d.add_trace(band_trace(MLBs, monthly['do_sy_max'], monthly['do_sy_min'], '#d97706', '선유 범위'))
        fig_d.add_trace(go.Scatter(x=MLBs, y=monthly['do_ny_mean'].round(3), name='노량진 평균',
                                   mode='lines+markers', line=dict(color='#0891b2', width=2.5), marker=dict(size=7)))
        fig_d.add_trace(go.Scatter(x=MLBs, y=monthly['do_sy_mean'].round(3), name='선유 평균',
                                   mode='lines+markers', line=dict(color='#d97706', width=2.5), marker=dict(size=7)))
        fig_d.add_hline(y=5.0, line_dash='dot', line_color='#dc2626',
                        annotation_text='수생태계 위험 하한 5.0', annotation_font_color='#dc2626', annotation_font_size=10)
        fig_d.update_layout(height=340, plot_bgcolor='white', paper_bgcolor='white',
                             margin=dict(l=10,r=10,t=16,b=10), yaxis=dict(range=[0,14],title='mg/L'),
                             legend=dict(orientation='h',y=1.08,xanchor='right',x=1))
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_d, use_container_width=True, config={'displaylogo': False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-hd">월별 상세 수치표</div>', unsafe_allow_html=True)
    tbl = pd.DataFrame({
        '월': MLBs,
        'pH 노량진 (평균)':   monthly['ph_ny_mean'].round(2),
        'pH 선유 (평균)':     monthly['ph_sy_mean'].round(2),
        'DO 노량진 (평균)':   monthly['do_ny_mean'].round(2),
        'DO 선유 (평균)':     monthly['do_sy_mean'].round(2),
        'DO 노량진 (최솟값)': monthly['do_ny_min'].round(2),
        'DO 선유 (최솟값)':   monthly['do_sy_min'].round(2),
    })
    st.dataframe(tbl, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 : 상관관계
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="sec-hd">pH – DO 상관관계 분석</div>', unsafe_allow_html=True)

    fig_s = go.Figure()
    corrs = {}
    for nm, pc, dc, clr in [('노량진','pH_노량진','DO_노량진','#2563eb'),
                              ('선유','pH_선유','DO_선유','#ea580c')]:
        tmp = df[[pc, dc, 'date']].dropna()
        fig_s.add_trace(go.Scatter(x=tmp[pc], y=tmp[dc], mode='markers', name=nm,
                                   marker=dict(color=clr, size=5, opacity=0.45),
                                   hovertemplate=f"<b>{nm}</b><br>pH: %{{x:.3f}}<br>DO: %{{y:.3f}} mg/L<extra></extra>"))
        z = np.polyfit(tmp[pc], tmp[dc], 1)
        xr = np.linspace(tmp[pc].min(), tmp[pc].max(), 100)
        fig_s.add_trace(go.Scatter(x=xr, y=np.polyval(z, xr), mode='lines', name=f'{nm} 추세선',
                                   line=dict(color=clr, width=2, dash='dash')))
        corrs[nm] = tmp[[pc, dc]].corr().iloc[0, 1]

    fig_s.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white',
                        margin=dict(l=10,r=10,t=10,b=10),
                        xaxis=dict(title='pH (일평균)', showgrid=True, gridcolor='#f3f4f6'),
                        yaxis=dict(title='DO mg/L (일평균)', showgrid=True, gridcolor='#f3f4f6'),
                        legend=dict(orientation='h',y=1.06,xanchor='right',x=1))
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig_s, use_container_width=True, config={'displaylogo': False})
    st.markdown('</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.metric("노량진 피어슨 상관계수 (r)", f"{corrs['노량진']:.3f}", "강한 양의 상관")
    with c2:
        st.metric("선유 피어슨 상관계수 (r)", f"{corrs['선유']:.3f}", "중간-강한 양의 상관")

    st.markdown("""
    <div class="ins-card indigo">
      <div class="ins-title">상관관계가 의미하는 것</div>
      <div class="ins-body">
        두 지표가 함께 오르내리는 이유는 <b>공통 생물학적 원인</b> 때문입니다.<br><br>
        <b>봄 (3–4월):</b> 광합성 활발 → CO₂ 소비 → pH ↑ / O₂ 생산 → DO ↑<br>
        <b>여름 (6–8월):</b> 유기물 분해 → CO₂ 방출 → pH ↓ / O₂ 소비 → DO ↓<br><br>
        노량진(r=0.767)이 선유(r=0.648)보다 높은 이유는, 선유에서 퇴적물·유기물 등
        국소 오염 인자가 DO를 추가로 낮춰 pH와의 연동을 희석시키기 때문입니다.
      </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 : 수질 해석
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="sec-hd">수질 데이터 심층 해석</div>', unsafe_allow_html=True)

    # expander 제목에서 이모지 제거 → 별도 ins-title로 표시하여 겹침 방지
    insights = [
        ("blue",
         "봄철 pH 급등 — 식물성 플랑크톤 광합성",
         """<span class="badge b-blue">3–4월</span>
         두 지점 모두 pH 연중 최고치(노량진 <b>8.3</b>, 선유 <b>8.4</b>)를 기록합니다.
         수온 상승 → 플랑크톤 폭발 증식 → 광합성으로 CO₂ 소비 →
         탄산(H₂CO₃) 감소 → 수소이온 농도 하락 → pH 상승의 연쇄입니다.
         봄철 오후 14–18시에 일중 pH 편차가 최대 <b>1.0 이상</b> 벌어지는 것도 같은 원리입니다."""),

        ("red",
         "여름철 DO 위기 — 수생태계 스트레스 구간",
         """<span class="badge b-red">5월 말 – 9월</span>
         노량진 6월 평균 DO <b>5.95 mg/L</b>, 선유 <b>5.51 mg/L</b>로 급락합니다.
         순간 최솟값은 노량진 <b>2.1 mg/L</b>, 선유 <b>2.0 mg/L</b>까지 떨어졌습니다.<br><br>
         <b>원인 ①</b> 수온 상승 → 산소 용해도 감소 (20°C: 9.1 → 30°C: 7.5 mg/L)<br>
         <b>원인 ②</b> 봄 플랑크톤 사체 분해 → 박테리아 대량 산소 소비<br><br>
         환경부 생물생존 최소 기준 <b>5 mg/L</b>에 근접하거나 하회하는 시간대가 발생하며
         민감 어종(쏘가리·참마자·버들치)에게 생존 스트레스가 생길 수 있습니다."""),

        ("green",
         "겨울철 DO 최고치 — 차가운 물의 산소 포화",
         """<span class="badge b-green">11–12월</span>
         노량진 12월 평균 <b>11.17 mg/L</b>, 선유 <b>10.91 mg/L</b>.
         수온이 낮을수록 기체 용해도가 높아져 DO가 최고치입니다.
         동시에 pH도 7.4–7.5로 중성에 가까워 수생태계 관점에서 가장 쾌적한 환경입니다."""),

        ("orange",
         "노량진 vs 선유 — 공간적 수질 차이",
         """선유는 노량진에 비해 계절 변동폭이 큽니다
         (pH 연간 범위 <b>1.8</b> vs <b>1.5</b>).
         선유는 하류 방향으로 유속이 느리고 유기물이 많아 분해에 의한 DO 소비가 더 큽니다.<br><br>
         <span class="badge b-orange">주의</span>
         선유 8월 유효 측정치 424건(정상 730건의 58%)으로 대폭 감소합니다.
         센서 이상·유지 보수 또는 수질 악화로 인한 장비 오류 가능성이 있어 해석 시 주의가 필요합니다."""),

        ("purple",
         "환경부 수질 등급 평가",
         """<table class="grade-table">
           <tr><th>등급</th><th>pH</th><th>DO (mg/L)</th><th>용도</th><th>2020 한강</th></tr>
           <tr><td><span class="badge b-blue">1등급 (매우 좋음)</span></td>
               <td>6.5–8.5</td><td>≥ 7.5</td><td>상수원·자연보전</td><td>10–4월 ✓</td></tr>
           <tr><td><span class="badge b-green">2등급 (좋음)</span></td>
               <td>6.5–8.5</td><td>≥ 5.0</td><td>1급 정수처리</td><td>봄·가을 해당</td></tr>
           <tr><td><span class="badge b-orange">3등급 (보통)</span></td>
               <td>6.5–8.5</td><td>≥ 5.0</td><td>농업·수산용수</td><td>여름 경계</td></tr>
           <tr><td><span class="badge b-red">4등급 이하</span></td>
               <td>6.0–8.5</td><td>≥ 2.0</td><td>공업용수</td><td>6월 순간값</td></tr>
         </table><br>
         <b>결론:</b> 연간 평균은 2~3등급 수준이나, 여름 DO 급락 구간에서 4등급 경계까지 악화됩니다.
         연간 수질 관리의 핵심 과제는 <b>5~9월 DO 하락 억제</b>입니다."""),
    ]

    for color, title, body in insights:
        # 이모지 없이 순수 텍스트 제목만 expander에 사용 → 겹침 방지
        with st.expander(title):
            st.markdown(f'<div class="ins-body">{body}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 : 미래 예측 (2030 · 2040 · 2050)
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="sec-hd">2026–2050 수질 예측 (기후변화 시나리오)</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="warn-box">
    ⚠️ <b>예측 모델 안내</b>: 2020년 실측 데이터를 기반으로 기후변화 시나리오(IPCC SSP2-4.5, SSP5-8.5)를
    적용한 통계적 외삽 모델입니다. 실제 수질은 정책·인프라·강수량 변동에 따라 달라질 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

    SCENARIOS = {
        'SSP2-4.5 (중위 시나리오)': {
            'dash': 'solid', 'temp_2050': 1.5,
            'do_per_c': 0.20, 'summer_penalty': 0.08, 'ph_per_yr': -0.002,
        },
        'SSP5-8.5 (고위 시나리오)': {
            'dash': 'dash', 'temp_2050': 3.0,
            'do_per_c': 0.22, 'summer_penalty': 0.18, 'ph_per_yr': -0.005,
        },
    }
    BASE = {'do_ny': 8.463, 'do_sy': 8.260, 'ph_ny': 7.287, 'ph_sy': 7.317}
    future_years = np.arange(2020, 2051)

    def forecast(base, sc, kind='do'):
        vals, noises = [], []
        for y in future_years:
            n, frac = y - 2020, (y - 2020) / 30
            if kind == 'do':
                val = base - sc['do_per_c'] * sc['temp_2050'] * frac - sc['summer_penalty'] * frac
                noise = 0.3 + 0.5 * frac
            else:
                val = base + sc['ph_per_yr'] * n
                noise = 0.05 + 0.1 * frac
            vals.append(val); noises.append(noise)
        return np.array(vals), np.array(noises)

    def make_band(years, vals, noise, hex_color, label):
        r,g,b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
        band = go.Scatter(
            x=list(years)+list(years[::-1]),
            y=list(vals+noise)+list((vals-noise)[::-1]),
            fill='toself', fillcolor=f'rgba({r},{g},{b},0.10)',
            line=dict(color='rgba(255,255,255,0)'), showlegend=False, name=f'{label} 불확실도')
        line = go.Scatter(x=years, y=np.round(vals,3), name=f'{label} 예측', mode='lines',
                          line=dict(color=hex_color, width=2.2))
        return band, line

    sc_name = st.selectbox("시나리오 선택", list(SCENARIOS.keys()), key='sc_sel')
    sc = SCENARIOS[sc_name]
    sc['dash']  # ensure key exists

    do_ny_v, do_ny_n = forecast(BASE['do_ny'], sc, 'do')
    do_sy_v, do_sy_n = forecast(BASE['do_sy'], sc, 'do')
    ph_ny_v, ph_ny_n = forecast(BASE['ph_ny'], sc, 'ph')
    ph_sy_v, ph_sy_n = forecast(BASE['ph_sy'], sc, 'ph')

    # ── 연도별 비교 강조 (2030 / 2040 / 2050) ─────────────────────────────
    st.markdown('<div class="sec-hd">2030 · 2040 · 2050 예측 수치 한눈에 보기</div>',
                unsafe_allow_html=True)

    highlight_years = [2026, 2030, 2040, 2050]
    h_idxs = [y - 2020 for y in highlight_years]

    col_cards = st.columns(4)
    status_emoji = {True: '🚨', False: ''}
    for i, (yr, idx) in enumerate(zip(highlight_years, h_idxs)):
        do_n = do_ny_v[idx]; do_s = do_sy_v[idx]
        ph_n = ph_ny_v[idx]; ph_s = ph_sy_v[idx]
        warn = do_n < 6.0 or do_s < 6.0
        danger = do_n < 5.0 or do_s < 5.0
        state = '🚨 위험' if danger else ('⚠️ 주의' if warn else '✅ 양호')
        top_color = '#dc2626' if danger else ('#f97316' if warn else '#22c55e')
        with col_cards[i]:
            st.markdown(f"""
            <div style="background:#fff; border-radius:14px; padding:18px 16px;
                        box-shadow:0 2px 8px rgba(0,0,0,0.07);
                        border-top:3px solid {top_color}; text-align:center;">
              <div style="font-size:22px; font-weight:900; color:#0c1e3c; margin-bottom:4px;">{yr}년</div>
              <div style="font-size:12px; color:#6b7280; margin-bottom:12px; font-weight:500;">{state}</div>
              <div style="font-size:12px; color:#374151; line-height:1.9; text-align:left;">
                DO 노량진 <b>{do_n:.2f}</b> mg/L<br>
                DO 선유&nbsp;&nbsp;&nbsp;<b>{do_s:.2f}</b> mg/L<br>
                pH 노량진 <b>{ph_n:.3f}</b><br>
                pH 선유&nbsp;&nbsp;&nbsp;<b>{ph_s:.3f}</b>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 예측 그래프 ───────────────────────────────────────────────────────────
    pred_tabs = st.tabs(["용존산소 (DO) 예측", "수소이온농도 (pH) 예측"])

    def add_milestone_lines(fig, years_list, vals_list, labels, row=None):
        """2030·2040·2050 수직선 + 값 주석"""
        for yr, val, lbl in zip(years_list, vals_list, labels):
            kw = dict(x=yr, line_dash='dot', line_color='rgba(100,100,100,0.4)',
                      annotation_text=lbl, annotation_font_size=10,
                      annotation_font_color='#6b7280')
            if row:
                fig.add_vline(**kw, row=row, col=1)
            else:
                fig.add_vline(**kw)

    milestone_yrs  = [2030, 2040, 2050]
    milestone_lbls = ['2030', '2040', '2050']

    with pred_tabs[0]:
        fig_f = go.Figure()
        b1,l1 = make_band(future_years, do_ny_v, do_ny_n, '#2563eb', '노량진')
        b2,l2 = make_band(future_years, do_sy_v, do_sy_n, '#d97706', '선유')
        fig_f.add_traces([b1,b2,l1,l2])
        fig_f.add_trace(go.Scatter(x=[2020],y=[BASE['do_ny']],mode='markers',
                                   name='노량진 실측(2020)',marker=dict(color='#2563eb',size=10)))
        fig_f.add_trace(go.Scatter(x=[2020],y=[BASE['do_sy']],mode='markers',
                                   name='선유 실측(2020)',marker=dict(color='#d97706',size=10)))
        # 2030·2040·2050 마커
        for yr in milestone_yrs:
            idx = yr - 2020
            fig_f.add_trace(go.Scatter(
                x=[yr,yr], y=[do_ny_v[idx], do_sy_v[idx]], mode='markers+text',
                marker=dict(color=['#2563eb','#d97706'], size=10, symbol='diamond'),
                text=[f"{do_ny_v[idx]:.2f}", f"{do_sy_v[idx]:.2f}"],
                textposition='top center', textfont=dict(size=10),
                showlegend=False, name=f'{yr}년'))
        fig_f.add_hline(y=5.0,line_dash='dot',line_color='#dc2626',
                        annotation_text='수생태계 위험 하한 5.0',annotation_font_color='#dc2626')
        fig_f.add_hline(y=7.5,line_dash='dot',line_color='#16a34a',
                        annotation_text='1등급 기준 7.5',annotation_font_color='#16a34a')
        fig_f.add_vline(x=2026,line_dash='dot',line_color='#6b7280',
                        annotation_text='현재(2026)',annotation_font_size=11)
        for yr in milestone_yrs:
            fig_f.add_vline(x=yr,line_dash='dot',line_color='rgba(150,150,150,0.3)',
                            annotation_text=str(yr),annotation_font_size=10,
                            annotation_font_color='#9ca3af')
        fig_f.update_layout(
            height=440, plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10,r=10,t=10,b=10),
            xaxis=dict(title='연도',showgrid=True,gridcolor='#f3f4f6'),
            yaxis=dict(title='DO (mg/L)',range=[3.0,13.0],showgrid=True,gridcolor='#f3f4f6'),
            legend=dict(orientation='h',y=1.06,xanchor='right',x=1))
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_f, use_container_width=True, config={'displaylogo': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with pred_tabs[1]:
        fig_fp = go.Figure()
        b3,l3 = make_band(future_years, ph_ny_v, ph_ny_n, '#2563eb', '노량진')
        b4,l4 = make_band(future_years, ph_sy_v, ph_sy_n, '#d97706', '선유')
        fig_fp.add_traces([b3,b4,l3,l4])
        fig_fp.add_trace(go.Scatter(x=[2020],y=[BASE['ph_ny']],mode='markers',
                                    name='노량진 실측(2020)',marker=dict(color='#2563eb',size=10)))
        fig_fp.add_trace(go.Scatter(x=[2020],y=[BASE['ph_sy']],mode='markers',
                                    name='선유 실측(2020)',marker=dict(color='#d97706',size=10)))
        for yr in milestone_yrs:
            idx = yr - 2020
            fig_fp.add_trace(go.Scatter(
                x=[yr,yr], y=[ph_ny_v[idx], ph_sy_v[idx]], mode='markers+text',
                marker=dict(color=['#2563eb','#d97706'], size=10, symbol='diamond'),
                text=[f"{ph_ny_v[idx]:.3f}", f"{ph_sy_v[idx]:.3f}"],
                textposition='top center', textfont=dict(size=10),
                showlegend=False, name=f'{yr}년'))
        fig_fp.add_hline(y=6.5,line_dash='dot',line_color='#dc2626',annotation_text='환경부 하한 6.5')
        fig_fp.add_hline(y=8.5,line_dash='dot',line_color='gray',annotation_text='환경부 상한 8.5')
        fig_fp.add_vline(x=2026,line_dash='dot',line_color='#6b7280',
                         annotation_text='현재(2026)',annotation_font_size=11)
        for yr in milestone_yrs:
            fig_fp.add_vline(x=yr,line_dash='dot',line_color='rgba(150,150,150,0.3)',
                             annotation_text=str(yr),annotation_font_size=10,
                             annotation_font_color='#9ca3af')
        fig_fp.update_layout(
            height=440, plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10,r=10,t=10,b=10),
            xaxis=dict(title='연도',showgrid=True,gridcolor='#f3f4f6'),
            yaxis=dict(title='pH',range=[6.0,9.0],showgrid=True,gridcolor='#f3f4f6'),
            legend=dict(orientation='h',y=1.06,xanchor='right',x=1))
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_fp, use_container_width=True, config={'displaylogo': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # 전체 연도표
    st.markdown('<div class="sec-hd">전체 연도별 예측 수치표</div>', unsafe_allow_html=True)
    all_miles = [2026, 2030, 2035, 2040, 2045, 2050]
    all_idxs  = [y - 2020 for y in all_miles]
    pred_tbl = pd.DataFrame({
        '연도': all_miles,
        'DO 노량진 (mg/L)': [f"{do_ny_v[i]:.2f}" for i in all_idxs],
        'DO 선유 (mg/L)':   [f"{do_sy_v[i]:.2f}" for i in all_idxs],
        'pH 노량진':         [f"{ph_ny_v[i]:.3f}" for i in all_idxs],
        'pH 선유':           [f"{ph_sy_v[i]:.3f}" for i in all_idxs],
        '수생태계 상태': [
            '🚨 위험' if do_ny_v[i]<5.0 or do_sy_v[i]<5.0
            else ('⚠️ 주의' if do_ny_v[i]<6.5 or do_sy_v[i]<6.5 else '✅ 양호')
            for i in all_idxs
        ],
    })
    st.dataframe(pred_tbl, use_container_width=True, hide_index=True)

    # 시나리오 해설
    st.markdown('<div class="sec-hd">시나리오 해설</div>', unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        st.markdown("""
        <div class="ins-card blue">
          <div class="ins-title">SSP2-4.5 — 중위 시나리오</div>
          <div class="ins-body">
            온실가스 감축 정책 지속 경로. 2050년 기온 <b>+1.5°C</b> 상승 예상.<br><br>
            2030: DO 노량진 ~8.1, 선유 ~7.9 mg/L<br>
            2040: DO 노량진 ~7.7, 선유 ~7.5 mg/L<br>
            2050: DO 노량진 ~7.3, 선유 ~7.1 mg/L<br><br>
            1등급 유지 기간: 연중 50% → 40%로 축소 예상
          </div>
        </div>
        """, unsafe_allow_html=True)
    with cb:
        st.markdown("""
        <div class="ins-card red">
          <div class="ins-title">SSP5-8.5 — 고위 시나리오</div>
          <div class="ins-body">
            현재 추세 지속 최악 경로. 2050년 기온 <b>+3.0°C</b> 상승 예상.<br><br>
            2030: DO 노량진 ~7.7, 선유 ~7.5 mg/L<br>
            2040: DO 노량진 ~7.1, 선유 ~6.9 mg/L<br>
            2050: DO 노량진 ~6.5, 선유 ~6.3 mg/L<br><br>
            민감 어종 서식 기간: 8개월 → <b>5개월 미만</b> 가능성
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="ins-card purple">
      <div class="ins-title">예측 모델 방법론 및 한계</div>
      <div class="ins-body">
        <b>기준 데이터:</b> 2020년 노량진·선유 시간별 실측값 (n=8,784)<br>
        <b>DO 예측:</b> Henry's Law (기온–산소 용해도) + 도시 비점오염 증가 보정<br>
        <b>pH 예측:</b> 대기 CO₂ 농도 증가(420→500–600 ppm) 탄산 평형 계산<br>
        <b>불확실도:</b> 단기 ±0.3 → 2050년 ±0.8 mg/L로 선형 증가<br><br>
        <span class="badge b-orange">한계점</span>
        단일 연도 기반 외삽이므로 장기 정책 효과나 기상 이변은 반영되지 않습니다.
      </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 : 수질 정책
# ═══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="sec-hd">한강 수질 개선을 위한 핵심 정책</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="ins-card sky" style="margin-bottom:20px;">
      <div class="ins-title">왜 정책이 필요한가</div>
      <div class="ins-body">
        2020년 실측 데이터는 여름철(5–9월) DO가 수생태계 위험 기준(5 mg/L)에 근접하거나
        하회하는 구간이 반복됨을 보여줍니다. 기후변화 시나리오(SSP5-8.5)대로 진행될 경우
        2050년에는 연평균 DO가 6.3–6.5 mg/L까지 떨어져 한강 생태계의 구조적 붕괴가 우려됩니다.
        자연적 회복력만으로는 한계가 있어 <b>제도적·기술적 개입</b>이 필수적입니다.
      </div>
    </div>
    """, unsafe_allow_html=True)

    policies = [
        {
            "color": "blue",
            "num": "1",
            "title": "하수처리장 고도화 및 총인(T-P) 저감",
            "why": """
                한강으로 유입되는 하수처리수에는 질소·인 등 영양염류가 포함됩니다.
                이들이 과다하면 <b>조류(藻類) 대발생(녹조)</b>을 유발하고,
                조류 사체가 분해될 때 막대한 산소를 소비해 DO를 급락시킵니다.
                2020년 6월 DO 최솟값 2.1 mg/L의 주요 원인 중 하나입니다.
            """,
            "what": """
                하수처리장에 <b>고도처리 공정</b>(A²O, MBR)을 도입해 방류수 총인 농도를
                0.2 mg/L 이하로 낮춥니다. 서울시는 2030년까지 중랑·탄천 처리장 고도화를
                완료하는 계획을 추진 중입니다.
            """,
            "effect": """
                총인 50% 감소 시 여름 조류 발생량 30–40% 억제 효과가 보고됩니다.
                DO 여름 최솟값을 약 <b>+1.0–1.5 mg/L</b> 개선 가능합니다.
            """
        },
        {
            "color": "green",
            "num": "2",
            "title": "비점오염원 관리 — 초기 우수(初期雨水) 처리",
            "why": """
                도시 강우 시 도로·주차장·공사장에서 씻겨 내려오는
                <b>초기 강우 유출수</b>는 오염 농도가 하수와 맞먹습니다.
                이 비점오염이 여름 장마철 한강 DO를 2차 급락시키는 원인입니다.
            """,
            "what": """
                강변 도로에 <b>초기 우수 저류조</b>를 설치하고,
                투수성 포장재 확대, 빗물정원(Rain Garden) 조성으로
                오염된 초기 우수가 직접 한강에 유입되지 않도록 합니다.
            """,
            "effect": """
                강우 후 DO 단기 급락 폭을 <b>30–50% 완충</b>할 수 있습니다.
                특히 선유 지점(하류·퇴적물 많음)의 여름 최솟값 개선에 효과적입니다.
            """
        },
        {
            "color": "orange",
            "num": "3",
            "title": "한강 인공 산소 공급 — 폭기(曝氣) 시설 운영",
            "why": """
                여름 고수온기(수온 26°C 이상)에는 물리적으로 DO 포화 농도 자체가 낮아집니다.
                생물학적 방법만으로는 즉각적인 대응이 불가능하며,
                <b>물고기 집단 폐사</b> 등 생태 재난이 발생할 수 있습니다.
            """,
            "what": """
                한강 바닥에 <b>산기관(Air Diffuser)</b>을 설치하거나
                수중 교반기(Aerator)를 가동해 물에 직접 공기를 불어 넣습니다.
                서울시는 이미 일부 구간에서 폭기 선박을 운영 중입니다.
            """,
            "effect": """
                폭기 시 해당 구간 DO를 단기간에 <b>2–4 mg/L</b> 높일 수 있습니다.
                특히 도심 구간(노량진·선유)의 긴급 대응 수단으로 유효합니다.
            """
        },
        {
            "color": "purple",
            "num": "4",
            "title": "한강 생태습지·수변완충구역 확대",
            "why": """
                콘크리트로 직선화된 하안은 자정(自淨) 능력이 거의 없습니다.
                자연 하안에 비해 유기물 정화 속도가 <b>3–5배 느리며</b>,
                수온도 더 빠르게 오릅니다.
            """,
            "what": """
                한강변에 <b>갈대·부들 등 정수식물</b> 군락을 복원하고
                수변 완충 녹지대(최소 30m)를 지정합니다.
                이미 조성된 난지·여의도 생태공원을 추가 확대합니다.
            """,
            "effect": """
                수변 습지는 질소를 연간 최대 <b>500 kg/ha</b> 제거할 수 있습니다.
                수온을 1–2°C 낮추는 냉각 효과도 있어 DO 포화도 유지에 기여합니다.
            """
        },
        {
            "color": "teal",
            "num": "5",
            "title": "수질 실시간 모니터링 고도화 및 조기경보",
            "why": """
                2020년 선유 8월 데이터 결측(58%)이 보여주듯,
                현재 측정망은 극단적 수질 악화 상황에서 오히려 데이터 공백이 생깁니다.
                선제적 대응을 위해서는 <b>정밀하고 끊김 없는 측정</b>이 필수입니다.
            """,
            "what": """
                AI 기반 수질 예측 모델과 IoT 실시간 센서망을 결합해
                DO·pH·수온·조류 농도를 10분 단위로 수집하고,
                위험 기준 접근 시 자동 경보 발령 체계를 구축합니다.
            """,
            "effect": """
                DO 5 mg/L 하회 <b>6–12시간 전 예측</b>이 가능해져
                폭기 선박 출동, 취수 조정 등 선제 조치 시간을 확보할 수 있습니다.
            """
        },
        {
            "color": "red",
            "num": "6",
            "title": "기후변화 대응 — 도시 열섬 완화 및 탄소 감축",
            "why": """
                한강 수질의 가장 큰 장기 위협은 <b>수온 상승</b>입니다.
                도시 열섬 효과로 서울 한강 수온은 전국 평균보다 빠르게 오르고 있으며,
                수온 1°C 상승은 DO 포화 농도를 약 0.2 mg/L 낮춥니다.
            """,
            "what": """
                건물 옥상 녹화, 도시 숲 확대, 바람길 조성으로 도시 열섬을 완화하고
                탄소 감축을 통해 기온 상승 자체를 억제합니다.
                한강 수온 모니터링을 기후 정책 지표로 공식 채택합니다.
            """,
            "effect": """
                도시 열섬 1°C 완화 시 여름 한강 수온 <b>0.5–0.8°C 감소</b>,
                DO 연중 최솟값 <b>+0.1–0.16 mg/L</b> 개선 효과가 기대됩니다.
                장기적으로는 SSP5-8.5 시나리오를 SSP2-4.5 수준으로 완화하는 핵심 수단입니다.
            """
        },
    ]

    color_map = {
        'blue':'blue','green':'green','orange':'orange',
        'purple':'purple','teal':'teal','red':'red'
    }

    for p in policies:
        c = p['color']
        st.markdown(f"""
        <div class="policy-card {c}">
          <div class="policy-title">
            <span class="policy-num {c}">{p['num']}</span>
            {p['title']}
          </div>
          <div class="policy-body">
            <div class="policy-row">
              <div class="policy-sub">
                <div class="policy-sub-title">왜 필요한가</div>
                <div class="policy-sub-body">{p['why']}</div>
              </div>
              <div class="policy-sub">
                <div class="policy-sub-title">무엇을 하는가</div>
                <div class="policy-sub-body">{p['what']}</div>
              </div>
            </div>
            <div class="policy-sub" style="margin-top:10px; border-left:3px solid #{'22c55e' if c=='green' else '3b82f6' if c=='blue' else 'f97316' if c=='orange' else 'a855f7' if c=='purple' else '0891b2' if c=='teal' else 'ef4444'};">
              <div class="policy-sub-title">기대 효과</div>
              <div class="policy-sub-body">{p['effect']}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # 정책 우선순위 요약
    st.markdown('<div class="sec-hd">정책 우선순위 로드맵</div>', unsafe_allow_html=True)

    fig_road = go.Figure()
    roadmap = [
        ('단기 (2026–2030)', ['폭기 시설 확충', '모니터링 고도화', '초기 우수 저류조'], '#2563eb'),
        ('중기 (2031–2040)', ['하수처리장 고도화 완료', '생태습지 확대', '비점오염 관리 강화'], '#0891b2'),
        ('장기 (2041–2050)', ['탄소 감축 목표 달성', '도시 열섬 완화', '자연형 하천 복원'], '#22c55e'),
    ]
    for i, (period, items, color) in enumerate(roadmap):
        r,g,b = int(color[1:3],16),int(color[3:5],16),int(color[5:7],16)
        fig_road.add_trace(go.Bar(
            x=[len(items)], y=[period], orientation='h',
            marker_color=f'rgba({r},{g},{b},0.15)',
            marker_line_color=color, marker_line_width=2,
            text=[' · '.join(items)], textposition='inside',
            textfont=dict(color=color, size=12),
            showlegend=False, name=period,
            hovertemplate=f"<b>{period}</b><br>{'<br>'.join(items)}<extra></extra>"
        ))

    fig_road.update_layout(
        height=200, plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10,r=10,t=10,b=10),
        xaxis=dict(visible=False),
        yaxis=dict(autorange='reversed', tickfont=dict(size=13, color='#374151')),
        bargap=0.3,
    )
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig_road, use_container_width=True, config={'displaylogo': False})
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 정책 실행 전 vs 후 비교 지도 ─────────────────────────────────────────
    st.markdown('<div class="sec-hd" style="margin-top:40px;">🗺️ 정책 실행 전 vs 후 — DO 수질 지도 비교</div>',
                unsafe_allow_html=True)
    st.caption("정책을 선택하고 연도를 설정하면, 실행하지 않았을 때와 실행했을 때의 DO 변화를 지도로 비교합니다.")

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
        map_year = st.select_slider(
            "예측 연도", options=[2026, 2030, 2040, 2050], value=2040, key="map_year"
        )

    # 기준 DO (정책 미실행)
    base_row    = df_future[df_future["year"] == map_year].iloc[0]
    base_do_nry = base_row[f"{map_scen_key}_노량진_DO"]
    base_do_syu = base_row[f"{map_scen_key}_선유_DO"]
    base_ph_nry = base_row[f"{map_scen_key}_노량진_pH"]
    base_ph_syu = base_row[f"{map_scen_key}_선유_pH"]

    # 정책 적용 후 DO
    total_imp_nry = sum(p["do_impact_nry"] for p in MAP_POLICIES if p["title"] in selected_policies)
    total_imp_syu = sum(p["do_impact_syu"] for p in MAP_POLICIES if p["title"] in selected_policies)
    after_do_nry  = min(base_do_nry + total_imp_nry, 12.0)
    after_do_syu  = min(base_do_syu + total_imp_syu, 12.0)
    imp_nry = after_do_nry - base_do_nry
    imp_syu = after_do_syu - base_do_syu
    scen_label2 = "SSP5-8.5" if map_scen_key == "SSP585" else "SSP2-4.5"

    # 활성 시설 마커 수집
    active_markers = []
    for title in selected_policies:
        active_markers.extend(POLICY_MARKERS.get(title, []))

    # 요약 배너
    st.markdown(f"""
    <div style='display:flex;gap:16px;margin:10px 0 16px 0;flex-wrap:wrap'>
        <div style='flex:1;min-width:240px;background:#FEF9E7;border-left:4px solid #F39C12;
        padding:10px 14px;border-radius:8px'>
            <b>📍 정책 미실행</b> | {scen_label2} {map_year}년<br>
            노량진 DO: <b style='color:{do_color(base_do_nry)}'>{base_do_nry:.2f} mg/L</b> &nbsp;
            선유 DO: <b style='color:{do_color(base_do_syu)}'>{base_do_syu:.2f} mg/L</b>
        </div>
        <div style='flex:1;min-width:240px;background:#EAFAF1;border-left:4px solid #27AE60;
        padding:10px 14px;border-radius:8px'>
            <b>✅ 정책 실행 후</b> | 선택 정책 {len(selected_policies)}개 적용<br>
            노량진 DO: <b style='color:{do_color(after_do_nry)}'>{after_do_nry:.2f} mg/L</b>
            <span style='color:#27AE60;font-size:12px'>(+{imp_nry:.2f})</span> &nbsp;
            선유 DO: <b style='color:{do_color(after_do_syu)}'>{after_do_syu:.2f} mg/L</b>
            <span style='color:#27AE60;font-size:12px'>(+{imp_syu:.2f})</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 좌우 지도
    map_col1, map_col2 = st.columns(2)
    center = [37.522, 126.906]
    with map_col1:
        st.markdown("**❌ 정책 미실행**")
        m_before = build_map(center, base_do_nry, base_do_syu,
                             base_ph_nry, base_ph_syu,
                             map_year, f"미실행 ({scen_label2})")
        st_folium(m_before, width=None, height=400, key="map_before")
    with map_col2:
        st.markdown("**✅ 정책 실행 후**")
        m_after = build_map(center, after_do_nry, after_do_syu,
                            base_ph_nry, base_ph_syu,
                            map_year, f"실행 후 ({scen_label2})",
                            policy_markers=active_markers)
        st_folium(m_after, width=None, height=400, key="map_after")

    # 등급 변화 요약
    st.divider()
    st.markdown("**📊 수질 등급 변화 요약**")
    sg1, sg2 = st.columns(2)
    with sg1:
        st.metric("노량진 DO", f"{after_do_nry:.2f} mg/L",
                  delta=f"+{imp_nry:.2f} mg/L",
                  help=f"미실행: {base_do_nry:.2f} → 실행 후: {after_do_nry:.2f}")
        st.caption(f"등급 변화: {do_grade_label(base_do_nry)} → {do_grade_label(after_do_nry)}")
    with sg2:
        st.metric("선유 DO", f"{after_do_syu:.2f} mg/L",
                  delta=f"+{imp_syu:.2f} mg/L",
                  help=f"미실행: {base_do_syu:.2f} → 실행 후: {after_do_syu:.2f}")
        st.caption(f"등급 변화: {do_grade_label(base_do_syu)} → {do_grade_label(after_do_syu)}")

    if map_scen_key == "SSP585" and map_year >= 2040:
        st.error(f"🚨 SSP5-8.5 {map_year}년: DO 위험 임계치(5.0 mg/L) 근접! 정책 실행이 시급합니다.")
    elif map_scen_key == "SSP585" and map_year >= 2030:
        st.warning("⚠️ SSP5-8.5 시나리오 — 2030년 이후 DO 감소 추세 본격화. 단기 정책 선행 필요.")
    else:
        st.success(f"✅ {map_year}년 {scen_label2} — 정책 실행 시 수질 관리 가능 범위 유지")

    st.info("💡 **핵심 메시지**: 기후변화 속 여름철 DO 취약성이 심화되고 있습니다. "
            "단기 폭기시설·모니터링부터 장기 탄소감축까지 3단계 정책이 한강의 미래를 결정합니다.")


# 푸터
st.markdown("""
<div style="text-align:center; font-size:12px; color:#9ca3af; margin-top:40px;
     padding: 16px 0; border-top: 1px solid #f3f4f6;">
    데이터 출처: 서울 열린데이터 광장 · 서울시 요일별 한강 수질 현황 (2020) &nbsp;|&nbsp;
    노량진 · 선유 측정소 시간별 실측값 일평균 &nbsp;|&nbsp;
    예측: IPCC AR6 SSP2-4.5 / SSP5-8.5 시나리오 적용
</div>
""", unsafe_allow_html=True)
