import streamlit as st

st.set_page_config(
    page_title="계약서 RAG 분석",
    page_icon="📄",
    layout="wide",
)

st.title("계약서 RAG 분석 웹앱")
st.caption("계약서를 업로드하고 주요 조항과 위험요소를 분석합니다.")

with st.sidebar:
    st.header("분석 설정")

    contract_type = st.selectbox(
        "계약 유형",
        [
            "일반 계약",
            "용역 계약",
            "구매 계약",
            "공급 계약",
            "NDA",
            "해외사업 계약",
        ],
    )

    review_position = st.selectbox(
        "검토 관점",
        [
            "중립",
            "발주자 관점",
            "계약상대자 관점",
        ],
    )

uploaded_file = st.file_uploader(
    "분석할 계약서를 업로드하세요",
    type=["pdf", "docx", "txt"],
)

if uploaded_file is None:
    st.info("PDF, DOCX 또는 TXT 계약서를 업로드하세요.")

else:
    st.success(f"{uploaded_file.name} 업로드 완료")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("파일명", uploaded_file.name)

    with col2:
        file_size_kb = uploaded_file.size / 1024
        st.metric("파일 크기", f"{file_size_kb:.1f} KB")

    with col3:
        st.metric("계약 유형", contract_type)

    st.divider()

    tab1, tab2, tab3 = st.tabs(
        [
            "계약서 요약",
            "위험조항 분석",
            "계약서 질문",
        ]
    )

    with tab1:
        st.subheader("계약서 요약")

        if st.button("계약서 요약 실행"):
            with st.spinner("계약서를 분석하고 있습니다..."):
                st.write("계약서 요약 결과가 이 영역에 표시됩니다.")
                st.write(f"검토 관점: {review_position}")
                st.write(f"계약 유형: {contract_type}")

    with tab2:
        st.subheader("위험조항 분석")

        analysis_items = st.multiselect(
            "분석 항목",
            [
                "계약기간",
                "대금 지급",
                "지체상금",
                "손해배상",
                "계약 해지",
                "보증",
                "비밀유지",
                "지식재산권",
                "준거법",
                "분쟁해결",
            ],
            default=[
                "대금 지급",
                "손해배상",
                "계약 해지",
            ],
        )

        if st.button("위험조항 분석 실행"):
            with st.spinner("위험조항을 확인하고 있습니다..."):
                for item in analysis_items:
                    with st.expander(item):
                        st.write("위험도: 분석 예정")
                        st.write("관련 조항: 분석 예정")
                        st.write("검토 의견: 분석 예정")
                        st.write("수정 권고안: 분석 예정")

    with tab3:
        st.subheader("계약서 질의응답")

        question = st.text_area(
            "계약서에 대해 질문하세요",
            placeholder="예: 계약 해지 조건과 손해배상 책임 한도를 알려줘.",
        )

        if st.button("질문 분석"):
            if not question.strip():
                st.warning("질문을 입력하세요.")
            else:
                with st.spinner("관련 조항을 검색하고 있습니다..."):
                    st.markdown("### 답변")
                    st.write(
                        "현재는 화면 확인용 버전입니다. "
                        "다음 단계에서 RAG 분석 모듈과 연결합니다."
                    )

                    st.markdown("### 관련 근거 조항")
                    st.info("검색된 계약 조항이 여기에 표시됩니다.")