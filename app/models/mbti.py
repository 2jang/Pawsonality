"""
MBTI & Dog Matching Pydantic Models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MBTIType(BaseModel):
    """MBTI 유형 정보"""
    mbti: str = Field(..., pattern="^[IE][SN][TF][JP]$", description="MBTI 코드 (예: ENFP)")
    type_name: str = Field(..., description="유형 이름")
    description: str = Field(..., description="유형 설명")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "mbti": "ENFP",
                "type_name": "재기발랄한 활동가",
                "description": "열정적이고 창의적이며 사교적인 성격"
            }
        }
    }


class MBTIDogMatch(BaseModel):
    """MBTI와 매칭되는 강아지 견종"""
    dog: str = Field(..., description="추천 견종")
    personality: str = Field(..., description="견종 성격 설명")
    image_url: Optional[str] = Field(None, description="견종 이미지 URL")
    wiki_url: Optional[str] = Field(None, description="나무위키 URL")


class MBTIRequest(BaseModel):
    """MBTI 조회 요청"""
    mbti: str = Field(..., pattern="^[IE][SN][TF][JP]$", description="MBTI 코드 (예: ENFP)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "mbti": "ENFP"
            }
        }
    }


class MBTIResponse(BaseModel):
    """MBTI 조회 응답"""
    mbti: str = Field(..., description="MBTI 코드")
    type_name: str = Field(..., description="유형 이름")
    description: str = Field(..., description="유형 설명")
    recommended_dog: MBTIDogMatch = Field(..., description="추천 견종 정보")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "mbti": "ENFP",
                "type_name": "재기발랄한 활동가",
                "description": "열정적이고 창의적인 성격",
                "recommended_dog": {
                    "dog": "골든 리트리버",
                    "personality": "사교적이고 활발한 성격",
                    "image_url": "https://example.com/golden.jpg",
                    "wiki_url": "https://namu.wiki/w/골든 리트리버"
                },
                "timestamp": "2025-11-06T15:00:00"
            }
        }
    }

