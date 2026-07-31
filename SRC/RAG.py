from typing import Any

from .llm import ContractLLM


class ContractAnalysisRAG:
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4.1-mini",
        top_k: int = 5,
    ):
        self.top_k = top_k

        self.llm = ContractLLM(
            api_key=api_key,
            model=model,
        )

        # 실제 계약서 청크를 저장할 공간
        self.chunks: list[dict[str, Any]] = []

    def add_chunks(self, chunks: list[dict[str, Any]]) -> None:
        """PDF에서 추출·분할한 계약서 청크를 등록합니다."""
        self.chunks = chunks

    def search(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        임시 검색 함수입니다.

        실제 프로젝트에서는 TF-IDF, 임베딩 또는 벡터DB 검색 코드로
        교체해야 합니다.
        """
        limit = top_k or self.top_k

        # 현재는 앞쪽 청크를 반환하는 임시 코드
        return self.chunks[:limit]

    def build_context(
        self,
        search_results: list[dict[str, Any]],
    ) -> str:
        """검색 결과를 LLM이 인용할 수 있는 형식으로 변환합니다."""
        context_parts = []

        for number, result in enumerate(search_results, start=1):
            text = result.get("text", "")
            page = result.get("page", "확인되지 않음")

            context_parts.append(
                f"""[근거 {number}]
페이지: {page}
내용:
{text}
"""
            )

        return "\n\n".join(context_parts)

    def answer_with_rag(
        self,
        question: str,
        review_position: str,
    ) -> str:
        """관련 계약서 청크를 검색한 뒤 OpenAI API로 답변합니다."""

        search_results = self.search(
            query=question,
            top_k=self.top_k,
        )

        if not search_results:
            return "질문과 관련된 계약서 근거를 찾지 못했습니다."

        context = self.build_context(search_results)

        return self.llm.answer_question(
            question=question,
            context=context,
            review_position=review_position,
        )
