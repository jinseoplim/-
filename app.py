import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="수의대 자리 티켓팅", layout="wide")
st.title("🏥 수의과대학 2학년 강의실 자리 배치 시스템")

# 2. 구글 시트 연결 (이게 핵심!)
url = "https://docs.google.com/spreadsheets/d/1_-b2IWVEQle2NirUEFIN38gm3-Vpytu_z-dcNYoP32I/edit?gid=0#gid=0/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

# 데이터 불러오기
df = conn.read(spreadsheet=url, usecols=[0, 1], ttl=0) # ttl=0은 실시간 갱신

# 3. 사이드바 - 이름 입력
st.sidebar.header("📋 본인 인증")
user_name = st.sidebar.text_input("성함을 입력하세요", placeholder="예: 임진섭")

# 4. 강의실 레이아웃 그리기
st.subheader("🖥️ 모니터 / 교탁 방향")
left_block, spacer, right_block = st.columns([5, 1, 5])

def draw_seats(block, start_num, end_num, is_right=False):
    with block:
        for r in range(6):
            cols = st.columns(6)
            for c in range(6):
                # 오른쪽 블록 1열(1행) 'x' 처리
                if is_right and r == 0:
                    cols[c].button("❌", key=f"x_{r}_{c}", disabled=True)
                    continue
                
                # 좌석 번호 매칭 (진섭 님 이미지 로직 반영)
                s_idx = (r * 6) + c + start_num if not is_right else (r * 6) + c + start_num
                if s_idx > 66: continue

                # 해당 번호의 주인 찾기
                seat_info = df[df['seat_no'] == s_idx]
                owner = seat_info['owner'].values[0] if not seat_info.empty else ""

                if pd.isna(owner) or owner == "":
                    if cols[c].button(f"{s_idx}\n예약", key=f"s_{s_idx}"):
                        if not user_name:
                            st.sidebar.error("⚠️ 이름을 먼저 입력하세요!")
                        else:
                            # 구글 시트에 즉시 반영
                            df.loc[df['seat_no'] == s_idx, 'owner'] = user_name
                            conn.update(spreadsheet=url, data=df)
                            st.balloons() # 축하 효과!
                            st.rerun()
                else:
                    cols[c].button(f"{s_idx}\n{owner}", key=f"s_{s_idx}", disabled=True, type="primary")

draw_seats(left_block, 1, 60)
draw_seats(right_block, 13, 66, is_right=True) # 오른쪽 블록 시작번호 보정 필요 시 수정

st.sidebar.markdown("---")
st.sidebar.write("※ 예약 후 취소는 과대표에게 직접 연락주세요.")
