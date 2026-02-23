import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests
import time

# 페이지 설정
st.set_page_config(page_title="수의대 자리 티켓팅", layout="wide")

# (CSS 스타일은 이전과 동일하게 유지)
st.markdown("""
    <style>
    .monitor-box { text-align: center; background-color: #fceea7; padding: 10px; color: black; font-weight: bold; border: 2px solid #000; width: 50%; margin: 0 auto 20px auto; }
    .desk-box { text-align: center; background-color: #fceea7; padding: 8px; color: black; font-weight: bold; border: 2px solid #000; width: 150px; margin-left: auto; }
    .stButton>button { width: 100%; height: 50px; font-weight: bold; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 구글 시트 연결
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

# [해결책] 데이터 로딩 함수 (캐시를 강제로 비우는 기능 추가)
def get_data():
    st.cache_data.clear() # 이전 데이터를 지우고 새로 가져옴
    return conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)

df = get_data()

# 3. 사이드바 본인 인증 및 새 URL 입력
st.sidebar.header("📋 본인 인증")
user_name = st.sidebar.text_input("성함을 입력하세요", placeholder="예: 임진섭")
GAS_URL = "https://script.google.com/macros/s/AKfycbyo2FEqmGTW-EALt8LbYlUGPhufcFFQ7LWpYQl35G9G5quno4LGg8eTGysP8ZqIAJu-vw/exec"

# 내 자리 정보 확인
my_seat_data = df[df['owner'] == user_name]
my_seat = my_seat_data['seat_no'].values[0] if not my_seat_data.empty else None

if my_seat:
    st.sidebar.success(f"✅ 현재 {my_seat}번 좌석 사용 중")
    if st.sidebar.button("자리 취소하기"):
        requests.get(GAS_URL, params={"owner": user_name})
        st.rerun()

# 4. 좌석 배치 및 예약 로직
st.markdown("<div class='monitor-box'>모니터</div>", unsafe_allow_html=True)

for r in range(6):
    row_cols = st.columns([1,1,1,1,1,1, 0.5, 1,1,1,1,1,1])
    for c in range(6):
        l_idx = (r * 12) + c + 1
        r_idx = (r * 12) + c + 7
        
        # 좌석 버튼 생성 함수
        def create_seat(col, idx, current_owner):
            with col:
                if pd.isna(current_owner) or current_owner == "":
                    # 빈자리 클릭 시
                    if st.button(f"{idx}", key=f"seat_{idx}"):
                        if not user_name: st.sidebar.error("⚠️ 이름을 입력하세요!")
                        else:
                            with st.spinner('처리 중...'):
                                requests.get(GAS_URL, params={"seat_no": idx, "owner": user_name})
                                time.sleep(1) # 구글 시트 반영 시간을 위해 1초 대기
                                st.rerun()
                elif current_owner == user_name:
                    # 내 자리 클릭 시 (파란색으로 표시)
                    st.button(f"{user_name}", key=f"seat_{idx}", type="primary")
                else:
                    # 남의 자리
                    st.button(f"{current_owner}", key=f"seat_{idx}", disabled=True)

        create_seat(row_cols[c], l_idx, df[df['seat_no'] == l_idx]['owner'].values[0] if not df[df['seat_no'] == l_idx].empty else "")
        if r != 0: # 오른쪽 1행 X 제외
            create_seat(row_cols[c+7], r_idx, df[df['seat_no'] == r_idx]['owner'].values[0] if not df[df['seat_no'] == r_idx].empty else "")
        elif c < 6:
             with row_cols[c+7]: st.button("❌", key=f"x_{c}", disabled=True)
