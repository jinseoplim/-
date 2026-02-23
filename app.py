import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="수의대 자리 티켓팅", layout="wide")

# [디자인] 버튼 높이와 글자 크기를 확실하게 키운 CSS
st.markdown("""
    <style>
    /* 가로 배열 유지 및 복도 간격 고정 */
    [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 2px !important; }
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0px !important; }
    
    /* [수정] 버튼: 높이를 65px로, 글자 크기를 12px로 대폭 키웠습니다! */
    .stButton > button {
        width: 100% !important;
        height: 65px !important; /* 이전 48px에서 더 확대 */
        padding: 0px !important;
        font-size: 12px !important; /* 글자 크기 확대 */
        font-weight: 800 !important; /* 글자 굵게 */
        line-height: 1 !important;
        white-space: nowrap !important;
        border-radius: 6px !important; /* 모서리 살짝 둥글게 */
    }
    
    /* 예약 완료 버튼 (초록색) */
    div.stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: 2px solid #1e7e34;
    }

    /* 노란색 구조물 디자인 */
    .yellow-box { text-align: center; background-color: #fceea7; color: black; font-weight: bold; border: 1px solid #000; display: flex; align-items: center; justify-content: center; }
    .monitor { height: 40px; font-size: 18px; width: 80%; margin: 0 auto 20px auto; }
    .desk { height: 60px; font-size: 14px; width: 150px; margin-left: auto; line-height: 1.2; margin-bottom: 20px; }
    .door { height: 60px; font-size: 14px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 수의대 2학년 자리 배치")

# 2. 구글 시트 연결
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    st.cache_data.clear()
    _df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)
    _df = _df.fillna("") 
    _df['seat_no'] = _df['seat_no'].astype(str).str.strip()
    _df['owner'] = _df['owner'].astype(str).str.strip()
    return _df

df = get_data()

# 3. 사이드바 - 본인 인증
user_name = st.sidebar.text_input("성함 입력", placeholder="예: 임진섭")
GAS_URL = "https://script.google.com/macros/s/AKfycbwIyemiDDz0BKptG5z5IWtvtn6aQNiXv0qTZRWWACntR_g3DOqZ7Ix6uXvpmzTuLJf9aQ/exec"

if st.sidebar.button("🔄 좌석 현황 새로고침"):
    st.rerun()

# 내 자리 확인
my_seat_row = df[df['owner'] == user_name]
if not my_seat_row.empty and user_name != "":
    my_seat = my_seat_row['seat_no'].values[0]
    st.sidebar.success(f"✅ {my_seat}번 예약 중")
    if st.sidebar.button("❌ 예약 취소하기"):
        requests.get(GAS_URL, params={"owner": user_name})
        st.rerun()

# 4. 강의실 레이아웃 시각화
st.markdown("<div class='yellow-box monitor'>모니터</div>", unsafe_allow_html=True)

# 교탁 (복도 간격 1.0 유지)
c_l, c_s, c_r = st.columns([6, 1.0, 6])
with c_r: st.markdown("<div class='yellow-box desk'>👨‍🏫<br>교수님 교탁</div>", unsafe_allow_html=True)
st.write("")

# 5. 좌석 배치 (1~66번)
for r in range(6):
    # 중앙 복도 간격 1.0으로 시원하게 유지
    cols = st.columns([1,1,1,1,1,1, 1.0, 1,1,1,1,1,1])
    for c in range(6):
        l_idx = str((r * 12) + c + 1)
        r_idx = str((r * 12) + c + 7)
        
        def draw_seat(column, idx):
            if int(idx) > 66: return
            with column:
                owner_row = df[df['seat_no'] == idx]
                owner = owner_row['owner'].values[0] if not owner_row.empty else ""
                
                if not owner or owner.lower() == "nan": 
                    if st.button(f"{idx}", key=f"s{idx}"):
                        if not user_name: st.sidebar.error("이름!")
                        else:
                            requests.get(GAS_URL, params={"seat_no": idx, "owner": user_name})
                            st.rerun()
                else: # 예약 완료 (이름 전체 표시)
                    st.button(f"{owner}", key=f"s{idx}", type="primary", disabled=(owner != user_name))

        draw_seat(cols[c], l_idx)
        if r == 0:
            with cols[c+7]: st.button("❌", key=f"x{c}", disabled=True)
        else:
            draw_seat(cols[c+7], r_idx)

# 6. 하단 출입문
st.write("")
d1, d2, d3 = st.columns([2, 9, 2])
with d1: st.markdown("<div class='yellow-box door'>출입문</div>", unsafe_allow_html=True)
with d3: st.markdown("<div class='yellow-box door'>출입문</div>", unsafe_allow_html=True)
