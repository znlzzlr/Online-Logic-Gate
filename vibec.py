import streamlit as st
import random
import colorsys
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="프리미엄 컬러 탐색기", layout="centered")

# --- 유틸리티 함수 ---
def hex_to_hls(hex_str):
    hex_str = hex_str.lstrip('#')
    r, g, b = tuple(int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return colorsys.rgb_to_hls(r, g, b)

def hls_to_hex(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))

# 세션 상태 초기화
if 'count' not in st.session_state:
    st.session_state.count = 1
    st.session_state.choices = [] # 선택한 색상들의 HEX 기록
    st.session_state.hls_history = [] # 그래프용 HLS 기록
    st.session_state.current_base_hls = (random.random(), 0.5, 0.5)
    st.session_state.show_result = False

# --- 사이드바: 분석 모니터링 ---
with st.sidebar:
    st.header("📊 분석 데이터")
    if st.session_state.choices:
        st.write("최근 선택한 색상")
        for c in st.session_state.choices[-5:]:
            st.color_picker(c, c, key=f"picker_{c}_{random.random()}")
    
    variation = max(0.02, 0.3 * (1 - min(st.session_state.count / 25, 0.9)))
    st.metric("현재 정밀도", f"{(1-variation)*100:.1f}%")

# --- 메인 화면 ---
st.title("🎨 진화하는 컬러 탐색기")

if st.session_state.show_result:
    st.balloons()
    final_color = st.session_state.choices[-1] if st.session_state.choices else "#FFFFFF"
    
    st.subheader("🎯 최종 분석 결과")
    st.markdown(f"""
        <div style='background-color: {final_color}; padding: 80px; border-radius: 20px; text-align: center; border: 5px solid #fff; box-shadow: 0px 10px 30px rgba(0,0,0,0.1);'>
            <h1 style='color: white; text-shadow: 2px 2px 10px rgba(0,0,0,0.3); margin: 0;'>{final_color.upper()}</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # --- 거쳐온 색상 경로 그래프 ---
    st.write("---")
    st.subheader("📉 취향 탐색 경로 (Hue - Lightness)")
    if st.session_state.hls_history:
        df = pd.DataFrame(st.session_state.hls_history, columns=['Hue', 'Lightness', 'Saturation'])
        df['Step'] = range(1, len(df) + 1)
        st.line_chart(df.set_index('Step')[['Hue', 'Lightness']])
        st.caption("해석: Hue(색상값)와 Lightness(밝기)가 일정 수치로 수렴할수록 당신의 취향이 확고해졌음을 의미합니다.")

    if st.button("새로운 탐색 시작하기", use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

else:
    # 진행도 안내
    st.write(f"### 분석 단계: {st.session_state.count} / 20+")
    st.progress(min(st.session_state.count / 20, 1.0))

    # 9가지 색상 생성 로직
    def generate_balanced_colors(base_hls, count):
        colors = []
        h, l, s = base_hls
        var = max(0.02, 0.3 * (1 - min(count / 25, 0.9)))
        for i in range(9):
            if i < 2: # 랜덤 (전혀 다른 색)
                new_h, new_l, new_s = random.random(), random.uniform(0.2, 0.8), random.uniform(0.2, 0.8)
            elif i < 4: # 보완 (보색 근처)
                new_h, new_l, new_s = (h + 0.5) % 1.0, l, s
            else: # 정밀 (취향 강화)
                new_h = (h + random.uniform(-var, var)) % 1.0
                new_l = max(0.1, min(0.9, l + random.uniform(-var, var)))
                new_s = max(0.1, min(0.9, s + random.uniform(-var, var)))
            colors.append(hls_to_hex(new_h, new_l, new_s))
        random.shuffle(colors)
        return colors

    current_colors = generate_balanced_colors(st.session_state.current_base_hls, st.session_state.count)

    # 3x3 격자 레이아웃
    st.markdown("""<style>.color-tile { height: 120px; border-radius: 10px; margin-bottom: 5px; border: 1px solid #eee; }</style>""", unsafe_allow_html=True)

    for r in range(3):
        cols = st.columns(3)
        for c in range(3):
            idx = r * 3 + c
            color = current_colors[idx]
            with cols[c]:
                st.markdown(f"<div class='color-tile' style='background-color: {color};'></div>", unsafe_allow_html=True)
                if st.button(f"선택 {idx+1}", key=f"t_{st.session_state.count}_{idx}", use_container_width=True):
                    st.session_state.current_base_hls = hex_to_hls(color)
                    st.session_state.choices.append(color)
                    st.session_state.hls_history.append(st.session_state.current_base_hls)
                    st.session_state.count += 1
                    st.rerun()

    # --- 추가된 제어 영역 ---
    st.write("---")
    c1, c2 = st.columns([1, 1])
    
    with c1:
        # 패스 버튼: 현재 기준점은 유지하되 색상만 다시 섞음
        if st.button("⏩ 마음에 드는 색이 없음 (새로고침)", use_container_width=True):
            st.rerun()
            
    with c2:
        # 결과 보기 버튼 제어
        if st.session_state.count > 20:
            if st.button("🎯 결과 분석 완료!", type="primary", use_container_width=True):
                st.session_state.show_result = True
                st.rerun()
        else:
            st.button(f"분석 데이터 수집 중... ({st.session_state.count}/20)", disabled=True, use_container_width=True)
    
    st.caption("알림: '새로고침'을 눌러도 분석 단계는 유지되며, 더 정교한 색상을 불러옵니다.")