"""
DBTI API Router
Dog Behavior Type Indicator 검사 및 결과 조회 API
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.dbti import (
    DBTIQuestion,
    DBTISubmission,
    DBTIResult
)
from ..data.dbti_data import get_data_loader, DBTIDataLoader
from datetime import datetime

router = APIRouter()


@router.get(
    "/questions",
    response_model=List[DBTIQuestion],
    summary="DBTI 질문 목록 조회",
    description="12개의 DBTI 검사 질문을 조회합니다."
)
async def get_questions(
    data_loader: DBTIDataLoader = Depends(get_data_loader)
) -> List[DBTIQuestion]:
    """
    DBTI 검사를 위한 12개 질문을 반환합니다.
    
    Returns:
        List[DBTIQuestion]: 12개의 질문 목록
    """
    questions = data_loader.get_questions()
    return [DBTIQuestion(**q) for q in questions]


@router.post(
    "/submit",
    response_model=DBTIResult,
    summary="DBTI 검사 제출",
    description="12개 질문에 대한 답변을 제출하고 DBTI 유형 결과를 받습니다."
)
async def submit_dbti(
    submission: DBTISubmission,
    data_loader: DBTIDataLoader = Depends(get_data_loader)
) -> DBTIResult:
    """
    DBTI 검사 답변을 제출하고 결과를 받습니다.
    
    Args:
        submission: 12개 질문에 대한 답변
    
    Returns:
        DBTIResult: DBTI 유형 결과 (유형 코드, 설명, 솔루션 등)
    
    Raises:
        HTTPException: 유효하지 않은 답변이거나 DBTI 유형을 찾을 수 없는 경우
    """
    # 답변 검증
    if len(submission.answers) != 12:
        raise HTTPException(
            status_code=400,
            detail=f"정확히 12개의 답변이 필요합니다. (현재: {len(submission.answers)}개)"
        )
    
    # 답변을 딕셔너리 리스트로 변환
    answers_dict = [answer.model_dump() for answer in submission.answers]
    
    # DBTI 코드 계산
    dbti_code = data_loader.calculate_dbti(answers_dict)
    
    # DBTI 유형 정보 조회
    dbti_info = data_loader.get_dbti_type(dbti_code)
    
    if not dbti_info:
        raise HTTPException(
            status_code=404,
            detail=f"DBTI 유형 '{dbti_code}'를 찾을 수 없습니다."
        )
    
    # 결과 생성
    personality = dbti_info.get("Personality", "").split(", ") if dbti_info.get("Personality") else []
    solution = dbti_info.get("Solution", "")
    
    result = DBTIResult(
        dbti_code=dbti_code,
        dbti_type=dbti_code,  # 호환성
        mbti_type=dbti_info.get("MBTI", ""),
        type_name=dbti_info.get("Type Name", ""),
        description=dbti_info.get("Description", ""),
        solution=solution,
        care_tips=[solution] if solution else [],  # solution을 care_tips로도 제공
        personality_traits=personality,
        compatibility={
            "best_match": ["모든 유형과 잘 어울립니다"],
            "good_match": ["친근한 성격의 강아지들"]
        },
        image_url=dbti_info.get("Img URL"),
        site_url=dbti_info.get("Site URL"),
        timestamp=datetime.now()
    )
    
    return result


@router.get(
    "/types/{dbti_code}",
    response_model=DBTIResult,
    summary="DBTI 유형 조회",
    description="특정 DBTI 유형 코드에 대한 상세 정보를 조회합니다."
)
async def get_dbti_type(
    dbti_code: str,
    data_loader: DBTIDataLoader = Depends(get_data_loader)
) -> DBTIResult:
    """
    DBTI 유형 코드로 상세 정보를 조회합니다.
    
    Args:
        dbti_code: DBTI 유형 코드 (예: WTIL, DTLP 등)
    
    Returns:
        DBTIResult: DBTI 유형 상세 정보
    
    Raises:
        HTTPException: 유형을 찾을 수 없는 경우
    """
    dbti_code = dbti_code.upper()
    dbti_info = data_loader.get_dbti_type(dbti_code)
    
    if not dbti_info:
        raise HTTPException(
            status_code=404,
            detail=f"DBTI 유형 '{dbti_code}'를 찾을 수 없습니다."
        )
    
    personality = dbti_info.get("Personality", "").split(", ") if dbti_info.get("Personality") else []
    solution = dbti_info.get("Solution", "")
    
    result = DBTIResult(
        dbti_code=dbti_code,
        dbti_type=dbti_code,  # 호환성
        mbti_type=dbti_info.get("MBTI", ""),
        type_name=dbti_info.get("Type Name", ""),
        description=dbti_info.get("Description", ""),
        solution=solution,
        care_tips=[solution] if solution else [],  # solution을 care_tips로도 제공
        personality_traits=personality,
        compatibility={
            "best_match": ["모든 유형과 잘 어울립니다"],
            "good_match": ["친근한 성격의 강아지들"]
        },
        image_url=dbti_info.get("Img URL"),
        site_url=dbti_info.get("Site URL"),
        timestamp=datetime.now()
    )
    
    return result

