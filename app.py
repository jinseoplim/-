import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# 1. 페이지 설정 (가로 모드 고정)
st.set_page_config(page_title="수의대 자리 티켓팅", layout="wide")

# [디자인] 모든 간격을 제거하여 좌석 너비를 극대화하고 와이드 직사각형 구현
st.markdown("""
    <style>
    /* 전체 여백 및 헤더 제거 */
    [data-testid="stAppViewContainer"] { padding: 0.2rem 0.05rem !important; }
    [data-testid="stMainViewContainer"] { padding: 0px !important; }
    header { visibility: hidden; }

    /* 컬럼 사이의 기본 간격(Gap)을 완전히 제거하여 버튼 너비 확보 */
    [data-testid="stHorizontalBlock"] { 
        gap: 0px !important; 
        flex-wrap: nowrap !important;
    }
    
    /* 각 컬럼의 여백을 0으로 설정하여 버튼이 거의 맞닿게 함 */
    [data-testid="column"] { 
        flex: 1 1 0% !important;
        min-width: 0px !important;
        padding: 0px 0.2px !important; 
    }
    
    /* [핵심] 버튼 디자인: 가로 100% + 높이 22px로 와이드 직사각형 완성 */
    .stButton > button {
        width: 100% !important; 
        height: 22px !important; /* 높이를 낮춰야 옆으로 넓어 보입니다 */
        padding: 0px !important;
        font-size: 8.5px !important; /* 이름 3자가 딱 들어가는 크기 */
        font-weight: 700 !important;
        line-height: 1 !important;
        white-space: nowrap !important;
        letter-spacing: -1.0px !important;
        border-radius: 1px !important;
        border: 0.1px solid #444 !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    
    /* 예약 완료 초록색 버튼 */
    div.stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }

    /* 노란색 구조물 디자인 (모니터, 교탁, 출입문) */
    .yellow-box { text-align: center; background-color: #fceea7; color: black; font-weight: bold; border: 1px solid #000; display: flex; align-items: center; justify-content: center; }
    .monitor { height: 25px; font-size: 13px; width: 90%; margin: 0 auto 10px auto; }
    .desk { height: 35px; font-size: 10px; width: 100px; margin-left: auto; line-height: 1.1; margin-bottom: 5px; }
    .door { height: 35px; font-size: 11px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 수의과대학 2학년 자리 배치")

# 2. 데이터 로드 (실시간 반영 및 nan 박멸)
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    st.cache_data.clear() # 수동 수정 즉시 반영
    _df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)
    _df = _df.fillna("").replace("nan", "") # 흉측한 nan 글자 제거
    _df['seat_no'] = _df['seat_no'].astype(str).str.strip()
    _df['owner'] = _df['owner'].astype(str).str.strip()
    return _df

df = get_data()

# 3. 사이드바 및 상태 관리 (이선좌 알림용)
if 'occupied_error' not in st.session_state: st.session_state.occupied_error = False
user_name = st.sidebar.text_input("성함을 입력하세요", placeholder="예: 이름")
GAS_URL = "https://script.google.com/macros/s/AKfycbwIyemiDDz0BKptG5z5IWtvtn6aQNiXv0qTZRWWACntR_g3DOqZ7Ix6uXvpmzTuLJf9aQ/exec"

# 이선좌 알림창
if st.session_state.occupied_error:
    st.error("🎟️ 이미 선택된 좌석입니다! (이선좌)")
    if st.button("알림 닫기 ✖️"):
        st.session_state.occupied_error = False
        st.rerun()

if st.sidebar.button("🔄 좌석 현황 새로고침"): st.rerun()

# 내 좌석 취소
my_seat_row = df[df['owner'] == user_name]
if not my_seat_row.empty and user_name != "":
    my_seat = my_seat_row['seat_no'].values[0]
    st.sidebar.success(f"✅ {my_seat}번 예약 중")
    if st.sidebar.button("❌ 예약 취소하기"):
        requests.get(GAS_URL, params={"owner": user_name})
        st.rerun()

# 4. 강의실 레이아웃 (모니터 및 교탁)
st.markdown("<div class='yellow-box monitor'>모니터 (정면)</div>", unsafe_allow_html=True)

# 교탁 배치 (중앙 복도 간격 0.3으로 좁혀서 좌석폭 확보)
c_l, c_s, c_r = st.columns([6, 0.3, 6])
with c_r: st.markdown("<div class='yellow-box desk'>👨‍🏫<br>교수님 교탁</div>", unsafe_allow_html=True)
st.write("")

# 5. 좌석 배치 로직 (1~66번)
for r in range(6):
    # 중앙 복도(0.3) 외 모든 간격을 CSS로 제로화
    cols = st.columns([1,1,1,1,1,1, 0.3, 1,1,1,1,1,1])
    for c in range(6):
        l_idx = str((r * 12) + c + 1)
        r_idx = str((r * 12) + c + 7)
        
        def draw_seat(column, idx, key_p):
            if int(idx) > 66: return
            with column:
                owner = df[df['seat_no'] == idx]['owner'].values[0] if not df[df['seat_no'] == idx].empty else ""
                
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
                    # 예약 완료 (이름 전체 표시, 옆 칸 침범 없음)
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
