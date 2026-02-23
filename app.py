import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="수의대 자리 티켓팅", layout="wide")

# [핵심] 모든 버튼의 가로/세로를 강제로 고정하여 규격을 통일하는 CSS
st.markdown("""
    <style>
    /* 전체 여백 제거 */
    [data-testid="stAppViewContainer"] { padding: 0.5rem 0.1rem !important; }
    [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 2px !important; }
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0px !important; padding: 0px !important; }

    /* [진짜 핵심] 이름 유무와 상관없이 모든 버튼의 크기를 똑같은 직사각형으로 고정 */
    .stButton > button {
        width: 100% !important;   /* 칸 너비를 꽉 채움 */
        
        /* 높이를 45px로 고정 (사진 속 초록 네모와 가장 유사한 널찍한 크기) */
        height: 45px !important;  
        min-height: 45px !important;
        max-height: 45px !important;
        
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        
        padding: 0px !important;
        font-size: 11px !important; 
        font-weight: 700 !important;
        white-space: nowrap !important;
        letter-spacing: -0.5px !important;
        
        border-radius: 4px !important;
        border: 1px solid #444 !important;
        
        /* 내용이 길어도 박스 크기가 절대 변하지 않도록 제한 */
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    /* 예약 완료 버튼 (색상만 초록색으로 변경, 크기는 위에서 고정된 45px 유지) */
    div.stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }

    /* 노란색 구조물 디자인 */
    .yellow-box { text-align: center; background-color: #fceea7; color: black; font-weight: bold; border: 1px solid #000; display: flex; align-items: center; justify-content: center; }
    .monitor { height: 30px; font-size: 15px; width: 80%; margin: 0 auto 15px auto; }
    .desk { height: 45px; font-size: 12px; width: 110px; margin-left: auto; line-height: 1.2; margin-bottom: 10px; }
    .door { height: 40px; font-size: 12px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 수의과대학 2학년 자리 배치")

# 2. 데이터 로드 (nan 박멸 및 실시간 반영)
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_clean_data():
    st.cache_data.clear()
    _df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)
    # 사진에서 보이던 nan 문제를 확실히 지웁니다
    _df = _df.fillna("").replace("nan", "")
    _df['seat_no'] = _df['seat_no'].astype(str).str.strip()
    return _df

df = get_clean_data()

# 3. 사이드바 관리
user_name = st.sidebar.text_input("성함 입력", placeholder="예: 임진섭")
GAS_URL = "https://script.google.com/macros/s/AKfycbwIyemiDDz0BKptG5z5IWtvtn6aQNiXv0qTZRWWACntR_g3DOqZ7Ix6uXvpmzTuLJf9aQ/exec"

if st.sidebar.button("🔄 실시간 현황 새로고침"): st.rerun()

# 4. 강의실 레이아웃
st.markdown("<div class='yellow-box monitor'>모니터 (정면)</div>", unsafe_allow_html=True)
c_l, c_s, c_r = st.columns([6, 0.5, 6])
with c_r: st.markdown("<div class='yellow-box desk'>👨‍🏫<br>교탁</div>", unsafe_allow_html=True)
st.write("")

# 5. 좌석 배치 (1~66번)
for r in range(6):
    cols = st.columns([1,1,1,1,1,1, 0.5, 1,1,1,1,1,1])
    for c in range(6):
        l_idx = str((r * 12) + c + 1)
        r_idx = str((r * 12) + c + 7)
        
        def draw_seat(column, idx, key_p):
            if int(idx) > 66: return
            with column:
                owner = df[df['seat_no'] == idx]['owner'].values[0] if not df[df['seat_no'] == idx].empty else ""
                
                # 빈자리든 예약석이든 CSS의 45px 높이 설정을 똑같이 따릅니다.
                if not owner or owner == "":
                    if st.button(f"{idx}", key=f"{key_p}_{idx}"):
                        if not user_name: st.sidebar.error("이름!")
                        else:
                            res = requests.get(GAS_URL, params={"seat_no": idx, "owner": user_name})
                            if res.text == "Occupied": st.error("이선좌!")
                            else: st.balloons()
                            st.rerun()
                else:
                    # 예약 완료 (모든 칸 사이즈가 초록 네모 규격으로 고정됨)
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
