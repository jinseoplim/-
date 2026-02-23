import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="수의대 자리 티켓팅", layout="wide")

# [디자인] 간격을 제로로 만들어서 버튼 너비를 극대화하는 CSS
st.markdown("""
    <style>
    /* 1. 컬럼 사이의 기본 간격(Gap)을 0으로 강제 고정 */
    [data-testid="stHorizontalBlock"] { 
        gap: 0px !important; 
        flex-wrap: nowrap !important;
    }
    
    /* 2. 각 좌석 칸(Column)의 좌우 여백(Padding)을 완전히 제거 */
    /* 이래야 버튼이 옆 칸이랑 거의 맞닿으면서 가로로 넓어집니다 */
    [data-testid="column"] { 
        padding-left: 0.5px !important; 
        padding-right: 0.5px !important;
        flex: 1 1 0% !important;
        min-width: 0px !important;
    }
    
    /* 3. 버튼 디자인: 위아래 높이는 낮추고 가로는 100% 채우기 */
    .stButton > button {
        width: 100% !important; 
        height: 25px !important; /* 높이를 낮게 잡아야 '가로로 긴 직사각형'이 됩니다 */
        padding: 0px !important;
        font-size: 9px !important; 
        font-weight: 700 !important;
        line-height: 1 !important;
        white-space: nowrap !important;
        letter-spacing: -1.0px !important;
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
    .monitor { height: 30px; font-size: 15px; width: 80%; margin: 0 auto 10px auto; }
    .desk { height: 40px; font-size: 11px; width: 100px; margin-left: auto; line-height: 1.1; margin-bottom: 5px; }
    .door { height: 40px; font-size: 12px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 수의대 2학년 자리 배치")

# 2. 데이터 로드 및 nan 박멸
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    st.cache_data.clear()
    _df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)
    _df = _df.fillna("").replace("nan", "") # nan 문제 해결
    _df['seat_no'] = _df['seat_no'].astype(str).str.strip()
    return _df

df = get_data()

# 3. 사이드바 및 상태 관리
if 'occupied_error' not in st.session_state: st.session_state.occupied_error = False
user_name = st.sidebar.text_input("성함 입력", placeholder="예: 임진섭")
GAS_URL = "https://script.google.com/macros/s/AKfycbwIyemiDDz0BKptG5z5IWtvtn6aQNiXv0qTZRWWACntR_g3DOqZ7Ix6uXvpmzTuLJf9aQ/exec"

if st.session_state.occupied_error:
    st.error("🎟️ 이미 선택된 좌석입니다! (이선좌)")
    if st.button("알림 닫기 ✖️"):
        st.session_state.occupied_error = False
        st.rerun()

# 4. 레이아웃 시각화
st.markdown("<div class='yellow-box monitor'>모니터</div>", unsafe_allow_html=True)

# 교탁 부분 (복도 간격을 0.2로 줄여서 좌석 넓이로 환원)
c_l, c_s, c_r = st.columns([6, 0.2, 6])
with c_r: st.markdown("<div class='yellow-box desk'>👨‍🏫<br>교수님 교탁</div>", unsafe_allow_html=True)
st.write("")

# 5. 좌석 배치 (1~66번)
for r in range(6):
    # 중앙 통로(0.2)를 제외한 모든 간격을 극소화했습니다.
    cols = st.columns([1,1,1,1,1,1, 0.2, 1,1,1,1,1,1])
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
                            res = requests.get(GAS_URL, params={"seat_no": idx, "owner": user_name})
                            if res.text == "Occupied": st.session_state.occupied_error = True
                            else: st.balloons()
                            st.rerun()
                else:
                    # 예약 완료 (성함 전체 표시)
                    st.button(f"{owner}", key=f"{key_p}_{idx}", type="primary", disabled=(owner != user_name))

        draw_seat(cols[c], l_idx, "L")
        if r == 0:
            with cols[c+7]: st.button("❌", key=f"x_{c}", disabled=True)
        else:
            draw_seat(cols[c+7], r_idx, "R")
