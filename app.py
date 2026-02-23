import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="수의대 자리 티켓팅", layout="wide")

# [디자인] 모든 버튼의 규격을 '초록 네모'와 100% 일치시키는 CSS
st.markdown("""
    <style>
    /* 전체 여백 및 간격 제로화 */
    [data-testid="stAppViewContainer"] { padding: 0.5rem 0.05rem !important; }
    [data-testid="stHorizontalBlock"] { gap: 0px !important; flex-wrap: nowrap !important; }
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0px !important; padding: 0px 0.5px !important; }

    /* [핵심] 번호/이름 상관없이 모든 버튼의 크기를 강제로 고정 */
    .stButton > button {
        width: 100% !important;   /* 칸의 너비를 꽉 채움 */
        height: 24px !important;  /* 높이를 낮게 고정해서 '옆으로 넓은' 직사각형 유지 */
        
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
    }

    /* 예약 완료 버튼 (색상만 초록색으로 변경, 크기는 위와 동일) */
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

st.title("🏥 수의과대학 2학년 자리 배치")

# 2. 데이터 로드 (nan 박멸 및 실시간 반영)
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    st.cache_data.clear()
    _df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)
    _df = _df.fillna("").replace("nan", "") # 흉측한 nan 완전 제거
    _df['seat_no'] = _df['seat_no'].astype(str).str.strip()
    return _df

df = get_data()

# 3. 사이드바 관리
user_name = st.sidebar.text_input("성함 입력", placeholder="예: 이름")
GAS_URL = "https://script.google.com/macros/s/AKfycbwIyemiDDz0BKptG5z5IWtvtn6aQNiXv0qTZRWWACntR_g3DOqZ7Ix6uXvpmzTuLJf9aQ/exec"

if st.sidebar.button("🔄 좌석 현황 새로고침"): st.rerun()

# 4. 강의실 레이아웃
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
                
                # 빈자리든 예약석이든 .stButton > button 설정에 따라 동일한 규격으로 생성됨
                if not owner or owner == "":
                    if st.button(f"{idx}", key=f"{key_p}_{idx}"):
                        if not user_name: st.sidebar.error("이름!")
                        else:
                            res = requests.get(GAS_URL, params={"seat_no": idx, "owner": user_name})
                            if res.text == "Occupied": st.error("이선좌!")
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
with d1: st.markdown("<div class='yellow-box door'>문</div>", unsafe_allow_html=True)
with d3: st.markdown("<div class='yellow-box door'>문</div>", unsafe_allow_html=True)
