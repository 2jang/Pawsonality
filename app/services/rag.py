"""
RAG (Retrieval-Augmented Generation) Service
벡터 검색 + LLM을 결합한 지식 기반 응답 생성
"""
from typing import List, Dict, Optional
import logging
from .embeddings import get_embedding_service
from .vector_db import get_vector_db_service

logger = logging.getLogger(__name__)


class RAGService:
    """
    RAG 서비스: 벡터 검색으로 관련 문서를 찾고 컨텍스트로 사용
    """
    
    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.vector_db = get_vector_db_service()
        self._initialized = False
    
    def initialize(self):
        """RAG 서비스 초기화"""
        if self._initialized:
            return
        
        try:
            logger.info("🚀 RAG 서비스 초기화 중...")
            
            # 임베딩 모델 로드
            self.embedding_service.load_model()
            
            # 벡터 DB 연결 및 컬렉션 로드
            self.vector_db.connect()
            self.vector_db.create_collection()
            
            self._initialized = True
            logger.info("✅ RAG 서비스 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ RAG 서비스 초기화 실패: {e}")
            raise
    
    def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        pawna_filter: Optional[str] = None,
        min_score: float = 0.3
    ) -> List[Dict]:
        """
        쿼리에 대한 관련 컨텍스트 검색
        
        Args:
            query: 사용자 질문
            top_k: 반환할 문서 개수
            pawna_filter: Pawna 코드로 필터링
            min_score: 최소 유사도 점수
            
        Returns:
            List[Dict]: 관련 문서 리스트
        """
        if not self._initialized:
            self.initialize()
        
        # 쿼리 임베딩
        query_embedding = self.embedding_service.encode_text(query)
        
        # 벡터 검색
        results = self.vector_db.search(
            query_embedding=query_embedding.tolist(),
            top_k=top_k,
            pawna_filter=pawna_filter
        )
        
        # 최소 점수 필터링
        filtered_results = [r for r in results if r['score'] >= min_score]
        
        logger.info(f"🔍 검색 완료: {len(filtered_results)}/{len(results)}개 문서 (최소 점수: {min_score})")
        
        return filtered_results
    
    def format_context(self, retrieved_docs: List[Dict]) -> str:
        """
        검색된 문서를 LLM 프롬프트용 컨텍스트로 포맷팅
        
        Args:
            retrieved_docs: 검색된 문서 리스트
            
        Returns:
            str: 포맷된 컨텍스트 문자열
        """
        if not retrieved_docs:
            return "관련 정보를 찾을 수 없습니다."
        
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(
                f"[문서 {i}] {doc['title']}\n"
                f"{doc['content']}\n"
                f"(Pawna: {doc['pawna_code']}, 유사도: {doc['score']:.2f})"
            )
        
        return "\n\n".join(context_parts)
    
    def generate_response_with_context(
        self,
        query: str,
        pawna_type: Optional[str] = None,
        top_k: int = 3
    ) -> Dict:
        """
        RAG 기반 응답 생성
        
        Args:
            query: 사용자 질문
            pawna_type: 사용자의 Pawna 유형 (컨텍스트)
            top_k: 검색할 문서 개수
            
        Returns:
            Dict: 응답 및 메타데이터
        """
        # 1. 관련 컨텍스트 검색
        retrieved_docs = self.retrieve_context(
            query=query,
            top_k=top_k,
            pawna_filter=pawna_type
        )
        
        # 2. 컨텍스트 포맷팅
        context = self.format_context(retrieved_docs)
        
        # 3. 응답 생성
        # 현재는 검색된 컨텍스트 기반 간단한 응답
        if retrieved_docs:
            # 가장 관련성 높은 문서 사용
            top_doc = retrieved_docs[0]
            response = f"{top_doc['content']}"
            
            # Pawna 유형 정보 추가
            if pawna_type:
                response += f"\n\n💡 {pawna_type} 유형에 대한 맞춤 정보입니다."
        else:
            response = "죄송합니다. 관련 정보를 찾지 못했습니다. 다른 질문을 해주시겠어요?"
        
        return {
            "response": response,
            "context": context,
            "sources": [doc['title'] for doc in retrieved_docs],
            "num_sources": len(retrieved_docs),
            "confidence": retrieved_docs[0]['score'] if retrieved_docs else 0.0
        }
    
    def search_similar_questions(
        self,
        question: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        유사한 질문 검색 (FAQ 기능)
        
        Args:
            question: 검색할 질문
            top_k: 반환할 결과 개수
            
        Returns:
            List[Dict]: 유사한 질문 리스트
        """
        if not self._initialized:
            self.initialize()
        
        # 질문 임베딩
        query_embedding = self.embedding_service.encode_text(question)
        
        # QA 카테고리만 검색
        results = self.vector_db.search(
            query_embedding=query_embedding.tolist(),
            top_k=top_k
        )
        
        # QA 카테고리 필터링
        qa_results = [r for r in results if r.get('category') == 'qa']
        
        return qa_results


# 전역 RAG 서비스 인스턴스
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """RAG 서비스 싱글톤 인스턴스 반환"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service

