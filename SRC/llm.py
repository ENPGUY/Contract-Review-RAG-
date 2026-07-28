# SRC/llm.py

from openai import OpenAI


SYSTEM_PROMPT = """
당신은 한국어 계약서 검토 전문가입니다.

규칙:
1. 제공된 계약서 내용만 근거로 답변합니다.
2. 계약서에 없는 내용은 추측하지 않습니다.
3. 중요한 판단에는 반드시 [근거 N]을 표시합니다.
4. 금액, 날짜, 비율, 계약기간은 정확하게 작성합니다.
5. 불리하거나 모호한 조항은 위험 이유와 수정안을 제시합니다.
6. 계약서에서 확인되지 않는 내용은
   '계약서에서 확인되지 않음'이라고 답변합니다.
7. 최종 법률 자문이 아닌 계약 검토 참고 의견으로 작성합니다.
8. 답변은 읽기 쉬운 한국어 Markdown 형식으로 작성합니다.
"""


class ContractLLM:
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4.1-mini",
    ):
        if not api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

        self.client = OpenAI(
            api_key=api_key,
            timeout=60.0,
            max_retries=2,
        )
        self.model = model

    def generate(
        self,
        instruction: str,
        context: str,
        max_output_tokens: int = 2000,
    ) -> str:
        prompt = f"""
사용자 요청:
{instruction}

계약서 근거:
{context}

위 계약서 근거를 사용하여 답변하세요.
"""

        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=SYSTEM_PROMPT,
                input=prompt,
                max_output_tokens=max_output_tokens,
            )

            answer = response.output_text.strip()

            if not answer:
                return "LLM이 답변을 생성하지 못했습니다."

            return answer

        except Exception as error:
            return f"LLM 답변 생성 중 오류가 발생했습니다: {error}"

    def summarize_contract(
        self,
        context: str,
        contract_type: str,
        review_position: str,
    ) -> str:
        instruction = f"""
계약 유형: {contract_type}
검토 관점: {review_position}

다음 형식으로 계약서를 요약하세요.

## 계약 개요
- 계약 목적
- 계약 당사자
- 계약기간
- 계약금액
- 업무 또는 납품 범위

## 주요 권리와 의무
- 발주자 의무
- 계약상대자 의무

## 금액 및 지급조건
- 계약금액
- 지급 시기
- 지급 조건
- 검수 조건

## 계약 종료 및 책임
- 계약 해지 조건
- 손해배상
- 지체상금
- 보증 책임

## 주요 위험요소
- 불리하거나 모호한 조항
- 누락된 것으로 보이는 조항
- 추가 확인이 필요한 사항

모든 주요 판단에 [근거 N]을 표시하세요.
"""
        return self.generate(
            instruction=instruction,
            context=context,
            max_output_tokens=2500,
        )

    def analyze_risk(
        self,
        context: str,
        analysis_items: list[str],
        contract_type: str,
        review_position: str,
    ) -> str:
        items = ", ".join(analysis_items)

        instruction = f"""
계약 유형: {contract_type}
검토 관점: {review_position}
분석 항목: {items}

각 항목을 다음 표로 분석하세요.

| 분석 항목 | 위험도 | 원문 핵심내용 | 위험 이유 | 수정·협상 권고 |
|---|---|---|---|---|

위험도는 다음 중 하나로 표시하세요.

- 높음
- 중간
- 낮음
- 확인 필요

특히 다음 내용을 확인하세요.

- 무제한 손해배상
- 일방적인 계약 해지
- 과도한 지체상금
- 불명확한 검수 기준
- 자동 갱신
- 짧은 시정기간
- 지식재산권의 일방적 귀속
- 불리한 준거법 및 관할
- 책임 제한 조항 부재
- 비밀유지 기간 및 예외 부재

마지막에는 다음 내용을 추가하세요.

## 우선 협상할 조항 3개

## 권장 수정 문구

계약서에 없는 조항을 있다고 단정하지 마세요.
모든 판단에 [근거 N]을 표시하세요.
"""
        return self.generate(
            instruction=instruction,
            context=context,
            max_output_tokens=3000,
        )

    def answer_question(
        self,
        question: str,
        context: str,
        review_position: str,
    ) -> str:
        instruction = f"""
검토 관점: {review_position}

질문:
{question}

다음 순서로 답변하세요.

## 결론
질문에 대한 결론을 한두 문장으로 작성합니다.

## 계약서상 근거
관련된 원문 내용과 [근거 N]을 표시합니다.

## 실무적 의미와 위험
해당 조항이 검토자에게 어떤 영향을 주는지 설명합니다.

## 확인 또는 협상할 사항
추가 확인사항과 권장 협상 방향을 제시합니다.

답변할 근거가 부족하면
'계약서에서 충분한 근거를 확인하지 못했습니다'라고 작성하세요.
"""
        return self.generate(
            instruction=instruction,
            context=context,
            max_output_tokens=2000,
        )
