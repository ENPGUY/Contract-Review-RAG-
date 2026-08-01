from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .ContractLLM import ContractLLM


class ContractAnalysisRAG:
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4.1-mini",
        top_k: int = 5,
    ):
        """
        계약서 검색과 OpenAI 답변 생성을 담당합니다.

        Args:
            api_key: OpenAI API 키
            model: 사용할 OpenAI 모델
            top_k: 질문과 관련된 계약서 청크 검색 개수
        """
        self.top_k = top_k

        self.llm = ContractLLM(
            api_key=api_key,
            model=model,
        )

        self.chunks: list[dict[str, Any]] = []

    def add_chunks(
        self,
        chunks: list[dict[str, Any]],
    ) -> None:
        """
        PDF에서 추출한 계약서 청크를 등록합니다.
        """
        valid_chunks = []

        for chunk in chunks:
            text = str(chunk.get("text", "")).strip()

            if not text:
                continue

            valid_chunks.append(
                {
                    "text": text,
                    "page": chunk.get(
                        "page",
                        "확인되지 않음",
                    ),
                }
            )

        self.chunks = valid_chunks

    def search(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        TF-IDF와 코사인 유사도를 사용하여 질문과 관련된
        계약서 청크를 검색합니다.
        """
        if not self.chunks:
            return []

        query = query.strip()

        if not query:
            return []

        limit = top_k or self.top_k
        limit = min(limit, len(self.chunks))

        documents = [
            chunk["text"]
            for chunk in self.chunks
        ]

        try:
            # 한글 검색을 위해 문자 단위 n-gram을 사용합니다.
            vectorizer = TfidfVectorizer(
                analyzer="char_wb",
                ngram_range=(2, 4),
                min_df=1,
            )

            matrix = vectorizer.fit_transform(
                documents + [query]
            )

            document_vectors = matrix[:-1]
            query_vector = matrix[-1]

            scores = cosine_similarity(
                query_vector,
                document_vectors,
            ).flatten()

            ranked_indexes = scores.argsort()[::-1][:limit]

            results = []

            for index in ranked_indexes:
                chunk = self.chunks[int(index)].copy()
                chunk["score"] = float(scores[index])
                results.append(chunk)

            return results

        except ValueError:
            # 텍스트가 너무 짧아 TF-IDF 계산이 불가능한 경우
            return self.chunks[:limit]

    def build_context(
        self,
        search_results: list[dict[str, Any]],
    ) -> str:
        """
        검색 결과를 LLM이 인용할 수 있는 근거 형식으로
        변환합니다.
        """
        context_parts = []

        for number, result in enumerate(
            search_results,
            start=1,
        ):
            text = result.get("text", "")
            page = result.get(
                "page",
                "확인되지 않음",
            )

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
        """
        관련 계약서 청크를 검색한 뒤 OpenAI API를 호출합니다.
        """
        if not self.chunks:
            return "계약서를 먼저 업로드하세요."

        if not question.strip():
            return "계약서에 대한 질문을 입력하세요."

        search_results = self.search(
            query=question,
            top_k=self.top_k,
        )

        if not search_results:
            return (
                "질문과 관련된 계약서 근거를 "
                "찾지 못했습니다."
            )

        context = self.build_context(search_results)

        return self.llm.answer_question(
            question=question,
            context=context,
            review_position=review_position,
        )
