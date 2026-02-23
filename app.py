st.markdown("""
    <style>
    /* 1. 모든 좌석 버튼의 규격을 초록색 칸과 동일하게 고정 */
    .stButton > button {
        width: 100% !important;   /* 칸의 너비를 꽉 채움 */
        height: 42px !important;  /* [중요] 모든 버튼의 높이를 이 수치로 통일 */
        
        padding: 0px !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        
        /* 텍스트가 중앙에 오도록 고정 */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        
        white-space: nowrap !important;
        overflow: hidden !important; /* 이름이 길어도 박스 크기 유지 */
        text-overflow: ellipsis !important;
        
        border-radius: 4px !important;
        border: 1px solid #444 !important;
    }

    /* 2. 예약된 칸(Primary)과 빈 칸의 사이즈 차이를 없앰 */
    div.stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
        /* 높이와 너비는 위에서 이미 공통으로 설정됨 */
    }

    /* 3. 모바일에서 12칸이 뭉개지지 않도록 여백 조정 */
    [data-testid="stHorizontalBlock"] { gap: 2px !important; flex-wrap: nowrap !important; }
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0px !important; padding: 0px 1px !important; }
    </style>
    """, unsafe_allow_html=True)
