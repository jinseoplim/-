import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# 페이지 설정
st.set_page_config(page_title="수의대 자리 티켓팅", layout="wide")

# CSS 스타일 (이미지 레이아웃 재현)
st.markdown("""
    <style>
    .monitor-box { text-align: center; background-color: #fceea7; padding: 10px; color: black; font-weight: bold; border: 2px solid #000; width: 50%; margin: 0 auto 20px auto; }
    .desk-box { text-align: center; background-color: #fceea7; padding: 8px; color: black; font-weight: bold; border: 2px solid #000; width: 150px; margin-left: auto; }
    .door-box { text-align: center; background-color: #fceea7; padding: 15px; color: black; font-weight: bold; border: 2px solid #000; width: 100px; }
    .stButton>button { width: 100%; height: 50px; font-weight: bold; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 수의과대학 2학년 강의실 자리 배치")

# 구글 시트 연결
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)

# 사이드바 설정
st.sidebar.header("📋 본인 인증")
user_name = st.sidebar.text_input("성함을 입력하세요", placeholder="예: 임진섭")
GAS_URL = "https://script.google.com/macros/s/AKfycby0pPNpjtos1AGIGNXDx7Qfoc5B4JvQURf6CrWNyfBqn0_J8AWn6WN3JNjD8aTi7PrURw/exec"

# 1인 1석 체크
is_registered = user_name in df['owner'].values
if is_registered:
    my_seat = df[df['owner'] == user_name]['seat_no'].values[0]
    st.sidebar.success(f"✅ {user_name}님은 {my_seat}번 자리에 등록됨")

# 강의실 상단 배치
st.markdown("<div class='monitor-box'>모니터</div>", unsafe_allow_html=True)
col_l, col_s, col_r = st.columns([6, 0.5, 6])
with col_r: st.markdown("<div class='desk-box'>교탁</div>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)

# 좌석 배치 로직 (1~6행)
for r in range(6):
    row_cols = st.columns([1,1,1,1,1,1, 0.5, 1,1,1,1,1,1])
    for c in range(6):
        # 번호 계산 (중복 없는 12단위 배열)
        l_idx = (r * 12) + c + 1
        r_idx = (r * 12) + c + 7
        
        # --- 왼쪽 블록 ---
        with row_cols[c]:
            owner = df[df['seat_no'] == l_idx]['owner'].values[0] if not df[df['seat_no'] == l_idx].empty else ""
            if pd.isna(owner) or owner == "":
                # 등록 안 된 경우만 버튼 활성화 (이미 등록된 사람은 클릭 금지)
                if st.button(f"{l_idx}", key=f"L_{l_idx}", disabled=is_registered):
                    if not user_name: st.sidebar.error("⚠️ 이름을 입력하세요!")
                    else:
                        res = requests.get(GAS_URL, params={"seat_no": l_idx, "owner": user_name})
                        st.rerun()
            else:
                st.button(f"{owner}", key=f"L_{l_idx}", disabled=True, type="primary")

        # --- 오른쪽 블록 ---
        with row_cols[c+7]:
            if r == 0: st.button("❌", key=f"x_{c}", disabled=True)
            else:
                owner = df[df['seat_no'] == r_idx]['owner'].values[0] if not df[df['seat_no'] == r_idx].empty else ""
                if pd.isna(owner) or owner == "":
                    if st.button(f"{r_idx}", key=f"R_{r_idx}", disabled=is_registered):
                        if not user_name: st.sidebar.error("⚠️ 이름을 입력하세요!")
                        else:
                            res = requests.get(GAS_URL, params={"seat_no": r_idx, "owner": user_name})
                            st.rerun()
                else:
                    st.button(f"{owner}", key=f"R_{r_idx}", disabled=True, type="primary")

# 하단 출입문
st.write("<br>", unsafe_allow_html=True)
d1, d2, d3 = st.columns([1, 10, 1])
with d1: st.markdown("<div class='door-box'>출입문</div>", unsafe_allow_html=True)
with d3: st.markdown("<div class='door-box'>출입문</div>", unsafe_allow_html=True)
