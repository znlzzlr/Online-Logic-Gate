import streamlit as st
import random
import datetime

# 1. 세션 상태 초기화
if 'sleep_mode' not in st.session_state:
    st.session_state.sleep_mode = False

kafka_quotes = [
    "잠은 가장 무구한 존재이며, 불면은 가장 유죄인 존재이다.",
    "나는 잠을 자야 한다. 나의 불면증은 나를 파괴하고 있다.",
    "잠이 들지 않는 밤, 나는 오직 그대만을 생각하며 어둠 속에서 길을 잃는다.",
    "기상 시간의 고통보다 더한 고통은, 잠들지 못하는 밤의 기록이다."
    "집이 가고싶은가?"
]

if not st.session_state.sleep_mode:
    # [일반 모드]
    st.title("🌙 수면 관리 시스템")
    wake_up_time = st.time_input("기상 시간 설정", datetime.time(7, 0))
    
    if st.button("수면 시작", use_container_width=True):
        st.session_state.sleep_mode = True
        st.rerun()

else:
    # [수면 모드] 완벽 암전 CSS
    st.markdown("""
        <style>
        /* 모든 요소의 배경을 검은색으로 강제 */
        [data-testid="stAppViewContainer"], 
        [data-testid="stHeader"], 
        [data-testid="stSidebar"],
        .main {
            background-color: #000000 !important;
            color: #1a1a1a !important;
        }
        
        /* 텍스트 색상을 아주 어둡게 조절 (카프카 명언만 살짝 보이게) */
        h1, h2, h3, p, span, div {
            color: #1a1a1a !important;
        }
        
        /* 버튼 테두리 제거 및 어둡게 처리 */
        button {
            border: none !important;
            background-color: #050505 !important;
            color: #111111 !important;
        }
        
        /* 스크롤바 숨기기 */
        ::-webkit-scrollbar {
            display: none;
        }
        </style>
        """, unsafe_allow_html=True)

    # 화면 중앙 정렬을 위한 여백
    st.write(" ")
    st.write(" ")
    st.title("KAFKA'S NIGHT")
    st.markdown(f"### *{random.choice(kafka_quotes)}*")
    
    # 해제 버튼
    if st.button("현실로 복귀"):
        st.session_state.sleep_mode = False
        st.rerun()