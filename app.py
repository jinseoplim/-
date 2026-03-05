import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="206호 자리 배치", layout="wide")

# [디자인] 버튼 중심 고정 및 글자 수에 따른 밀림 방지 CSS
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { padding: 0.5rem 0.1rem !important; }
    
    /* [수정] 좌석 사이 간격 조절 및 중심 고정 */
    [data-testid="stHorizontalBlock"] { 
        flex-wrap: nowrap !important; 
        gap: 15px !important; /* 너무 넓었던 gap을 적절히 조절 */
        justify-content: center !important; 
    }
    
    [data-testid="column"] { 
        flex: 1 1 0% !important; 
        min-width: 0px !important; 
        padding: 0px !important;
        display: flex !important;
        justify-content: center !important; /* 컬럼 자체의 중심을 고정 */
    }

    /* [핵심 수정] 좌석 버튼: 너비를 100%로 고정하되, 컬럼 너비 안에서만 존재하게 함 */
    .stButton {
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
    }

    .stButton > button {
        width: 140px !important; /* 버튼의 절대적인 가로 길이를 고정 (밀림 방지 핵심) */
        height: 45px !important; 
        min-height: 45px !important;
        max-height: 45px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0px 5px !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        
        /* 글자가 길어질 경우 상자가 늘어나는 대신 말줄임표 처리 */
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        
        border-radius: 4px !important;
        border: 1px solid #444 !important;
        margin-bottom: 8px !important;
    }

    /* 사이드바 버튼 복구 */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        height: auto !important;
        min-height: 0px !important;
        padding: 0.5rem 1rem !important;
    }

    div.stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }

    .yellow-box { text-align: center; background-color: #fceea7; color: black; font-weight: bold; border: 1px solid #000; display: flex; align-items: center; justify-content: center; }
    .monitor { height: 35px; font-size: 16px; width: 20%; margin: 0 auto 20px auto; }
    .desk { height: 60px; font-size: 14px; width: 100%; line-height: 1.2; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; font-size: 2.8rem; font-weight: 700; margin-bottom: 1rem;'>206호 자리 배치</h1>", unsafe_allow_html=True)

# 2. 데이터 로드
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_clean_data():
    st.cache_data.clear()
    _df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)
    _df = _df.fillna("").replace("nan", "")
    _df['seat_no'] = _df['seat_no'].astype(str).str.strip()
    return _df

df = get_clean_data()

if 'occupied_error' not in st.session_state:
    st.session_state.occupied_error = False

# 3. 사이드바
user_name = st.sidebar.text_input("이름 입력", placeholder="예: 임진섭")
GAS_URL = "https://script.google.com/macros/s/AKfycbwIyemiDDz0BKptG5z5IWtvtn6aQNiXv0qTZRWWACntR_g3DOqZ7Ix6uXvpmzTuLJf9aQ/exec"

if st.session_state.occupied_error:
    st.error("🎟️ 이선좌! 이미 선택된 좌석입니다. 새로고침 후 다시 시도하세요.")
    if st.button("알림 닫기 ✖️"):
        st.session_state.occupied_error = False
        st.rerun()

if st.sidebar.button("🔄 실시간 현황 새로고침"):
    st.session_state.occupied_error = False
    st.rerun()

my_seat_row = df[df['owner'] == user_name]
has_seat = not my_seat_row.empty and user_name != ""

if has_seat:
    my_seat = my_seat_row['seat_no'].values[0]
    st.sidebar.success(f"✅ {my_seat}번 좌석 배정됨")
    st.sidebar.info("💡 좌석 변경을 원하실 경우 이동할 새 좌석을 선택하세요.")
else:
    if user_name != "":
        st.sidebar.warning("📍 아직 배정된 좌석이 없습니다.")

# ==============================================================================
# 메인 콘텐츠 중앙 정렬 레이아웃
# ==============================================================================
layout_cols = st.columns([1, 14, 1])

with layout_cols[1]: 
    st.markdown("<div class='yellow-box monitor'>모니터</div>", unsafe_allow_html=True)

    desk_row = st.columns([1,1,1,1,1, 1.0, 1,1,1,1,1])
    with desk_row[8]: 
        st.markdown("<div class='yellow-box desk' style='width: 200% !important; margin-left: -50%;'>교탁</div>", unsafe_allow_html=True)
    st.write("")

    # 5. 좌석 배치
    for r in range(6):
        cols = st.columns([1,1,1,1,1, 1.0, 1,1,1,1,1])
        for c in range(5):
            l_idx = str((r * 10) + c + 1)
            r_idx = str((r * 10) + c + 6)
            
            def draw_seat(column, idx, key_p):
                if int(idx) > 60: return 
                with column:
                    owner = df[df['seat_no'] == idx]['owner'].values[0] if not df[df['seat_no'] == idx].empty else ""
                    if not owner or owner == "":
                        if st.button(f"{idx}", key=f"{key_p}_{idx}"):
                            if not user_name: st.sidebar.error("이름을 입력하세요!")
                            else:
                                st.session_state.occupied_error = False
                                res = requests.get(GAS_URL, params={"seat_no": idx, "owner": user_name})
                                if res.text == "Occupied":
                                    st.session_state.occupied_error = True
                                else:
                                    st.balloons()
                                st.rerun()
                    else:
                        # 본인 좌석만 초록색(primary), 나머지는 이름 표시
                        st.button(f"{owner}", key=f"{key_p}_{idx}", type="primary", disabled=(owner != user_name))

            draw_seat(cols[c], l_idx, "L")
            draw_seat(cols[c+6], r_idx, "R")

    st.write("")
