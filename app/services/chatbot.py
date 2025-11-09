"""
Complete RAG + LLM Chatbot Service
벡터 검색 + OpenRouter LLM을 결합한 완전한 챗봇
"""
from typing import List, Dict, Optional
import logging
from .rag_simple import get_simple_rag_service, SimpleRAGService
from .openrouter import get_openrouter_client, OpenRouterClient
from .prompts import PromptTemplates

logger = logging.getLogger(__name__)


class ChatbotService:
    """
    완전한 RAG 기반 챗봇 서비스
    """
    
    def __init__(self):
        self.rag_service: Optional[SimpleRAGService] = None
        self.llm_client: Optional[OpenRouterClient] = None
        self._initialized = False
        
    def initialize(self):
        """챗봇 서비스 초기화"""
        if self._initialized:
            return
        
        try:
            logger.info("🚀 챗봇 서비스 초기화 중...")
            
            # RAG 서비스 초기화
            self.rag_service = get_simple_rag_service()
            self.rag_service.initialize()
            
            # OpenRouter 클라이언트 초기화
            self.llm_client = get_openrouter_client()
            
            self._initialized = True
            logger.info("✅ 챗봇 서비스 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ 챗봇 서비스 초기화 실패: {e}")
            raise
    
    async def generate_response(
        self,
        user_query: str,
        dbti_type: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        use_llm: bool = True,
        model: Optional[str] = None
    ) -> Dict:
        """
        사용자 질문에 대한 응답 생성
        
        Args:
            user_query: 사용자 질문
            dbti_type: 사용자의 DBTI 유형
            conversation_history: 이전 대화 기록
            use_llm: LLM 사용 여부 (False면 RAG만 사용)
            model: 사용할 LLM 모델
            
        Returns:
            Dict: 응답 및 메타데이터
        """
        if not self._initialized:
            self.initialize()
        
        try:
            # 1. RAG: 관련 컨텍스트 검색
            logger.info(f"🔍 검색 쿼리: {user_query[:50]}...")
            
            context_docs = self.rag_service.retrieve_context(
                query=user_query,
                top_k=3,
                dbti_filter=dbti_type,
                min_score=0.3
            )
            
            # 2. LLM 사용 여부에 따라 응답 생성
            if use_llm and self.llm_client.api_key:
                # OpenRouter LLM 사용
                response_text = await self._generate_llm_response(
                    user_query=user_query,
                    context_docs=context_docs,
                    dbti_type=dbti_type,
                    conversation_history=conversation_history,
                    model=model
                )
                method = "RAG + LLM"
            else:
                # RAG만 사용
                logger.info("ℹ️  LLM 미사용 - RAG 기반 응답")
                rag_result = self.rag_service.generate_response_with_context(
                    query=user_query,
                    dbti_type=dbti_type,
                    top_k=3
                )
                response_text = rag_result["response"]
                method = "RAG only"
            
            return {
                "response": response_text,
                "sources": [doc["title"] for doc in context_docs],
                "num_sources": len(context_docs),
                "confidence": context_docs[0]["score"] if context_docs else 0.0,
                "method": method,
                "dbti_type": dbti_type
            }
            
        except Exception as e:
            logger.error(f"❌ 응답 생성 실패: {e}", exc_info=True)
            
            # 폴백: 간단한 응답
            return {
                "response": "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                "sources": [],
                "num_sources": 0,
                "confidence": 0.0,
                "method": "fallback",
                "error": str(e)
            }
    
    async def _generate_llm_response(
        self,
        user_query: str,
        context_docs: List[Dict],
        dbti_type: Optional[str],
        conversation_history: Optional[List[Dict]],
        model: Optional[str]
    ) -> str:
        """
        OpenRouter LLM으로 응답 생성
        
        Args:
            user_query: 사용자 질문
            context_docs: 검색된 컨텍스트 문서
            dbti_type: DBTI 유형
            conversation_history: 대화 기록
            model: LLM 모델
            
        Returns:
            str: LLM 생성 응답
        """
        # 메시지 구성
        messages = PromptTemplates.create_conversation_messages(
            user_query=user_query,
            context_documents=context_docs,
            dbti_type=dbti_type,
            conversation_history=conversation_history
        )
        
        logger.info(f"🤖 LLM 응답 생성 중... (모델: {model or '기본'})")
        
        # OpenRouter API 호출
        result = await self.llm_client.chat_completion(
            messages=messages,
            model=model,
            temperature=0.7,
            max_tokens=1000
        )
        
        # 응답 추출
        if "choices" in result and len(result["choices"]) > 0:
            response_text = result["choices"][0]["message"]["content"]
            logger.info(f"✅ LLM 응답 생성 완료 ({len(response_text)}자)")
            return response_text
        else:
            logger.error("❌ LLM 응답에서 텍스트를 추출할 수 없습니다.")
            raise ValueError("Invalid LLM response format")
    
    async def explain_dbti_type(
        self,
        dbti_code: str,
        use_llm: bool = True
    ) -> Dict:
        """
        DBTI 유형에 대한 상세 설명 생성
        
        Args:
            dbti_code: DBTI 코드 (예: WTIL)
            use_llm: LLM 사용 여부
            
        Returns:
            Dict: 설명 및 메타데이터
        """
        if not self._initialized:
            self.initialize()
        
        # 해당 DBTI 유형의 모든 문서 검색
        dbti_docs = self.rag_service.search_by_dbti(dbti_code, top_k=10)
        
        if not dbti_docs:
            return {
                "response": f"{dbti_code} 유형에 대한 정보를 찾을 수 없습니다.",
                "sources": [],
                "confidence": 0.0
            }
        
        if use_llm and self.llm_client.api_key:
            # LLM으로 자연스러운 설명 생성
            prompt = PromptTemplates.create_dbti_explanation_prompt(
                dbti_code, dbti_docs
            )
            
            messages = [
                {"role": "system", "content": PromptTemplates.system_prompt(dbti_code)},
                {"role": "user", "content": prompt}
            ]
            
            result = await self.llm_client.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            )
            
            response_text = result["choices"][0]["message"]["content"]
        else:
            # RAG만 사용
            response_text = f"**{dbti_code} 유형 정보**:\n\n"
            for doc in dbti_docs[:5]:
                response_text += f"• {doc['title']}\n{doc['content']}\n\n"
        
        return {
            "response": response_text,
            "sources": [doc["title"] for doc in dbti_docs[:5]],
            "confidence": 1.0,
            "dbti_code": dbti_code
        }
    
    def get_status(self) -> Dict:
        """챗봇 서비스 상태 반환"""
        return {
            "initialized": self._initialized,
            "rag_available": self.rag_service is not None,
            "llm_available": self.llm_client is not None and bool(self.llm_client.api_key),
            "mode": "RAG + LLM" if (self.llm_client and self.llm_client.api_key) else "RAG only"
        }


# 전역 챗봇 서비스 인스턴스
_chatbot_service: Optional[ChatbotService] = None


def get_chatbot_service() -> ChatbotService:
    """챗봇 서비스 싱글톤 인스턴스 반환"""
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = ChatbotService()
    return _chatbot_service

