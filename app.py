import streamlit as st
import pdfplumber
from SRC import RAG
from SRC import llm


# --------------------------------------------------
# rag 설정
# --------------------------------------------------

try:
    rag = ContractAnalysisRAG(
        api_key=st.secrets["OPENAI_API_KEY"],
        model=st.secrets.get("OPENAI_MODEL", "gpt-4.1-mini"),
        top_k=5,
    )

except KeyError:
    st.error("OPENAI_API_KEY가 설정되지 않았습니다.")
    st.stop()
    

st.set_page_config(
    page_title="AI 계약서 검토",
    page_icon="📄",
    layout="wide",
)

st.title("📄 AI 계약서 검토 시스템")
st.caption("계약서 내용을 기반으로 요약, 위험조항 분석 및 질의응답을 제공합니다.")


# --------------------------------------------------
# OpenAI API 설정
# --------------------------------------------------

try:
    api_key = st.secrets["OPENAI_API_KEY"]
    model = st.secrets.get("OPENAI_MODEL", "gpt-4.1-mini")

    llm = ContractLLM(
        api_key=api_key,
        model=model,
    )

except KeyError:
    st.error(
        "OPENAI_API_KEY가 설정되지 않았습니다. "
        "Streamlit Secrets를 확인하세요."
    )
    st.stop()


# --------------------------------------------------
# 검토 조건
# --------------------------------------------------

contract_type = st.selectbox(
    "계약 유형",
    [
        "용역계약",
        "물품구매계약",
        "공사계약",
        "비밀유지계약(NDA)",
        "해외사업계약",
        "기타",
    ],
)

review_position = st.selectbox(
    "검토 관점",
    [
        "발주자",
        "계약상대자",
        "중립적 관점",
    ],
)


# --------------------------------------------------
# 테스트용 계약서 입력
# 나중에는 PDF 추출 결과 또는 RAG 검색 결과를 넣습니다.
# --------------------------------------------------

chunks = [
    {
        "text": contract_text,
        "page": 1,
    }
]

rag.add_chunks(chunks)

uploaded_file = st.file_uploader(
    "계약서 PDF 업로드",
    type=["pdf"],
)

question = st.text_input(
    "계약서 질문",
    placeholder="예: 계약 해지 조건은 무엇인가요?",
)

if st.button("질문하기", type="primary"):
    if not question.strip():
        st.warning("질문을 입력하세요.")

    elif not rag.chunks:
        st.warning("계약서를 먼저 업로드하세요.")

    else:
        with st.spinner("계약서 근거를 검색하고 답변을 생성하고 있습니다..."):
            answer = rag.answer_with_rag(
                question=question,
                review_position=review_position,
            )

        st.markdown(answer)

contract_text = ""

if uploaded_file is not None:
    try:
        pages = []

        with pdfplumber.open(uploaded_file) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text() or ""

                if page_text.strip():
                    pages.append(
                        f"[페이지 {page_number}]\n{page_text}"
                    )

        contract_text = "\n\n".join(pages)

        if contract_text:
            st.success(
                f"계약서 {len(pages)}개 페이지의 텍스트를 추출했습니다."
            )

            with st.expander("추출된 계약서 내용 확인"):
                st.text_area(
                    "추출 결과",
                    value=contract_text,
                    height=350,
                    disabled=True,
                )
        else:
            st.warning(
                "PDF에서 텍스트를 추출하지 못했습니다. "
                "스캔 PDF라면 OCR 기능이 필요합니다."
            )

    except Exception as error:
        st.error(f"PDF 처리 중 오류가 발생했습니다: {error}")

# --------------------------------------------------
# 계약서 요약
# --------------------------------------------------

if st.button("계약서 요약", use_container_width=True):
    if not contract_text.strip():
        st.warning("계약서 내용을 입력하세요.")

    else:
        with st.spinner("계약서를 요약하고 있습니다..."):
            answer = llm.summarize_contract(
                context=contract_text,
                contract_type=contract_type,
                review_position=review_position,
            )

        st.markdown(answer)


# --------------------------------------------------
# 위험조항 분석
# --------------------------------------------------

analysis_items = st.multiselect(
    "위험 분석 항목",
    [
        "손해배상",
        "계약 해지",
        "지체상금",
        "검수 조건",
        "자동 갱신",
        "지식재산권",
        "비밀유지",
        "책임 제한",
        "준거법 및 관할",
    ],
    default=[
        "손해배상",
        "계약 해지",
        "지체상금",
        "검수 조건",
    ],
)

if st.button("위험조항 분석", use_container_width=True):
    if not contract_text.strip():
        st.warning("계약서 내용을 입력하세요.")

    elif not analysis_items:
        st.warning("분석할 항목을 선택하세요.")

    else:
        with st.spinner("위험조항을 분석하고 있습니다..."):
            answer = llm.analyze_risk(
                context=contract_text,
                analysis_items=analysis_items,
                contract_type=contract_type,
                review_position=review_position,
            )

        st.markdown(answer)


# --------------------------------------------------
# 계약서 질의응답
# --------------------------------------------------

st.divider()
st.subheader("계약서 질의응답")

question = st.text_input(
    "질문",
    placeholder="예: 계약상대자가 계약을 해지할 수 있는 조건은 무엇인가요?",
)

if st.button("질문하기", type="primary", use_container_width=True):
    if not contract_text.strip():
        st.warning("계약서 내용을 먼저 입력하세요.")

    elif not question.strip():
        st.warning("질문을 입력하세요.")

    else:
        with st.spinner("계약서에서 근거를 찾아 답변하고 있습니다..."):
            answer = llm.answer_question(
                question=question,
                context=contract_text,
                review_position=review_position,
            )

        st.markdown(answer)
