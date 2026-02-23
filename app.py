import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="수의대 자리 티켓팅", layout="wide")

# [디자인] 모든 여백을 제거하여 좌석 가로폭을 극한으로 확보하는 CSS
st.markdown("""
    <style>
    /* 1. 전체 앱 컨테이너 및 메인 여백 0화 */
    [data-testid="stAppViewContainer"] { padding: 0.2rem 0.05rem !important; }
    [data-testid="stMainViewContainer"] { padding: 0px !important; }
    [data-testid="stHeader"] { display: none; } /* 상단 헤더 숨겨서 공간 확보 */

    /* 2. 가로 블록(Row) 간격 및 컬럼 여백 완전히 제거 */
    [data-testid="stHorizontalBlock"] { 
        flex-wrap: nowrap !important; 
        gap: 0px !important; 
    }
    [data-testid="column"] { 
        flex: 1 1 0% !important; 
        min-width: 0px !important; 
        padding: 0px 0.2px !important; /* 좌우 간격을 0.2px로 극소화 */
    }
    
    /* 3. 좌석 버튼: 높이를 낮게(28px) 설정하여 가로로 긴 직사각형 비율 강제 */
    .stButton > button {
        width: 10% !important;
        height: 20px !important; 
        padding: 0px !important;
        font-size: 9px !important; 
        font-weight: 700 !important;
        line-height: 1 !important;
        white-space: nowrap !important;
        letter-spacing: -1.0px !important; /* 자간 축소로 이름 3자 수용 */
        border-radius: 1px !important;
        border: 0.1px solid #444 !important;
    }
    
    /* 예약 완료 버튼 (초록색) */
    div.stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }

    /* 노란색 강의실 구조물 (크기 최적화) */
    .yellow-box { text-align: center; background-color: #fceea7; color: black; font-weight: bold; border: 1px solid #000; display: flex; align-items: center; justify-content: center; }
    .monitor { height: 25px; font-size: 13px; width: 95%; margin: 0 auto 10px auto; }
    .desk { height: 35px; font-size: 10px; width: 90px; margin-left: auto; line-height: 1.1; margin-bottom: 5px; }
    .door { height: 35px; font-size: 11px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 수의대 2학년 자리 배치")

# 2. 데이터 로드 (실시간 반영 및 nan 방지)
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    st.cache_data.clear() # 수동 수정 즉시 반영
    _df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)
    _df = _df.fillna("").replace("nan", "") # nan 박멸
    _df['seat_no'] = _df['seat_no'].astype(str).str.strip()
    _df['owner'] = _df['owner'].astype(str).str.strip()
    return _df

df = get_data()

# 3. 사이드바 및 인증
if 'occupied_error' not in st.session_state: st.session_state.occupied_error = False
user_name = st.sidebar.text_input("성함 입력", placeholder="예: 임진섭")
# 진섭 님이 주신 최종 GAS URL 적용
GAS_URL = "https://script.google.com/macros/s/AKfycbwIyemiDDz0BKptG5z5IWtvtn6aQNiXv0qTZRWWACntR_g3DOqZ7Ix6uXvpmzTuLJf9aQ/exec"

# 이선좌 알림창
if st.session_state.occupied_error:
    st.error("🎟️ 이미 선택된 좌석입니다! (이선좌)")
    if st.button("알림 닫기 ✖️"):
        st.session_state.occupied_error = False
        st.rerun()

if st.sidebar.button("🔄 실시간 현황 새로고침"): st.rerun()

# 내 좌석 상태 확인
my_seat_row = df[df['owner'] == user_name]
if not my_seat_row.empty and user_name != "":
    my_seat = my_seat_row['seat_no'].values[0]
    st.sidebar.success(f"✅ {my_seat}번 사용 중")
    if st.sidebar.button("❌ 예약 취소하기"):
        requests.get(GAS_URL, params={"owner": user_name})
        st.rerun()

# 4. 레이아웃 시각화 (모니터 및 교탁)
st.markdown("<div class='yellow-box monitor'>모니터 (정면)</div>", unsafe_allow_html=True)
c_l, c_s, c_r = st.columns([6, 0.2, 6]) # 통로 간격을 0.2로 최소화하여 좌석폭 확보
with c_r: st.markdown("<div class='yellow-box desk'>👨‍🏫<br>교탁</div>", unsafe_allow_html=True)
st.write("")

# 5. 좌석 배치 (1~66번)
for r in range(6):
    # 중앙 통로(0.2) 외 모든 간격을 제로화하여 버튼 가로폭을 극대화
    cols = st.columns([1,1,1,1,1,1, 1.0, 1,1,1,1,1,1])
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
                    # 예약 완료 (이름 3글자 전체 표시)
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
