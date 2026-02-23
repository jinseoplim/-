import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="수의대 자리 티켓팅", layout="wide")

# [디자인] 폰 세로 모드 고정 + 와이드 버튼 + 넓은 복도 디자인
st.markdown("""
    <style>
    /* 1. 폰 세로 모드에서도 좌석이 아래로 쌓이지 않게 강제 고정 (핵심) */
    [data-testid="stHorizontalBlock"] { 
        flex-wrap: nowrap !important; 
        gap: 1px !important; 
    }
    [data-testid="column"] { 
        flex: 1 1 0% !important; 
        min-width: 0px !important; 
    }
    
    /* 2. 와이드 버튼: 가로가 세로보다 긴 직사각형 형태로 최적화 */
    .stButton > button {
        width: 100% !important;
        height: 28px !important; /* 높이를 슬림하게 줄여서 좌우로 넓어 보이게 함 */
        padding: 0px !important;
        font-size: 10px !important; /* 이름이 한 줄에 쏙 들어가도록 조절 */
        font-weight: 700 !important;
        line-height: 1 !important;
        white-space: nowrap !important;
        letter-spacing: -0.8px !important; /* 자간 축소로 밀착 */
        border-radius: 2px !important;
        border: 1px solid #444 !important;
    }
    
    /* 예약 완료 초록색 버튼 */
    div.stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }

    /* 노란색 강의실 구조물 */
    .yellow-box { 
        text-align: center; background-color: #fceea7; color: black; font-weight: bold; 
        border: 1px solid #000; display: flex; align-items: center; justify-content: center; 
    }
    .monitor { height: 35px; font-size: 16px; width: 80%; margin: 0 auto 15px auto; }
    .desk { height: 40px; font-size: 11px; width: 100px; margin-left: auto; line-height: 1.2; margin-bottom: 10px; }
    .door { height: 40px; font-size: 12px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 수의과대학 2학년 자리 배치")

# 2. 구글 시트 데이터 로드 (수동 수정 즉시 반영)
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    st.cache_data.clear() # 수동 시트 수정 반영을 위해 매번 캐시 삭제
    _df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)
    _df = _df.fillna("") # 'nan' 표시 방지
    _df['seat_no'] = _df['seat_no'].astype(str).str.strip()
    _df['owner'] = _df['owner'].astype(str).str.strip()
    return _df

df = get_data()

# 3. 사이드바 - 인증 및 관리
user_name = st.sidebar.text_input("성함을 입력하세요", placeholder="예: 임진섭")
GAS_URL = "https://script.google.com/macros/s/AKfycbwIyemiDDz0BKptG5z5IWtvtn6aQNiXv0qTZRWWACntR_g3DOqZ7Ix6uXvpmzTuLJf9aQ/exec"

if st.sidebar.button("🔄 실시간 현황 새로고침"):
    st.rerun()

# 내 예약 상태 확인 및 취소
my_seat_row = df[df['owner'] == user_name]
if not my_seat_row.empty and user_name != "":
    my_seat = my_seat_row['seat_no'].values[0]
    st.sidebar.success(f"✅ {my_seat}번 예약 중")
    if st.sidebar.button("❌ 예약 취소하기"):
        requests.get(GAS_URL, params={"owner": user_name})
        st.rerun()

# 4. 강의실 레이아웃 시각화 (모니터 및 교탁)
st.markdown("<div class='yellow-box monitor'>모니터</div>", unsafe_allow_html=True)

# 교탁 배치 (중앙 복도 간격 1.5로 시원하게 넓힘)
c_l, c_s, c_r = st.columns([6, 1.5, 6])
with c_r: st.markdown("<div class='yellow-box desk'>👨‍🏫<br>교수님 교탁</div>", unsafe_allow_html=True)
st.write("")

# 5. 좌석 배치 로직 (1~66번)
for r in range(6):
    # 중앙 복도(1.5)를 통해 좌우 블록 간격을 시원하게 넓혔습니다.
    cols = st.columns([1,1,1,1,1,1, 1.5, 1,1,1,1,1,1])
    for c in range(6):
        l_idx = str((r * 12) + c + 1)
        r_idx = str((r * 12) + c + 7)
        
        def draw_seat(column, idx, key_p):
            if int(idx) > 66: return
            with column:
                owner_row = df[df['seat_no'] == idx]
                owner = owner_row['owner'].values[0] if not owner_row.empty else ""
                
                if not owner or owner.lower() == "nan": 
                    if st.button(f"{idx}", key=f"{key_p}_{idx}"):
                        if not user_name: st.sidebar.error("이름을 입력하세요!")
                        else:
                            with st.spinner('확보 중...'):
                                res = requests.get(GAS_URL, params={"seat_no": idx, "owner": user_name})
                                # [이선좌 로직] Occupied 응답 시 에러 메시지 출력
                                if res.text == "Occupied": 
                                    st.error("🎟️ 이미 선택된 좌석입니다! (이선좌)")
                                else: 
                                    st.balloons()
                                    st.rerun()
                else: 
                    # 예약 완료 (이름 전체 표시)
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
