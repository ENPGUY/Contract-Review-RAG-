import streamlit as st

from src.llm import ContractLLM


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

contract_text = st.text_area(
    "계약서 내용",
    height=350,
    placeholder="계약서 내용을 입력하거나 PDF에서 추출한 내용을 연결하세요.",
)


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
