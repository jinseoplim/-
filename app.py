import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="자리 배치 시스템", layout="wide")

# [디자인] 모든 여백을 0으로 깎아내서 좌석 너비를 극대화하는 CSS
st.markdown("""
    <style>
    /* 1. 전체 앱 컨테이너의 좌우 여백을 완전히 제거 */
    [data-testid="stAppViewContainer"] { padding: 0.5rem 0.05rem !important; }
    [data-testid="stMainViewContainer"] { padding: 0px !important; }

    /* 2. 컬럼 사이의 간격(Gap)을 완전히 제거 */
    [data-testid="stHorizontalBlock"] { 
        gap: 0px !important; 
        flex-wrap: nowrap !important;
    }
    
    /* 3. 각 컬럼 내부의 여백(Padding)을 0으로 설정하여 버튼이 꽉 차게 함 */
    [data-testid="column"] { 
        padding: 0px !important; 
        flex: 1 1 0% !important;
        min-width: 0px !important;
    }
    
    /* 4. 버튼: 가로를 100% 채우고 높이를 낮춰서 와이드 비율 확보 */
    .stButton > button {
        width: 200% !important; 
        height: 24px !important; /* 높이가 낮을수록 가로로 더 넓어 보입니다 */
        margin: 0px !important;
        padding: 0px !important;
        font-size: 9px !important; 
        font-weight: 700 !important;
        line-height: 1 !important;
        white-space: nowrap !important;
        letter-spacing: -1.0px !important;
        border-radius: 0px !important; /* 각지게 만들면 시각적으로 더 밀착되어 보임 */
        border: 0.5px solid #444 !important;
    }
    
    /* 예약 완료 초록색 버튼 */
    div.stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }

    /* 노란색 구조물 디자인 */
    .yellow-box { text-align: center; background-color: #fceea7; color: black; font-weight: bold; border: 1px solid #000; display: flex; align-items: center; justify-content: center; }
    .monitor { height: 30px; font-size: 14px; width: 80%; margin: 0 auto 10px auto; }
    .desk { height: 35px; font-size: 10px; width: 100px; margin-left: auto; line-height: 1.1; margin-bottom: 5px; }
    .door { height: 35px; font-size: 11px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 강의실 자리 배치 시스템")

# 2. 데이터 로드 (nan 방지 및 실시간 반영)
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    st.cache_data.clear()
    _df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)
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
c_l, c_s, c_r = st.columns([6, 0.2, 6]) # 중앙 복도 간격도 0.2로 최소화
with c_r: st.markdown("<div class='yellow-box desk'>👨‍🏫<br>교수님 교탁</div>", unsafe_allow_html=True)
st.write("")

# 5. 좌석 배치 (1~66번)
for r in range(6):
    # 중앙 복도(0.2)를 제외한 모든 간격을 CSS로 완전히 없앴습니다.
    cols = st.columns([1,1,1,1,1,1, 0.7, 1,1,1,1,1,1])
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
