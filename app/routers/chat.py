"""
Chatbot API Router
AI 챗봇 API
"""
from fastapi import APIRouter, Depends
from ..models.chat import ChatRequest, ChatResponse
from ..services.rag_simple import get_simple_rag_service, SimpleRAGService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=ChatResponse,
    summary="챗봇 메시지 전송",
    description="RAG 기반 AI 챗봇에게 메시지를 전송하고 응답을 받습니다."
)
async def chat(
    request: ChatRequest,
    rag_service: SimpleRAGService = Depends(get_simple_rag_service)
) -> ChatResponse:
    """
    RAG + LLM 기반 챗봇 응답 생성
    
    - 벡터 검색으로 관련 문서 찾기
    - OpenRouter LLM으로 자연스러운 응답 생성
    
    Args:
        request: 챗봇 요청 (메시지, DBTI 유형, 대화 기록)
    
    Returns:
        ChatResponse: 챗봇 응답
    """
    try:
        # RAG + LLM으로 응답 생성
        rag_result = await rag_service.generate_response_with_context(
            query=request.message,
            dbti_type=request.dbti_type,
            top_k=3,
            use_llm=True
        )
        
        return ChatResponse(
            message=rag_result["response"],
            sources=rag_result["sources"],
            confidence=rag_result["confidence"],
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"❌ 챗봇 응답 생성 실패: {e}", exc_info=True)
        
        return ChatResponse(
            message="죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            sources=[],
            confidence=0.0,
            timestamp=datetime.now()
        )


@router.get(
    "/health",
    summary="챗봇 상태 확인",
    description="챗봇 서비스의 상태를 확인합니다."
)
async def chatbot_health():
    """챗봇 서비스 상태 확인"""
    return {
        "status": "ok",
        "message": "챗봇 서비스가 정상적으로 실행되고 있습니다."
    }

