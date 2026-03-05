import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="206호 자리 배치", layout="wide")

# [디자인] '정면' 박스 크기 조절 및 레이아웃 최적화
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { padding: 0.5rem 0.1rem !important; }
    [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 1px !important; }
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0px !important; padding: 0px !important; }

    /* 타이틀 중앙 정렬 */
    .centered-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }

    /* 좌석 버튼 규격 (45px 높이 직사각형) */
    .stButton > button {
        width: 150% !important; 
        height: 45px !important; 
        min-height: 45px !important;
        max-height: 45px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0px !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        white-space: nowrap !important;
        border-radius: 4px !important;
        border: 1px solid #444 !important;
    }

    /* 예약 완료 초록색 버튼 */
    div.stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }

    /* 노란색 구조물 스타일 */
    .yellow-box { text-align: center; background-color: #fceea7; color: black; font-weight: bold; border: 1px solid #000; display: flex; align-items: center; justify-content: center; }
    
    /* [수정] 정면 박스: 너비를 60%로 줄이고 중앙 정렬 */
    .monitor { height: 30px; font-size: 16px; width: 20%; margin: 0 auto 15px auto; }
    
    /* 교탁 스타일 */
    .desk { height: 60px; font-size: 14px; width: 100%; line-height: 1.2; margin-bottom: 10px; }
    
    /* 강아지 이모지 스타일 */
    .doggy { font-size: 22px; text-align: center; margin: 5px 0; white-space: nowrap; }
    </style>
    """, unsafe_allow_html=True)

# 타이틀 중앙 정렬
st.markdown("<h1 class='centered-title'>206호 자리 배치</h1>", unsafe_allow_html=True)

# 2. 데이터 로드 (실시간 반영 및 nan 방지)
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_clean_data():
    st.cache_data.clear()
    _df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0)
    _df = _df.fillna("").replace("nan", "")
    _df['seat_no'] = _df['seat_no'].astype(str).str.strip()
    return _df

df = get_clean_data()

# 상태 관리
if 'occupied_error' not in st.session_state:
    st.session_state.occupied_error = False

# 3. 사이드바 인터페이스
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

# 배정 확인 알림
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

with layout_cols[1]: # 가운데 컬럼에 메인 콘텐츠 집중
    # 4. 강의실 구조물 (정면)
    st.markdown("<div class='yellow-box monitor'>모니터</div>", unsafe_allow_html=True)

    # 교탁 위치 (5-통로-5 구조 유지)
    desk_row = st.columns([1,1,1,1,1, 1.0, 1,1,1,1,1])
    with desk_row[8]: 
        st.markdown("<div class='yellow-box desk' style='width: 200% !important; margin-left: -50%;'>교탁</div>", unsafe_allow_html=True)
    st.write("")

    # 5. 좌석 배치 (5-통로-5)
    for r in range(6):
        cols = st.columns([1,1,1,1,1, 1.0, 1,1,1,1,1])
        for c in range(5):
            l_idx = str((r * 10) + c + 1)
            r_idx = str((r * 10) + c + 6)
            
            def draw_seat(column, idx, key_p):
                if int(idx) > 60: return # 최대 60석
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
                        st.button(f"{owner}", key=f"{key_p}_{idx}", type="primary", disabled=(owner != user_name))

            draw_seat(cols[c], l_idx, "L")
            draw_seat(cols[c+6], r_idx, "R")

    # [수정] 6. 하단 출입문 삭제 (전체 섹션 삭제됨)
    st.write("")
