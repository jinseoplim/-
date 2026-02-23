import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests
import time

# 1. 페이지 설정
st.set_page_config(page_title="자리 배치 티켓팅!!!", layout="wide")

# CSS 디자인 (모니터, 교탁, 출입문 위치 완벽 재현)
st.markdown("""
    <style>
    .monitor-box { text-align: center; background-color: #fceea7; padding: 10px; color: black; font-weight: bold; font-size: 22px; border: 2px solid #000; width: 50%; margin: 0 auto 20px auto; }
    .desk-box { text-align: center; background-color: #fceea7; padding: 8px; color: black; font-weight: bold; border: 2px solid #000; width: 150px; margin-left: auto; }
    .door-box { text-align: center; background-color: #fceea7; padding: 15px; color: black; font-weight: bold; border: 2px solid #000; width: 100px; }
    .stButton>button { width: 100%; height: 55px; font-weight: bold; font-size: 17px; }
    </style>
    """, unsafe_allow_html=True)

st.title("즐거운 자리 배치~~")

# 2. 구글 시트 데이터 불러오기 (초고속 로딩 설정)
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5) # 5초마다 데이터 갱신 (50명 동시 접속 대비 최적화)
def get_data():
    return conn.read(spreadsheet=url, usecols=[0, 1])

df = get_data()

# 3. 사이드바 - 본인 인증
st.sidebar.header("📋 로그인")
user_name = st.sidebar.text_input("이름을 입력하세요", placeholder="예: 임진섭")
# [주의] 이 주소는 아까 '앱스 스크립트' 배포해서 받은 URL을 넣으셔야 합니다!
GAS_URL = "https://script.google.com/macros/s/AKfycbwROH8eMtG2zg3420yofFYuZ0M0uQ7vOckzkCNLwKtq7yEhsZxPpVLYOWuONKs4d0WptQ/exec"

# 내 자리 확인 및 취소 기능
my_seat_data = df[df['owner'] == user_name]
my_seat = my_seat_data['seat_no'].values[0] if not my_seat_data.empty else None

if my_seat:
    st.sidebar.success(f"✅ {my_seat}번 좌석 배정됨")
    if st.sidebar.button("❌ 배정 취소하기"):
        requests.get(GAS_URL, params={"owner": user_name})
        st.cache_data.clear()
        st.rerun()

# 4. 강의실 레이아웃 시각화
st.markdown("<div class='monitor-box'>모니터</div>", unsafe_allow_html=True)
col_l, col_s, col_r = st.columns([6, 0.5, 6])
with col_r: st.markdown("<div class='desk-box'>교탁</div>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)

# 5. 좌석 배치 로직 (1~6행)
for r in range(6):
    row_cols = st.columns([1,1,1,1,1,1, 0.5, 1,1,1,1,1,1])
    for c in range(6):
        l_idx = (r * 12) + c + 1
        r_idx = (r * 12) + c + 7
        
        # 좌석 버튼 생성 함수
        def draw_seat(col, idx):
            with col:
                owner = df[df['seat_no'] == idx]['owner'].values[0] if not df[df['seat_no'] == idx].empty else ""
                
                if pd.isna(owner) or owner == "":
                    # 빈자리 클릭 시 예약 진행
                    if st.button(f"{idx}", key=f"s_{idx}"):
                        if not user_name: st.sidebar.error("⚠️ 이름을 입력하세요!")
                        else:
                            with st.spinner('좌석 배정 중...'):
                                res = requests.get(GAS_URL, params={"seat_no": idx, "owner": user_name})
                                if res.text == "Occupied":
                                    st.error("이미 선택된 좌석입니다. 이선좌~~~")
                                    time.sleep(1)
                                else:
                                    st.cache_data.clear()
                                    st.balloons()
                                st.rerun()
                elif owner == user_name:
                    # 내 자리는 파란색 강조
                    st.button(f"{owner}", key=f"s_{idx}", type="primary")
                else:
                    # 남의 자리는 비활성화
                    st.button(f"{owner}", key=f"s_{idx}", disabled=True)

        draw_seat(row_cols[c], l_idx)
        if r == 0:
            with row_cols[c+7]: st.button("❌", key=f"x_{c}", disabled=True)
        else:
            draw_seat(row_cols[c+7], r_idx)

# 하단 출입문 표시
st.write("<br>", unsafe_allow_html=True)
d1, d2, d3 = st.columns([1, 10, 1])
with d1: st.markdown("<div class='door-box'>출입문</div>", unsafe_allow_html=True)
with d3: st.markdown("<div class='door-box'>출입문</div>", unsafe_allow_html=True)
