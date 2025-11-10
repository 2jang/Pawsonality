"""
간단한 RAG (Retrieval-Augmented Generation) Service
파일 기반 벡터 DB + OpenRouter LLM을 사용한 RAG 시스템
"""
from typing import List, Dict, Optional
import logging
from .embeddings import get_embedding_service
from .vector_db_simple import get_simple_vector_db
from .openrouter import get_openrouter_client
from .prompts import PromptTemplates
from ..config import settings

logger = logging.getLogger(__name__)


class SimpleRAGService:
    """
    간단한 RAG 서비스: 벡터 검색으로 관련 문서를 찾고 컨텍스트로 사용
    """
    
    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.vector_db = get_simple_vector_db()
        self.openrouter_client = get_openrouter_client()
        self.prompt_templates = PromptTemplates()
        self._initialized = False
        self._openrouter_available = False
    
    def initialize(self):
        """RAG 서비스 초기화"""
        if self._initialized:
            return
        
        try:
            logger.info("🚀 RAG 서비스 초기화 중...")
            
            # 임베딩 모델 로드
            self.embedding_service.load_model()
            
            # 벡터 DB 로드
            if not self.vector_db.load():
                logger.warning("⚠️  벡터 DB가 비어있습니다. setup_vectordb_simple.py를 먼저 실행하세요.")
            
            # OpenRouter 사용 가능 여부 확인
            if self.openrouter_client.api_key:
                self._openrouter_available = True
                logger.info("✅ OpenRouter API 사용 가능")
            else:
                logger.warning("⚠️  OpenRouter API 키가 없습니다. RAG 검색만 사용됩니다.")
            
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
            query_embedding=query_embedding,
            top_k=top_k,
            pawna_filter=pawna_filter,
            min_score=min_score
        )
        
        logger.info(f"🔍 검색 완료: {len(results)}개 문서 (최소 점수: {min_score})")
        
        return results
    
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
    
    async def generate_response_with_context(
        self,
        query: str,
        pawna_type: Optional[str] = None,
        top_k: int = 3,
        use_llm: bool = True
    ) -> Dict:
        """
        RAG 기반 응답 생성 (OpenRouter LLM 사용)
        
        Args:
            query: 사용자 질문
            pawna_type: 사용자의 Pawna 유형 (컨텍스트)
            top_k: 검색할 문서 개수
            use_llm: LLM 사용 여부 (False면 검색 결과만 반환)
            
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
        
        # 3. LLM으로 응답 생성
        if use_llm and self._openrouter_available and retrieved_docs:
            try:
                # 시스템 프롬프트 생성
                system_prompt = self.prompt_templates.get_system_prompt(pawna_type)
                
                # 메시지 포맷팅
                messages = self.openrouter_client.format_messages(
                    system_prompt=system_prompt,
                    user_message=query,
                    context=context
                )
                
                # OpenRouter API 호출
                selected_model = settings.OPENROUTER_MODEL
                logger.info(f"🤖 OpenRouter로 응답 생성 중 (모델: {selected_model})...")
                result = await self.openrouter_client.chat_completion(
                    messages=messages,
                    model=selected_model,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                # 응답 추출
                llm_response = result['choices'][0]['message']['content']
                
                # 출처 정보 추가
                response = self.prompt_templates.format_response_with_sources(
                    llm_response,
                    [doc['title'] for doc in retrieved_docs]
                )
                
                return {
                    "response": response,
                    "context": context,
                    "sources": [doc['title'] for doc in retrieved_docs],
                    "num_sources": len(retrieved_docs),
                    "confidence": retrieved_docs[0]['score'] if retrieved_docs else 0.0,
                    "llm_used": True,
                    "model": selected_model
                }
                
            except Exception as e:
                logger.error(f"❌ OpenRouter 응답 생성 실패: {e}")
                # 폴백: 검색 결과만 사용
                use_llm = False
        
        # 4. 폴백: 검색된 컨텍스트만 사용
        if retrieved_docs:
            # 가장 관련성 높은 문서 사용
            top_doc = retrieved_docs[0]
            response = f"💡 {top_doc['content']}"
            
            # 추가 정보가 있으면 포함
            if len(retrieved_docs) > 1:
                response += "\n\n📚 추가 참고 정보:\n"
                for i, doc in enumerate(retrieved_docs[1:], 2):
                    response += f"• {doc['title']}\n"
            
            # Pawna 유형 정보 추가
            if pawna_type:
                response += f"\n\n🐾 {pawna_type} 유형에 대한 맞춤 정보입니다."
        else:
            response = "죄송합니다. 관련 정보를 찾지 못했습니다. 다른 질문을 해주시겠어요?"
        
        return {
            "response": response,
            "context": context,
            "sources": [doc['title'] for doc in retrieved_docs],
            "num_sources": len(retrieved_docs),
            "confidence": retrieved_docs[0]['score'] if retrieved_docs else 0.0,
            "llm_used": False
        }
    
    def search_by_pawna(self, pawna_code: str, top_k: int = 10) -> List[Dict]:
        """
        특정 Pawna 유형에 대한 모든 정보 검색
        
        Args:
            pawna_code: Pawna 코드 (예: WTIL)
            top_k: 반환할 결과 개수
            
        Returns:
            List[Dict]: 해당 Pawna 유형의 문서 리스트
        """
        if not self._initialized:
            self.initialize()
        
        # 간단한 필터링 (Pawna 코드로만)
        all_docs = [doc for doc in self.vector_db.documents if doc['pawna_code'] == pawna_code]
        return all_docs[:top_k]


# 전역 RAG 서비스 인스턴스
_simple_rag_service: Optional[SimpleRAGService] = None


def get_simple_rag_service() -> SimpleRAGService:
    """간단한 RAG 서비스 싱글톤 인스턴스 반환"""
    global _simple_rag_service
    if _simple_rag_service is None:
        _simple_rag_service = SimpleRAGService()
    return _simple_rag_service

