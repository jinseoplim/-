import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="강의실 자리 배치", layout="wide")

# [디자인] 모든 버튼의 규격을 '초록 네모'와 100% 일치시키는 CSS
st.markdown("""
    <style>
    /* 1. 전체 여백 및 간격 제로화 (좌석 가로폭 확보) */
    [data-testid="stAppViewContainer"] { padding: 0.5rem 0.05rem !important; }
    [data-testid="stHorizontalBlock"] { gap: 1px !important; flex-wrap: nowrap !important; }
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0px !important; padding: 0px 0.2px !important; }

    /* 2. [핵심] 모든 버튼의 사이즈를 강제로 고정 */
    /* 숫자가 써있든 이름이 써있든 이 규격(width: 100%, height: 28px)을 무조건 따릅니다 */
    .stButton > button {
        width: 100% !important;   /* 칸의 가로를 꽉 채움 */
        height: 28px !important;  /* 높이를 낮게 고정하여 '옆으로 넓은' 직사각형 생성 */
        
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        
        padding: 0px !important;
        font-size: 9px !important; 
        font-weight: 700 !important;
        line-height: 1 !important;
        white-space: nowrap !important;
        letter-spacing: -0.8px !important;
        border-radius: 1px !important;
        border: 0.5px solid #444 !important;
        
        /* 내용이 길어도 박스 크기가 변하지 않도록 고정 */
        overflow: hidden !important;
        text-overflow: clip !important;
    }

    /* 3. 예약 완료 버튼 (색상만 초록색으로 변경, 크기는 위와 동일하게 유지) */
    div.stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }

    /* 노란색 구조물 디자인 */
    .yellow-box { text-align: center; background-color: #fceea7; color: black; font-weight: bold; border: 1px solid #000; display: flex; align-items: center; justify-content: center; }
    .monitor { height: 30px; font-size: 14px; width: 90%; margin: 0 auto 10px auto; }
    .desk { height: 35px; font-size: 10px; width: 100px; margin-left: auto; line-height: 1.1; margin-bottom: 5px; }
    .door { height: 35px; font-size: 11px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 강의실 자리 배치 시스템")

# 2. 데이터 로드 (nan 박멸 및 실시간 반영)
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    st.cache_data.clear()
    _df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)
    # 이미지에서 보이던 'nan' 글자를 완전히 지웁니다.
    _df = _df.fillna("").replace("nan", "")
    _df['seat_no'] = _df['seat_no'].astype(str).str.strip()
    return _df

df = get_data()

# 3. 사이드바 및 상태 관리
if 'occupied_error' not in st.session_state: st.session_state.occupied_error = False
user_name = st.sidebar.text_input("성함 입력", placeholder="예: 이름")
GAS_URL = "https://script.google.com/macros/s/AKfycbwIyemiDDz0BKptG5z5IWtvtn6aQNiXv0qTZRWWACntR_g3DOqZ7Ix6uXvpmzTuLJf9aQ/exec"

if st.session_state.occupied_error:
    st.error("🎟️ 이미 선택된 좌석입니다! (이선좌)")
    if st.button("알림 닫기 ✖️"):
        st.session_state.occupied_error = False
        st.rerun()

# 4. 레이아웃 시각화 (모니터 및 교탁)
st.markdown("<div class='yellow-box monitor'>모니터</div>", unsafe_allow_html=True)
c_l, c_s, c_r = st.columns([6, 0.2, 6])
with c_r: st.markdown("<div class='yellow-box desk'>👨‍🏫<br>교수님 교탁</div>", unsafe_allow_html=True)
st.write("")

# 5. 좌석 배치 (1~66번)
for r in range(6):
    cols = st.columns([1,1,1,1,1,1, 0.2, 1,1,1,1,1,1])
    for c in range(6):
        l_idx = str((r * 12) + c + 1)
        r_idx = str((r * 12) + c + 7)
        
        def draw_seat(column, idx, key_p):
            if int(idx) > 66: return
            with column:
                owner = df[df['seat_no'] == idx]['owner'].values[0] if not df[df['seat_no'] == idx].empty else ""
                
                # [수정] 빈자리든 예약석이든 상단 CSS 설정(.stButton > button)에 따라 동일한 규격으로 생성됨
                if not owner or owner == "":
                    if st.button(f"{idx}", key=f"{key_p}_{idx}"):
                        if not user_name: st.sidebar.error("이름!")
                        else:
                            st.session_state.occupied_error = False
                            res = requests.get(GAS_URL, params={"seat_no": idx, "owner": user_name})
                            if res.text == "Occupied": st.session_state.occupied_error = True
                            else: st.balloons()
                            st.rerun()
                else:
                    # 예약 완료 (이름 전체 표시, 크기는 숫자 버튼과 동일하게 유지)
                    st.button(f"{owner}", key=f"{key_p}_{idx}", type="primary", disabled=(owner != user_name))

        draw_seat(cols[c], l_idx, "L")
        if r == 0:
            with cols[c+7]: st.button("❌", key=f"x_{c}", disabled=True)
        else:
            draw_seat(cols[c+7], r_idx, "R")

# 6. 하단 출입문
st.write("")
d1, d2, d3 = st.columns([2, 9, 2])
with d1: st.markdown("<div class='yellow-box door'>문</div>", unsafe_allow_html=True)
with d3: st.markdown("<div class='yellow-box door'>문</div>", unsafe_allow_html=True)
