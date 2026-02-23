import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="수의대 자리 티켓팅", layout="wide")

# [황금 비율 CSS] 좌석을 옆으로 널찍하게 만들고 침범을 방지하는 설정
st.markdown("""
    <style>
    /* 전체 여백을 줄여서 가로 공간 확보 */
    [data-testid="stAppViewContainer"] { padding: 0.5rem 0.1rem !important; }
    
    /* 12칸이 한 줄에 유지되도록 고정 및 간격 최소화 */
    [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 0px !important; }
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0px !important; padding: 0px 0.5px !important; }
    
    /* [핵심] 버튼을 '와이드 직사각형'으로 만드는 설정 */
    .stButton > button {
        width: 100% !important;   /* 옆 칸 침범 방지를 위해 100% 고정 */
        height: 22px !important;  /* 높이를 낮춰서 상대적으로 가로가 길어 보이게 함 */
        padding: 0px !important;
        font-size: 8px !important; /* 이름 3자가 딱 맞게 들어가는 크기 */
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
    .monitor { height: 25px; font-size: 14px; width: 85%; margin: 0 auto 10px auto; }
    .desk { height: 35px; font-size: 10px; width: 90px; margin-left: auto; line-height: 1.1; margin-bottom: 5px; }
    .door { height: 35px; font-size: 11px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 수의대 2학년 자리 배치")

# 2. 실시간 데이터 로드 (nan 박멸 버전)
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def load_clean_data():
    st.cache_data.clear() # 수동 수정 즉시 반영
    _df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)
    # nan 글자가 뜨는 것을 방지하기 위해 빈칸 처리
    _df = _df.fillna("").replace("nan", "")
    _df['seat_no'] = _df['seat_no'].astype(str).str.strip()
    return _df

df = load_clean_data()

# 3. 사이드바 및 이선좌 관리
if 'occupied_error' not in st.session_state: st.session_state.occupied_error = False
user_name = st.sidebar.text_input("성함을 입력하세요", placeholder="예: 임진섭")
GAS_URL = "https://script.google.com/macros/s/AKfycbwIyemiDDz0BKptG5z5IWtvtn6aQNiXv0qTZRWWACntR_g3DOqZ7Ix6uXvpmzTuLJf9aQ/exec"

# 이선좌 알림 (닫기 버튼 누를 때까지 유지)
if st.session_state.occupied_error:
    st.error("🎟️ 이미 선택된 좌석입니다! (이선좌)")
    if st.button("알림 닫기 ✖️"):
        st.session_state.occupied_error = False
        st.rerun()

if st.sidebar.button("🔄 좌석 현황 새로고침"): st.rerun()

# 내 예약 취소 기능
my_seat_row = df[df['owner'] == user_name]
if not my_seat_row.empty and user_name != "":
    my_seat = my_seat_row['seat_no'].values[0]
    st.sidebar.success(f"✅ {my_seat}번 사용 중")
    if st.sidebar.button("❌ 예약 취소하기"):
        requests.get(GAS_URL, params={"owner": user_name})
        st.rerun()

# 4. 강의실 레이아웃
st.markdown("<div class='yellow-box monitor'>모니터 (정면)</div>", unsafe_allow_html=True)
c_l, c_s, c_r = st.columns([6, 0.3, 6]) # 통로를 0.3으로 좁혀서 좌석폭 추가 확보
with c_r: st.markdown("<div class='yellow-box desk'>👨‍🏫<br>교탁</div>", unsafe_allow_html=True)
st.write("")

# 5. 좌석 배치 (1~66번)
for r in range(6):
    cols = st.columns([1,1,1,1,1,1, 0.3, 1,1,1,1,1,1]) # 0.3의 좁은 통로
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
                    # 예약 완료 (이름 전체 표시, 초록색)
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
