import tempfile

import streamlit as st

from SRC.contract_analysis import ContractAnalysisRAG


st.set_page_config(
    page_title="계약서 RAG 분석",
    page_icon="📄",
    layout="wide",
)

st.title("계약서 RAG 분석")
st.caption("PDF 계약서를 업로드하고 관련 조항을 검색합니다.")

uploaded_file = st.file_uploader(
    "계약서 PDF 업로드",
    type=["pdf"],
)

question = st.text_input(
    "계약서에 질문하세요",
    placeholder="예: 계약 해지 조건과 손해배상 책임은?",
)

if uploaded_file:
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf",
    ) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        pdf_path = temp_file.name

    st.success(f"{uploaded_file.name} 업로드 완료")

    if st.button("계약서 분석", type="primary"):
        if not question.strip():
            st.warning("질문을 입력하세요.")
        else:
            try:
                with st.spinner("계약서를 분석하고 있습니다..."):
                    rag = ContractAnalysisRAG()
                    result = rag.analyze_contract(
                        pdf_path,
                        question,
                    )

                st.subheader("분석 결과")
                st.write(result)

            except Exception as error:
                st.error(f"실행 오류: {error}")
                st.info(
                    "ContractAnalysisRAG 클래스의 실제 메서드 이름과 "
                    "app.py의 호출 부분을 맞춰야 합니다."
                )
else:
    st.info("분석할 PDF 계약서를 업로드하세요.")