"""
Pawna (Pawsonality) Pydantic Models
Dog Personality Test Data Models
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PawnaQuestion(BaseModel):
    """Pawsonality 질문 모델"""
    id: int = Field(..., description="질문 ID (1-12)")
    title: str = Field(..., description="질문 제목")
    type: str = Field(..., description="MBTI 차원 (EI, SN, TF, JP)")
    option_a: str = Field(..., description="A 선택지")
    option_b: str = Field(..., description="B 선택지")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "title": "산책 나가자고 하면?",
                "type": "EI",
                "option_a": "즉시 뛰어나간다",
                "option_b": "잠시 생각한 후 나간다"
            }
        }
    }


class PawnaAnswer(BaseModel):
    """Pawsonality 답변 모델"""
    question_id: int = Field(..., ge=1, le=12, description="질문 ID (1-12)")
    selected: str = Field(..., pattern="^[AB]$", description="선택된 답변 (A 또는 B)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "question_id": 1,
                "selected": "A"
            }
        }
    }


class PawnaSubmission(BaseModel):
    """Pawsonality 제출 모델"""
    answers: List[PawnaAnswer] = Field(..., min_length=12, max_length=12, description="12개의 답변")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "answers": [
                    {"question_id": i, "selected": "A" if i % 2 == 0 else "B"}
                    for i in range(1, 13)
                ]
            }
        }
    }


class PawnaType(BaseModel):
    """Pawsonality 유형 정보"""
    pawna_code: str = Field(..., description="Pawna 코드 (예: WTIL)")
    mbti: str = Field(..., description="대응되는 MBTI 코드 (예: ENFP)")
    type_name: str = Field(..., description="유형 이름")
    description: str = Field(..., description="유형 설명")
    solution: str = Field(..., description="양육 솔루션")
    personality_traits: List[str] = Field(default_factory=list, description="성격 특성 목록")
    image_url: Optional[str] = Field(None, description="이미지 URL")
    site_url: Optional[str] = Field(None, description="참고 사이트 URL")


class PawnaResult(BaseModel):
    """Pawsonality 결과 모델"""
    pawna_code: str = Field(..., description="Pawna 유형 코드")
    pawna_type: Optional[str] = Field(None, description="Pawna 유형 코드 (호환성)")
    mbti_type: str = Field(..., description="MBTI 유형 코드")
    type_name: str = Field(..., description="유형 이름")
    description: str = Field(..., description="유형 설명")
    solution: str = Field(..., description="양육 솔루션")
    care_tips: List[str] = Field(default_factory=list, description="양육 팁")
    personality_traits: List[str] = Field(default_factory=list, description="성격 특성")
    compatibility: Optional[dict] = Field(None, description="궁합 정보")
    image_url: Optional[str] = Field(None, description="이미지 URL")
    site_url: Optional[str] = Field(None, description="참고 사이트 URL")
    timestamp: datetime = Field(default_factory=datetime.now, description="결과 생성 시간")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "pawna_code": "WTIL",
                "pawna_type": "WTIL",
                "mbti_type": "ENFP",
                "type_name": "활발한 탐험가",
                "description": "호기심 많고 활동적인 성격",
                "solution": "충분한 운동과 정신적 자극 필요",
                "personality_traits": ["활발함", "사교적", "호기심 많음"],
                "image_url": "https://example.com/wtil.png",
                "site_url": "https://example.com/wtil",
                "timestamp": "2025-11-06T15:00:00"
            }
        }
    }

