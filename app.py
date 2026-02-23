import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="수의대 자리 티켓팅", layout="wide")

# [중앙 정렬 CSS] 버튼을 칸의 정중앙에 배치하고 와이드 비율 유지
st.markdown("""
    <style>
    /* 전체 여백 최적화 */
   
    [data-testid="stAppViewContainer"] { padding: 0.5rem 0.1rem !important; }
    [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 0px !important; }
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0px !important; padding: 0px !important; }

    /* [핵심] 버튼을 감싸는 컨테이너를 중앙 정렬 모드로 변경 */
    div.stButton {
        display: flex;
        justify-content: center; /* 가로 중앙 정렬 */
        align-items: center;     /* 세로 중앙 정렬 */
        width: 100%;
    }
    
    /* 버튼 디자인: 와이드 직사각형 비율 유지 */
    .stButton > button {
        width: 300% !important;    /* 중앙에 오는 느낌을 주려고 너비를 살짝 줄였습니다(92%) */
        height: 22px !important;  /* 진섭 님이 선택한 와이드한 높이 */
        padding: 0px !important;
        font-size: 8px !important;
        font-weight: 700 !important;
        line-height: 1 !important;
        white-space: nowrap !important;
        letter-spacing: -0.9px !important;
        border-radius: 1px !important;
        border: 1px solid #444 !important;
    }
    
    /* 예약 완료 초록색 버튼 */
    div.stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }

    /* 노란색 구조물 디자인 */
    .yellow-box { text-align: center; background-color: #fceea7; color: black; font-weight: bold; border: 1px solid #000; display: flex; align-items: center; justify-content: center; }
    .monitor { height: 25px; font-size: 14px; width: 85%; margin: 0 auto 10px auto; }
    .desk { height: 35px; font-size: 10px; width: 90px; margin-left: auto; line-height: 1.1; margin-bottom: 5px; }
    .door { height: 35px; font-size: 11px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 수의과대학 2학년 자리 배치")

# 2. 실시간 데이터 로드 (nan 박멸)
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    st.cache_data.clear()
    _df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)
    _df = _df.fillna("").replace("nan", "")
    _df['seat_no'] = _df['seat_no'].astype(str).str.strip()
    return _df

df = load_data()

# 3. 사이드바 및 이선좌 상태 관리
if 'occupied_error' not in st.session_state: st.session_state.occupied_error = False
user_name = st.sidebar.text_input("성함을 입력하세요", placeholder="예: 임진섭")
GAS_URL = "https://script.google.com/macros/s/AKfycbwIyemiDDz0BKptG5z5IWtvtn6aQNiXv0qTZRWWACntR_g3DOqZ7Ix6uXvpmzTuLJf9aQ/exec"

if st.session_state.occupied_error:
    st.error("🎟️ 이미 선택된 좌석입니다! (이선좌)")
    if st.button("알림 닫기 ✖️"):
        st.session_state.occupied_error = False
        st.rerun()

if st.sidebar.button("🔄 좌석 현황 새로고침"): st.rerun()

# 4. 강의실 레이아웃
st.markdown("<div class='yellow-box monitor'>모니터 (정면)</div>", unsafe_allow_html=True)
c_l, c_s, c_r = st.columns([6, 0.3, 6])
with c_r: st.markdown("<div class='yellow-box desk'>👨‍🏫<br>교탁</div>", unsafe_allow_html=True)
st.write("")

# 

# 5. 좌석 배치 로직
for r in range(6):
    cols = st.columns([1,1,1,1,1,1, 1.0, 1,1,1,1,1,1])
    for c in range(6):
        l_idx = str((r * 12) + c + 1)
        r_idx = str((r * 12) + c + 7)
        
        def draw_seat(column, idx, key_p):
            if int(idx) > 66: return
            with column:
                owner = df[df['seat_no'] == idx]['owner'].values[0] if not df[df['seat_no'] == idx].empty else ""
                if not owner:
                    if st.button(f"{idx}", key=f"{key_p}_{idx}"):
                        if not user_name: st.sidebar.error("이름!")
                        else:
                            st.session_state.occupied_error = False
                            res = requests.get(GAS_URL, params={"seat_no": idx, "owner": user_name})
                            if res.text == "Occupied": st.session_state.occupied_error = True
                            else: st.balloons()
                            st.rerun()
                else:
                    st.button(f"{owner}", key=f"{key_p}_{idx}", type="primary", disabled=(owner != user_name))

        draw_seat(cols[c], l_idx, "L")
        if r == 0:
            with cols[c+7]: st.button("❌", key=f"x_{c}", disabled=True)
        else:
            draw_seat(cols[c+7], r_idx, "R")

# 6. 하단 출입문
st.write("")
d1, d2, d3 = st.columns([2, 9, 2])
with d1: st.markdown("<div class='yellow-box door'>출입문</div>", unsafe_allow_html=True)
with d3: st.markdown("<div class='yellow-box door'>출입문</div>", unsafe_allow_html=True)
