"""
Chatbot Pydantic Models
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChatMessage(BaseModel):
    """채팅 메시지 모델"""
    role: str = Field(..., pattern="^(user|assistant|system)$", description="메시지 역할")
    content: str = Field(..., min_length=1, description="메시지 내용")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="메시지 시간")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "role": "user",
                "content": "우리 강아지가 WTIL인데 산책을 어떻게 해야 하나요?",
                "timestamp": "2025-11-06T15:00:00"
            }
        }
    }


class ChatRequest(BaseModel):
    """챗봇 요청 모델"""
    message: str = Field(..., min_length=1, max_length=1000, description="사용자 메시지")
    dbti_type: Optional[str] = Field(None, description="사용자의 DBTI 유형 (컨텍스트)")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default_factory=list,
        max_length=10,
        description="최근 대화 기록 (최대 10개)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "우리 강아지가 산책 중에 다른 강아지를 보면 짖어요",
                "dbti_type": "WTIL",
                "conversation_history": []
            }
        }
    }


class ChatResponse(BaseModel):
    """챗봇 응답 모델"""
    message: str = Field(..., description="챗봇 응답 메시지")
    sources: Optional[List[str]] = Field(default_factory=list, description="참고한 지식 소스")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="응답 신뢰도 (0-1)")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "WTIL 유형의 강아지는 활발하고 호기심이 많아...",
                "sources": ["DBTI 유형 가이드", "반려견 행동학"],
                "confidence": 0.95,
                "timestamp": "2025-11-06T15:00:00"
            }
        }
    }

