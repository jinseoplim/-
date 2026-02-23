import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="수의대 자리 티켓팅", layout="wide")

# [디자인] 노란색 구조물 + 초록색 버튼 디자인 유지
st.markdown("""
    <style>
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0px !important; }
    .stButton > button { width: 100% !important; height: 50px !important; font-weight: bold; font-size: 14px !important; }
    div.stButton > button[kind="primary"] { background-color: #28a745 !important; color: white !important; border: 2px solid #1e7e34; }
    .yellow-box { text-align: center; background-color: #fceea7; color: black; font-weight: bold; border: 2px solid #000; display: flex; align-items: center; justify-content: center; }
    .monitor { height: 50px; font-size: 22px; width: 60%; margin: 0 auto 30px auto; }
    .desk { height: 40px; font-size: 16px; width: 120px; margin-left: auto; }
    .door { height: 60px; font-size: 18px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 수의과대학 2학년 강의실 자리 배치")

# 2. 구글 시트 연결 및 최신 데이터 로드
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

# [해결책] 시트 수동 수정 사항을 즉시 반영하기 위한 함수
def load_data():
    # 캐시를 완전히 비워서 항상 구글 서버에서 새 데이터를 가져오게 합니다.
    st.cache_data.clear()
    # ttl=0은 캐시 수명을 0초로 설정하는 것입니다.
    _df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)
    # 데이터 매칭 에러를 방지하기 위해 번호를 모두 '문자'로 바꿉니다.
    _df['seat_no'] = _df['seat_no'].astype(str).str.strip()
    return _df

df = load_data()

# 3. 사이드바 - 인증 및 관리
st.sidebar.header("📋 시스템 (2023-11883)")
user_name = st.sidebar.text_input("성함을 입력하세요", placeholder="예: 임진섭")
GAS_URL = "https://script.google.com/macros/s/AKfycbwIyemiDDz0BKptG5z5IWtvtn6aQNiXv0qTZRWWACntR_g3DOqZ7Ix6uXvpmzTuLJf9aQ/exec"

# 수동으로 시트를 고쳤을 때 누르는 긴급 버튼
if st.sidebar.button("🔄 시트 수정사항 강제 반영"):
    st.rerun()

# 내 자리 확인
my_seat_data = df[df['owner'] == user_name]
my_seat = my_seat_data['seat_no'].values[0] if not my_seat_data.empty else None

if my_seat:
    st.sidebar.success(f"✅ 현재 {my_seat}번 좌석 사용 중")
    if st.sidebar.button("❌ 예약 취소하기"):
        requests.get(GAS_URL, params={"owner": user_name})
        st.rerun()

# 4. 강의실 레이아웃 시각화 (모니터, 교탁)
st.markdown("<div class='yellow-box monitor'>모니터</div>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([6, 0.5, 6])
with c3: st.markdown("<div class='yellow-box desk'>교탁</div>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)

# 5. 좌석 배치 및 예약 로직
for r in range(6):
    cols = st.columns([1,1,1,1,1,1, 0.2, 1,1,1,1,1,1])
    for c in range(6):
        l_idx = str((r * 12) + c + 1)
        r_idx = str((r * 12) + c + 7)
        
        def draw_seat(column, idx):
            if int(idx) > 66: return
            with column:
                # 시트의 seat_no와 코드의 idx를 정확하게 비교합니다.
                owner_row = df[df['seat_no'] == idx]
                owner = owner_row['owner'].values[0] if not owner_row.empty else ""
                
                if pd.isna(owner) or owner == "":
                    if st.button(f"{idx}", key=f"s{idx}"):
                        if not user_name: st.sidebar.error("이름 입력!")
                        else:
                            with st.spinner('확인 중...'):
                                res = requests.get(GAS_URL, params={"seat_no": idx, "owner": user_name})
                                if res.text == "Occupied": st.error("이선좌!")
                                else: st.balloons()
                                st.rerun()
                else:
                    st.button(f"{owner[:2]}", key=f"s{idx}", type="primary", disabled=(owner != user_name))

        draw_seat(cols[c], l_idx)
        if r == 0:
            with cols[c+7]: st.button("❌", key=f"x{c}", disabled=True)
        else:
            draw_seat(cols[c+7], r_idx)

# 6. 하단 출입문
st.write("<br>", unsafe_allow_html=True)
d1, d2, d3 = st.columns([2, 8, 2])
with d1: st.markdown("<div class='yellow-box door'>출입문</div>", unsafe_allow_html=True)
with d3: st.markdown("<div class='yellow-box door'>출입문</div>", unsafe_allow_html=True)
