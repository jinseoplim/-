import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. 페이지 설정 및 스타일 정의
st.set_page_config(page_title="수의대 자리 티켓팅", layout="wide")

st.markdown("""
    <style>
    .monitor-box {
        text-align: center;
        background-color: #fceea7;
        padding: 10px;
        color: black;
        font-weight: bold;
        font-size: 22px;
        border: 2px solid #000;
        width: 50%;
        margin: 0 auto 30px auto;
    }
    .desk-box {
        text-align: center;
        background-color: #fceea7;
        padding: 8px;
        color: black;
        font-weight: bold;
        border: 2px solid #000;
        width: 150px;
        margin-left: auto;
    }
    .door-box {
        text-align: center;
        background-color: #fceea7;
        padding: 15px;
        color: black;
        font-weight: bold;
        border: 2px solid #000;
        width: 100px;
    }
    .stButton>button {
        width: 100%;
        height: 60px;
        font-weight: bold;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 수의과대학 2학년 강의실 자리 배치 시스템")

# 2. 구글 시트 연결 (진섭 님 ID 반영)
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)

# 3. 사이드바 본인 인증
st.sidebar.header("📋 본인 인증")
user_name = st.sidebar.text_input("성함을 입력하세요", placeholder="예: 임진섭")

# 4. 상단 배치 (모니터)
st.markdown("<div class='monitor-box'>모니터</div>", unsafe_allow_html=True)

# 5. 교탁 배치 (오른쪽 블록 바로 위)
col_l, col_s, col_r = st.columns([6, 0.5, 6])
with col_r:
    st.markdown("<div class='desk-box'>교탁</div>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)

# 6. 좌석 배치 (1~6행)
for r in range(6):
    row_cols = st.columns([1,1,1,1,1,1, 0.5, 1,1,1,1,1,1])
    
    for c in range(6):
        # 왼쪽 블록 번호 (1-6, 7-12, 19-24...)
        l_idx = (r * 6) + c + 1
        with row_cols[c]:
            owner_data = df[df['seat_no'] == l_idx]['owner']
            owner = owner_data.values[0] if not owner_data.empty else ""
            
            if pd.isna(owner) or owner == "":
                if st.button(f"{l_idx}", key=f"L_{l_idx}"):
                    if not user_name: st.sidebar.error("⚠️ 이름을 입력하세요!")
                    else:
                        df.loc[df['seat_no'] == l_idx, 'owner'] = user_name
                        conn.update(spreadsheet=url, data=df)
                        st.rerun()
            else:
                st.button(f"{owner}", key=f"L_{l_idx}", disabled=True, type="primary")

        # 오른쪽 블록 번호 (x, 13-18, 25-30...)
        with row_cols[c+7]:
            if r == 0:
                st.button("❌", key=f"x_{c}", disabled=True)
            else:
                r_idx = (r * 6) + c + 7 # 2행 첫번째가 13이 되도록 계산
                owner_data = df[df['seat_no'] == r_idx]['owner']
                owner = owner_data.values[0] if not owner_data.empty else ""
                
                if pd.isna(owner) or owner == "":
                    if st.button(f"{r_idx}", key=f"R_{r_idx}"):
                        if not user_name: st.sidebar.error("⚠️ 이름을 입력하세요!")
                        else:
                            df.loc[df['seat_no'] == r_idx, 'owner'] = user_name
                            conn.update(spreadsheet=url, data=df)
                            st.rerun()
                else:
                    st.button(f"{owner}", key=f"R_{r_idx}", disabled=True, type="primary")

st.write("<br>", unsafe_allow_html=True)

# 7. 하단 배치 (출입문)
door_left, door_spacer, door_right = st.columns([1, 10, 1])
with door_left:
    st.markdown("<div class='door-box'>출입문</div>", unsafe_allow_html=True)
with door_right:
    st.markdown("<div class='door-box'>출입문</div>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.write(f"접속자: {user_name if user_name else '미인증'}")
