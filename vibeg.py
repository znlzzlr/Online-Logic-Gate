import streamlit as st
import numpy as np
import random

# 1. 초기 설정 및 색상 정의
TILE_COLORS = {
    0: "#cdc1b4", 2: "#eee4da", 4: "#ede0c8", 8: "#f2b179", 
    16: "#f59563", 32: "#f67c5f", 64: "#f65e3b", 128: "#edcf72", 
    256: "#edcc61", 512: "#edc850", 1024: "#edc53f", 2048: "#edc22e",
}

def init_game():
    st.session_state.board = np.zeros((4, 4), dtype=int)
    st.session_state.score = 0
    add_new_tile(); add_new_tile()

def add_new_tile():
    empty_cells = list(zip(*np.where(st.session_state.board == 0)))
    if empty_cells:
        r, c = random.choice(empty_cells)
        st.session_state.board[r, c] = 2 if random.random() < 0.9 else 4

def push_line(line):
    non_zero = line[line != 0]
    new_line = np.zeros(4, dtype=int)
    skip, idx = False, 0
    for i in range(len(non_zero)):
        if skip:
            skip = False; continue
        if i + 1 < len(non_zero) and non_zero[i] == non_zero[i+1]:
            new_line[idx] = non_zero[i] * 2
            st.session_state.score += new_line[idx]
            skip = True
        else:
            new_line[idx] = non_zero[i]
        idx += 1
    return new_line

def move(direction):
    # 0:Left, 1:Up, 2:Right, 3:Down
    board = np.rot90(st.session_state.board, direction)
    new_board = np.array([push_line(row) for row in board])
    final_board = np.rot90(new_board, -direction)
    
    if not np.array_equal(st.session_state.board, final_board):
        st.session_state.board = final_board
        add_new_tile()
        return True
    return False

# --- 페이지 설정 ---
st.set_page_config(page_title="Instant 2048", layout="centered")

if 'board' not in st.session_state:
    init_game()

# --- CSS: 디자인 및 색상 ---
st.markdown("""
    <style>
    .grid-container {
        display: grid; grid-template-columns: repeat(4, 1fr);
        gap: 12px; background-color: #bbada0;
        padding: 12px; border-radius: 10px; width: 400px; margin: 0 auto;
    }
    .tile {
        width: 85px; height: 85px; border-radius: 5px;
        display: flex; align-items: center; justify-content: center;
        font-size: 32px; font-weight: bold; font-family: 'Clear Sans', sans-serif;
    }
    /* 조작을 위한 숨겨진 버튼 스타일 */
    .stButton > button { display: none; }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"<h1 style='text-align: center; color: #776e65;'>Score: {st.session_state.score}</h1>", unsafe_allow_html=True)

# --- 보드 출력 ---
grid_html = '<div class="grid-container">'
for row in st.session_state.board:
    for val in row:
        bg = TILE_COLORS.get(val, "#3c3a32")
        color = "#776e65" if val <= 4 else "#f9f6f2"
        grid_html += f'<div class="tile" style="background-color: {bg}; color: {color};">{" " if val==0 else val}</div>'
grid_html += '</div>'
st.markdown(grid_html, unsafe_allow_html=True)

# --- JavaScript: 키보드 입력 가로채기 ---
# WASD 및 방향키를 눌렀을 때 Streamlit의 숨겨진 버튼을 클릭하게 함
st.components.v1.html("""
<script>
    const doc = window.parent.document;
    doc.onkeydown = function(e) {
        let btnIndex = -1;
        switch(e.key.toLowerCase()) {
            case 'arrowleft': case 'a': btnIndex = 0; break;
            case 'arrowup': case 'w': btnIndex = 1; break;
            case 'arrowright': case 'd': btnIndex = 2; break;
            case 'arrowdown': case 's': btnIndex = 3; break;
        }
        if (btnIndex !== -1) {
            const buttons = doc.querySelectorAll('.stButton button');
            if (buttons[btnIndex]) {
                buttons[btnIndex].click();
            }
        }
    };
</script>
""", height=0)

# --- 숨겨진 조작 버튼 (JS가 클릭함) ---
cols = st.columns(4)
with cols[0]:
    if st.button("L"): move(0); st.rerun()
with cols[1]:
    if st.button("U"): move(1); st.rerun()
with cols[2]:
    if st.button("R"): move(2); st.rerun()
with cols[3]:
    if st.button("D"): move(3); st.rerun()

if st.button("New Game", key="reset"):
    init_game(); st.rerun()

st.markdown("<p style='text-align:center;'>상하좌우 방향키 또는 WASD로 조작하세요!</p>", unsafe_allow_html=True)