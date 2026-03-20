# Tab 4: 수질 해석 (이어서 작성)
    for color, title, body in insights:
        st.markdown(f"""
        <div class="ins-card {color}">
          <div class="ins-title">{title}</div>
          <div class="ins-body">{body}</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# TAB 5 : 미래 예측 (시나리오 분석)
# ═══════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="sec-hd">기후변화 시나리오별 2050 수질 예측 (SSP 시나리오)</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.write("### 🔮 시나리오 선택")
        ssp_choice = st.radio(
            "기후 시나리오",
            ["SSP2-4.5 (중간 저감)", "SSP5-8.5 (고탄소 배출)"],
            help="SSP5-8.5는 현재 추세대로 탄소가 배출될 경우의 최악의 시나리오입니다."
        )
        selected_ssp = "SSP245" if "2-4.5" in ssp_choice else "SSP585"
        
        st.info("""
        **예측 근거:**
        기온 1°C 상승 시 포화 용존산소량은 약 2% 감소하며, 미생물 활동 증가로 인한 산소 소비량은 가속화됩니다.
        """)

    with col2:
        fig_f = go.Figure()
        years = df_future["year"]
        
        for stn in ["노량진", "선유"]:
            col_name = f"{selected_ssp}_{stn}_DO"
            fig_f.add_trace(go.Scatter(
                x=years, y=df_future[col_name],
                name=f"{stn} 예측 DO",
                mode='lines+markers+text',
                text=[f"{v}mg/L" for v in df_future[col_name]],
                textposition="top center",
                line=dict(width=3, dash='solid' if stn=="노량진" else 'dot')
            ))
        
        fig_f.add_hline(y=5.0, line_dash="dash", line_color="red", annotation_text="어류 생존 한계선 (5.0)")
        fig_f.update_layout(
            title=f"2050년까지의 DO 변화 전망 ({ssp_choice})",
            xaxis_title="연도", yaxis_title="DO (mg/L)",
            height=400, template="plotly_white"
        )
        st.plotly_chart(fig_f, use_container_width=True)

    st.warning("⚠️ **분석 결과:** 최악의 시나리오(SSP5-8.5) 적용 시, 2050년 한강 하류(선유)의 여름철 평균 DO는 **5.37mg/L**까지 하락하여 상시적인 수생태계 위기가 우려됩니다.")


# ═══════════════════════════════════════════════════════════════
# TAB 6 : 수질 정책 (지도 및 대응 방안)
# ═══════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="sec-hd">한강 수질 개선을 위한 단계별 정책 제언</div>', unsafe_allow_html=True)
    
    # 정책 선택
    selected_policy = st.selectbox("상세 정책 확인", [p["title"] for p in POLICIES])
    policy_info = next(p for p in POLICIES if p["title"] == selected_policy)
    
    # 지도 출력
    c1, c2 = st.columns([2, 1])
    
    with c1:
        # 미래 예측 데이터 기반 기본값 (2050년 SSP585 기준)
        base_do_nry = 5.54
        base_do_syu = 5.37
        
        # 정책 효과 적용
        improved_do_nry = base_do_nry + policy_info["do_impact_nry"]
        improved_do_syu = base_do_syu + policy_info["do_impact_syu"]
        
        m = build_map(
            center=[37.52, 126.92],
            do_nry=improved_do_nry, do_syu=improved_do_syu,
            ph_nry=7.137, ph_syu=7.167,
            year=2050, label=f"정책 적용: {selected_policy}",
            policy_markers=POLICY_MARKERS_MAP.get(selected_policy)
        )
        st_folium(m, width=800, height=450)
    
    with c2:
        st.markdown(f"""
        <div class="policy-card">
            <div class="policy-title">
                <span class="policy-num">{policy_info['icon']}</span> {policy_info['title']}
            </div>
            <div class="policy-body">
                <b>단계:</b> {policy_info['phase_label']}<br>
                <b>기대 효과:</b> {policy_info['effect']}<br><br>
                {policy_info['detail']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("#### 📈 정책 적용 후 DO 변화 (2050)")
        st.metric("노량진 지점", f"{improved_do_nry:.2f} mg/L", f"+{policy_info['do_impact_nry']} mg/L")
        st.metric("선유 지점", f"{improved_do_syu:.2f} mg/L", f"+{policy_info['do_impact_syu']} mg/L")

# ═══════════════════════════════════════════════════════════════
# 하단 푸터
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
st.caption("본 대시보드는 공공데이터포털의 한강 수질 측정망 데이터를 기반으로 제작되었습니다. 미래 예측치는 기후변화 시나리오에 따른 가상 모델링 결과입니다.")
""", unsafe_allow_html=True)
