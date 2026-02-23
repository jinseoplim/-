import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="수의대 자리 티켓팅", layout="wide")

# [디자인] 이름 세 글자가 한 줄에 들어가도록 폰트 최적화
st.markdown("""
    <style>
    /* 모바일 세로 모드 가로 배열 강제 고정 */
    [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 1px !important; }
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0px !important; }
    
    /* 버튼: 이름 3자가 다 보이도록 폰트 크기 및 여백 극소화 */
    .stButton > button {
        width: 100% !important;
        height: 38px !important;
        padding: 0px !important;
        font-size: 8.5px !important; /* 이름 3자 맞춤형 크기 */
        line-height: 1 !important;
        letter-spacing: -0.5px !important; /* 자간 축소로 밀착 */
        white-space: nowrap !important; /* 줄바꿈 방지 */
    }
    
    /* 예약 완료 초록색 버튼 */
    div.stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none;
    }

    /* 노란색 구조물 디자인 유지 */
    .yellow-box { text-align: center; background-color: #fceea7; color: black; font-weight: bold; border: 1px solid #000; display: flex; align-items: center; justify-content: center; }
    .monitor { height: 30px; font-size: 14px; width: 70%; margin: 0 auto 15px auto; }
    .desk { height: 40px; font-size: 11px; width: 80px; margin-left: auto; line-height: 1.2; }
    .door { height: 45px; font-size: 12px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 수의대 2학년 자리 배치")

# 2. 구글 시트 데이터 로드
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    st.cache_data.clear()
    _df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)
    _df['seat_no'] = _df['seat_no'].astype(str).str.strip()
    return _df

df = get_data()

# 3. 사이드바 - 인증 및 관리
user_name = st.sidebar.text_input("성함 입력", placeholder="예: 임진섭")
GAS_URL = "여기에_앱스_스크립트_URL_붙여넣기"

if st.sidebar.button("🔄 좌석 현황 새로고침"):
    st.rerun()

# 예약 취소
my_seat_row = df[df['owner'] == user_name]
if not my_seat_row.empty:
    my_seat = my_seat_row['seat_no'].values[0]
    st.sidebar.success(f"✅ {my_seat}번 예약 중")
    if st.sidebar.button("❌ 예약 취소하기"):
        requests.get(GAS_URL, params={"owner": user_name})
        st.rerun()

# 4. 강의실 레이아웃 시각화 (모니터, 교탁)
st.markdown("<div class='yellow-box monitor'>모니터</div>", unsafe_allow_html=True)
c_l, c_s, c_r = st.columns([6, 0.2, 6])
with c_r: st.markdown("<div class='yellow-box desk'>👨‍🏫<br>교수님 교탁</div>", unsafe_allow_html=True)
st.write("")

# 5. 좌석 배치 및 예약 로직
for r in range(6):
    cols = st.columns([1,1,1,1,1,1, 0.2, 1,1,1,1,1,1])
    for c in range(6):
        l_idx = str((r * 12) + c + 1)
        r_idx = str((r * 12) + c + 7)
        
        def draw_seat(column, idx):
            if int(idx) > 66: return
            with column:
                owner_row = df[df['seat_no'] == idx]
                owner = owner_row['owner'].values[0] if not owner_row.empty else ""
                
                if not owner: # 빈자리
                    if st.button(f"{idx}", key=f"s{idx}"):
                        if not user_name: st.sidebar.error("이름!")
                        else:
                            requests.get(GAS_URL, params={"seat_no": idx, "owner": user_name})
                            st.rerun()
                else: # 예약 완료 (이름 3글자 전체 표시)
                    st.button(f"{owner}", key=f"s{idx}", type="primary", disabled=(owner != user_name))

        draw_seat(cols[c], l_idx)
        if r == 0:
            with cols[c+7]: st.button("❌", key=f"x{c}", disabled=True)
        else:
            draw_seat(cols[c+7], r_idx)

# 6. 하단 출입문
st.write("")
d1, d2, d3 = st.columns([2, 8, 2])
with d1: st.markdown("<div class='yellow-box door'>출입문</div>", unsafe_allow_html=True)
with d3: st.markdown("<div class='yellow-box door'>출입문</div>", unsafe_allow_html=True)
