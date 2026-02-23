import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests  # 1. 배달원(requests)을 불러옵니다.

# 페이지 설정
st.set_page_config(page_title="수의대 자리 티켓팅", layout="wide")

# (기존 디자인 스타일 설정)
st.markdown("""
    <style>
    .monitor-box { text-align: center; background-color: #fceea7; padding: 10px; color: black; font-weight: bold; border: 2px solid #000; width: 50%; margin: 0 auto 30px auto; }
    .desk-box { text-align: center; background-color: #fceea7; padding: 8px; color: black; font-weight: bold; border: 2px solid #000; width: 150px; margin-left: auto; }
    .door-box { text-align: center; background-color: #fceea7; padding: 15px; color: black; font-weight: bold; border: 2px solid #000; width: 100px; }
    .stButton>button { width: 100%; height: 60px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 수의과대학 2학년 강의실 자리 배치 시스템")

# 2. 구글 시트 연결 (읽기 전용으로 사용)
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)

# 3. 사이드바 이름 입력
st.sidebar.header("📋 본인 인증")
user_name = st.sidebar.text_input("성함을 입력하세요", placeholder="예: 임진섭")

# 4. 아까 복사한 '웹 앱 URL'을 여기에 입력하세요 (중요!)
# "https://script.google.com/macros/s/..." 처럼 생긴 주소입니다.
GAS_URL = "여기에_아까_복사한_웹_앱_URL을_붙여넣으세요"

# (모니터, 교탁 배치 로직)
st.markdown("<div class='monitor-box'>모니터</div>", unsafe_allow_html=True)
col_l, col_s, col_r = st.columns([6, 0.5, 6])
with col_r: st.markdown("<div class='desk-box'>교탁</div>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)

# 5. 좌석 배치 및 예약 로직
for r in range(6):
    row_cols = st.columns([1,1,1,1,1,1, 0.5, 1,1,1,1,1,1])
    for c in range(6):
        # 왼쪽 블록 번호 계산
        l_idx = (r * 6) + c + 1
        with row_cols[c]:
            owner = df[df['seat_no'] == l_idx]['owner'].values[0] if not df[df['seat_no'] == l_idx].empty else ""
            if pd.isna(owner) or owner == "":
                if st.button(f"{l_idx}", key=f"L_{l_idx}"):
                    if not user_name: st.sidebar.error("⚠️ 이름을 입력하세요!")
                    else:
                        # 6. 배달원(GAS)에게 데이터 전달!
                        response = requests.get(GAS_URL, params={"seat_no": l_idx, "owner": user_name})
                        if response.text == "Success":
                            st.balloons()
                            st.rerun()
            else:
                st.button(f"{owner}", key=f"L_{l_idx}", disabled=True, type="primary")

        # 오른쪽 블록 번호 계산
        with row_cols[c+7]:
            if r == 0: st.button("❌", key=f"x_{c}", disabled=True)
            else:
                r_idx = (r * 6) + c + 7
                owner = df[df['seat_no'] == r_idx]['owner'].values[0] if not df[df['seat_no'] == r_idx].empty else ""
                if pd.isna(owner) or owner == "":
                    if st.button(f"{r_idx}", key=f"R_{r_idx}"):
                        if not user_name: st.sidebar.error("⚠️ 이름을 입력하세요!")
                        else:
                            response = requests.get(GAS_URL, params={"seat_no": r_idx, "owner": user_name})
                            if response.text == "Success":
                                st.balloons()
                                st.rerun()
                else:
                    st.button(f"{owner}", key=f"R_{r_idx}", disabled=True, type="primary")

# 출입문 표시 등 하단 레이아웃 생략...
