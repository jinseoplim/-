import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="자리 배치~~", layout="wide")

# 모바일 가로 배열 유지 및 초록색 버튼 CSS
st.markdown("""
    <style>
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0px !important; }
    .stButton > button { width: 100% !important; height: 45px !important; font-size: 12px !important; padding: 0px !important; }
    div.stButton > button[kind="primary"] { background-color: #28a745 !important; color: white !important; border: none; }
    .monitor-box { text-align: center; background-color: #fceea7; padding: 10px; font-weight: bold; border: 1px solid #000; margin-bottom: 15px; }
    .desk-box { text-align: center; background-color: #fceea7; padding: 5px; font-size: 12px; border: 1px solid #000; width: 70px; margin-left: auto; }
    </style>
    """, unsafe_allow_html=True)

# 2. 구글 시트 연결
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

# 데이터 로드 (캐시 없이 실시간 반영)
def get_live_data():
    st.cache_data.clear()
    _df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)
    _df['seat_no'] = pd.to_numeric(_df['seat_no'], errors='coerce')
    return _df

df = get_live_data()

# 3. 사이드바 설정
st.sidebar.header("📋 로그인")
user_name = st.sidebar.text_input("이름을 입력하세요", placeholder="예: 임진섭")
GAS_URL = "https://script.google.com/macros/s/AKfycbwIyemiDDz0BKptG5z5IWtvtn6aQNiXv0qTZRWWACntR_g3DOqZ7Ix6uXvpmzTuLJf9aQ/exec"

if 'err' not in st.session_state: st.session_state.err = False

# 이선좌 알림창
if st.session_state.err:
    if st.error("🎟️ 이선좌 이선좌!! 이미 선택된 좌석입니다!"):
        if st.button("알림 닫기"):
            st.session_state.err = False
            st.rerun()

# 내 자리 확인 및 취소
my_seat = df[df['owner'] == user_name]['seat_no'].values[0] if user_name in df['owner'].values else None
if my_seat:
    st.sidebar.success(f"✅ {int(my_seat)}번 예약 중")
    if st.sidebar.button("예약 취소"):
        requests.get(GAS_URL, params={"owner": user_name})
        st.rerun()

# 4. 강의실 레이아웃 (1~66번)
st.markdown("<div class='monitor-box'>모니터 (강의실 정면)</div>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([6, 0.5, 6])
with c3: st.markdown("<div class='desk-box'>교탁</div>", unsafe_allow_html=True)

for r in range(6):
    cols = st.columns([1,1,1,1,1,1, 0.2, 1,1,1,1,1,1])
    for c in range(6):
        l_idx = (r * 12) + c + 1
        r_idx = (r * 12) + c + 7
        
        def draw_btn(column, idx):
            if idx > 66: return
            with column:
                owner = df[df['seat_no'] == idx]['owner'].values[0] if not df[df['seat_no'] == idx].empty else ""
                if pd.isna(owner) or owner == "":
                    if st.button(f"{idx}", key=f"s{idx}"):
                        if not user_name: st.sidebar.error("이름 입력!")
                        else:
                            res = requests.get(GAS_URL, params={"seat_no": idx, "owner": user_name})
                            st.session_state.err = (res.text == "Occupied")
                            if not st.session_state.err: st.balloons()
                            st.rerun()
                else:
                    st.button(f"{owner[:2]}", key=f"s{idx}", type="primary", disabled=(owner != user_name))

        draw_btn(cols[c], l_idx)
        if r == 0:
            with cols[c+7]: st.button("❌", key=f"x{c}", disabled=True)
        else:
            draw_btn(cols[c+7], r_idx)
