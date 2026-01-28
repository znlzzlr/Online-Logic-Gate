import streamlit as st
from fuzzywuzzy import fuzz
import re

# --- 1. 음악 데이터베이스 ---
music_db = [
    {"title": "작은 별", "melody": "C C G G A A G", "artist": "동요", "img": "🌟"},
    {"title": "나비야", "melody": "G E E F D D C D E F G G G", "artist": "동요", "img": "🦋"},
    {"title": "학교종", "melody": "G G A A G G E G G E E D", "artist": "동요", "img": "🔔"},
    {"title": "비행기", "melody": "E D C D E E E D D D E G G", "artist": "동요", "img": "✈️"},
    {"title": "엘리제를 위하여", "melody": "E Eb E Eb E B D C A", "artist": "베토벤", "img": "🎹"},
    {"title": "환희의 송가", "melody": "E E F G G F E D C C D E E D D", "artist": "베토벤", "img": "🎻"},
]

# --- 2. 이명동음 및 한글 음정 표준화 로직 ---
enharmonic_map = {
    "Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#",
    "도#": "C#", "레#": "D#", "파#": "F#", "솔#": "G#", "라#": "A#",
    "레b": "C#", "미b": "D#", "솔b": "F#", "라b": "G#", "시b": "A#",
    "도": "C", "레": "D", "미": "E", "파": "F", "솔": "G", "라": "A", "시": "B"
}

def standardize_melody(melody_str):
    """모든 입력된 멜로디를 Sharp 기반의 표준 영문 음정으로 변환"""
    # 1. 샵(#)이나 플랫(b)이 붙은 음정을 우선적으로 찾기 위한 정규식
    # 한글(도#) 또는 영문(C#, Db) 패턴 매칭
    pattern = r'([A-G][b#]?|[가-힣][#b]?)'
    notes = re.findall(pattern, melody_str, re.IGNORECASE)
    
    standardized = []
    for n in notes:
        # 매핑 테이블에서 변환 (없으면 대문자 처리)
        std_n = enharmonic_map.get(n, n.upper())
        # 혹시 모를 소문자 b 처리 (ex: eb -> Eb -> D#)
        if n.lower().endswith('b') and n.capitalize() in enharmonic_map:
            std_n = enharmonic_map[n.capitalize()]
        standardized.append(std_n)
    
    return " ".join(standardized)

# --- 3. UI 스타일 및 레이아웃 ---
st.set_page_config(page_title="Melody Finder Pro", page_icon="🎵")

st.markdown("""
    <style>
    .main { background-color: #f9f9fb; }
    .result-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 6px solid #4A90E2;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
        padding: 10px 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎶 Melody Search Master")
st.write("가사나 제목이 기억나지 않을 때, **생각나는 음정**을 적어보세요.")

# --- 4. 검색 인터페이스 ---
with st.container():
    st.info("💡 **팁:** '도레미' 혹은 'CDE' 처럼 띄어쓰기 없이 입력해도 괜찮습니다. (플랫음정도 자동 변환됩니다)")
    
    user_input = st.text_input(
        "멜로디 입력", 
        placeholder="예: 솔솔라라솔솔미 / G G A A G G E / 파# 솔 라",
        help="한글 음명과 영문 음명 모두 지원합니다."
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        search_clicked = st.button("음악 찾기", type="primary", use_container_width=True)
    with col2:
        if st.button("입력 지우기"):
            st.rerun()

# --- 5. 결과 분석 및 출력 ---
if user_input or search_clicked:
    if not user_input.strip():
        st.warning("먼저 멜로디를 입력해 주세요.")
    else:
        # 사용자 입력 표준화
        std_user = standardize_melody(user_input)
        
        if not std_user:
            st.error("인식할 수 있는 음정이 없습니다. 음 이름을 정확히 입력했는지 확인해 주세요.")
        else:
            st.markdown(f"🔍 **분석된 음계 패턴:** `{std_user}`")
            
            # 검색 알고리즘
            results = []
            for song in music_db:
                std_db = standardize_melody(song["melody"])
                # 부분 일치 점수 계산
                score = fuzz.partial_ratio(std_user, std_db)
                results.append({**song, "score": score, "std_db": std_db})

            # 점수 높은 순 정렬 (상위 3개)
            top_3 = sorted(results, key=lambda x: x['score'], reverse=True)[:3]

            st.markdown("---")
            st.subheader("🔎 검색 결과")

            # 결과가 0점인 경우 예외 처리
            if top_3[0]['score'] == 0:
                st.write("일치하는 곡을 찾지 못했습니다. 멜로디를 조금 더 길게 입력해 보세요.")
            else:
                for res in top_3:
                    st.markdown(f"""
                        <div class="result-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <span style="font-size: 24px;">{res['img']}</span>
                                    <span style="font-size: 20px; font-weight: bold; margin-left: 10px;">{res['title']}</span>
                                    <div style="color: #777; font-size: 14px; margin-top: 5px; margin-left: 40px;">{res['artist']}</div>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 22px; font-weight: bold; color: #4A90E2;">{res['score']}%</div>
                                    <div style="font-size: 11px; color: #aaa;">매칭률</div>
                                </div>
                            </div>
                            <div style="margin-top: 15px; padding: 10px; background: #f0f2f6; border-radius: 8px; font-family: monospace;">
                                🎹 {res['melody']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

st.divider()
st.caption("Melody Finder - 텍스트 기반 멜로디 검색 도구")