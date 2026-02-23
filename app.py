import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="수의대 자리 티켓팅", layout="wide")

# [디자인] 모든 버튼의 규격을 45px 높이로 고정하고 중앙 정렬
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { padding: 0.5rem 0.1rem !important; }
    [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 1px !important; }
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0px !important; padding: 0px !important; }

    /* 모든 버튼 규격 통일: 이름이 있든 없든 무조건 똑같은 직사각형 */
    .stButton > button {
        width: 150% !important;
        height: 40px !important; 
        min-height: 45px !important;
        max-height: 45px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0px !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        white-space: nowrap !important;
        border-radius: 4px !important;
        border: 1px solid #444 !important;
    }

    /* 예약된 초록색 칸 */
    div.stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }

    .yellow-box { text-align: center; background-color: #fceea7; color: black; font-weight: bold; border: 1px solid #000; display: flex; align-items: center; justify-content: center; }
    .monitor { height: 30px; font-size: 16px; width: 80%; margin: 0 auto 15px auto; }
    .desk { height: 45px; font-size: 12px; width: 110px; margin-left: auto; line-height: 1.2; margin-bottom: 10px; }
    .door { height: 40px; font-size: 12px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 수의과대학 2학년 자리 배치")

# 2. 데이터 로드 및 nan 박멸
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_clean_data():
    st.cache_data.clear()
    _df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)
    _df = _df.fillna("").replace("nan", "")
    _df['seat_no'] = _df['seat_no'].astype(str).str.strip()
    return _df

df = get_clean_data()

# 3. 사이드바 - 인증 및 예약 취소 (부활!)
user_name = st.sidebar.text_input("성함 입력", placeholder="예: 임진섭")
GAS_URL = "https://script.google.com/macros/s/AKfycbwIyemiDDz0BKptG5z5IWtvtn6aQNiXv0qTZRWWACntR_g3DOqZ7Ix6uXvpmzTuLJf9aQ/exec"

if st.sidebar.button("🔄 실시간 현황 새로고침"):
    st.rerun()

# [핵심] 예약 취소 로직
my_seat_row = df[df['owner'] == user_name]
if not my_seat_row.empty and user_name != "":
    my_seat = my_seat_row['seat_no'].values[0]
    st.sidebar.success(f"✅ {my_seat}번 사용 중")
    if st.sidebar.button("❌ 내 예약 취소하기"):
        with st.spinner('취소 중...'):
            # GAS에 owner 정보만 보내서 해당 사용자의 데이터를 지웁니다.
            requests.get(GAS_URL, params={"owner": user_name})
            st.rerun()

# 4. 강의실 레이아웃 시각화
st.markdown("<div class='yellow-box monitor'>모니터 (정면)</div>", unsafe_allow_html=True)
c_l, c_s, c_r = st.columns([6, 0.5, 6])
with c_r: st.markdown("<div class='yellow-box desk'>👨‍🏫<br>교수님 교탁</div>", unsafe_allow_html=True)
st.write("")

# 5. 좌석 배치 (도면 일치 로직)
for r in range(6):
    cols = st.columns([1,1,1,1,1,1, 1.0, 1,1,1,1,1,1])
    for c in range(6):
        if r == 0:
            l_idx = str(c + 1)
            r_idx = "X" # 1열 우측 ❌
        else:
            l_idx = str((r-1)*12 + 7 + c)
            r_idx = str((r-1)*12 + 13 + c)
        
        def draw_seat(column, idx, key_p):
            if idx == "X":
                with column: st.button("❌", key=f"x_{r}_{c}", disabled=True)
                return
            if int(idx) > 66: return
            
            with column:
                owner = df[df['seat_no'] == idx]['owner'].values[0] if not df[df['seat_no'] == idx].empty else ""
                if not owner or owner == "":
                    if st.button(f"{idx}", key=f"{key_p}_{idx}"):
                        if not user_name: st.sidebar.error("이름!")
                        else:
                            res = requests.get(GAS_URL, params={"seat_no": idx, "owner": user_name})
                            if res.text == "Occupied": st.error("🎟️ 이선좌!")
                            else: st.balloons()
                            st.rerun()
                else:
                    st.button(f"{owner}", key=f"{key_p}_{idx}", type="primary", disabled=(owner != user_name))

        draw_seat(cols[c], l_idx, "L")
        draw_seat(cols[c+7], r_idx, "R")

# 6. 하단 출입문
st.write("")
d1, d2, d3 = st.columns([2, 9, 2])
with d1: st.markdown("<div class='yellow-box door'>출입문</div>", unsafe_allow_html=True)
with d3: st.markdown("<div class='yellow-box door'>출입문</div>", unsafe_allow_html=True)
