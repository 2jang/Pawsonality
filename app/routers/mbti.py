"""
MBTI API Router
MBTI 기반 강아지 추천 API
"""
from fastapi import APIRouter, HTTPException
from ..models.mbti import MBTIRequest, MBTIResponse, MBTIDogMatch
from datetime import datetime
import csv
from pathlib import Path
from typing import Dict, Optional

router = APIRouter()

# MBTI 데이터 캐시
_mbti_data: Optional[Dict] = None
_dog_match_data: Optional[Dict] = None


def load_mbti_data():
    """MBTI 데이터 로드"""
    global _mbti_data, _dog_match_data
    
    if _mbti_data is None:
        _mbti_data = {}
        mbti_csv = Path("data/raw/mbti_types.csv")
        if mbti_csv.exists():
            with open(mbti_csv, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    _mbti_data[row['MBTI']] = row
    
    if _dog_match_data is None:
        _dog_match_data = {}
        dog_csv = Path("data/raw/dog_match.csv")
        if dog_csv.exists():
            with open(dog_csv, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    _dog_match_data[row['MBTI']] = row
    
    return _mbti_data, _dog_match_data


@router.post(
    "/",
    response_model=MBTIResponse,
    summary="MBTI 기반 강아지 추천",
    description="사용자의 MBTI를 입력하면 어울리는 강아지 견종을 추천합니다."
)
async def get_mbti_dog_match(request: MBTIRequest) -> MBTIResponse:
    """
    MBTI 유형에 맞는 강아지 견종을 추천합니다.
    
    Args:
        request: MBTI 코드 (예: ENFP)
    
    Returns:
        MBTIResponse: MBTI 정보 + 추천 견종
    
    Raises:
        HTTPException: MBTI 정보를 찾을 수 없는 경우
    """
    mbti_code = request.mbti.upper()
    mbti_data, dog_data = load_mbti_data()
    
    # MBTI 정보 조회
    if mbti_code not in mbti_data:
        raise HTTPException(
            status_code=404,
            detail=f"MBTI 유형 '{mbti_code}'를 찾을 수 없습니다."
        )
    
    mbti_info = mbti_data[mbti_code]
    
    # 강아지 매칭 정보 조회
    if mbti_code not in dog_data:
        raise HTTPException(
            status_code=404,
            detail=f"MBTI 유형 '{mbti_code}'에 대한 강아지 추천 정보를 찾을 수 없습니다."
        )
    
    dog_info = dog_data[mbti_code]
    
    # 나무위키 URL 생성
    dog_name = dog_info['Dog'].split(', ')[-1] if ', ' in dog_info['Dog'] else dog_info['Dog']
    wiki_url = f"https://namu.wiki/w/{dog_name}"
    
    # 응답 생성
    response = MBTIResponse(
        mbti=mbti_code,
        type_name=mbti_info.get('Type Name', ''),
        description=mbti_info.get('Description', ''),
        recommended_dog=MBTIDogMatch(
            dog=dog_info['Dog'],
            personality=dog_info['Personality'],
            image_url=dog_info.get('Img URL'),
            wiki_url=wiki_url
        ),
        timestamp=datetime.now()
    )
    
    return response


@router.get(
    "/types",
    summary="모든 MBTI 유형 목록",
    description="사용 가능한 모든 MBTI 유형 목록을 반환합니다."
)
async def get_all_mbti_types():
    """모든 MBTI 유형 목록 반환"""
    mbti_data, _ = load_mbti_data()
    
    return {
        "count": len(mbti_data),
        "types": list(mbti_data.keys())
    }

