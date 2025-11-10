"""
Pawsonality API Router
Dog Personality Test 검사 및 결과 조회 API
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.pawna import (
    PawnaQuestion,
    PawnaSubmission,
    PawnaResult
)
from ..data.pawna_data import get_data_loader, PawnaDataLoader
from datetime import datetime

router = APIRouter()


@router.get(
    "/questions",
    response_model=List[PawnaQuestion],
    summary="Pawsonality 질문 목록 조회",
    description="12개의 Dog Personality Test 질문을 조회합니다."
)
async def get_questions(
    data_loader: PawnaDataLoader = Depends(get_data_loader)
) -> List[PawnaQuestion]:
    """
    Pawsonality 검사를 위한 12개 질문을 반환합니다.
    
    Returns:
        List[PawnaQuestion]: 12개의 질문 목록
    """
    questions = data_loader.get_questions()
    return [PawnaQuestion(**q) for q in questions]


@router.post(
    "/submit",
    response_model=PawnaResult,
    summary="Pawsonality 검사 제출",
    description="12개 질문에 대한 답변을 제출하고 Pawsonality 유형 결과를 받습니다."
)
async def submit_pawna(
    submission: PawnaSubmission,
    data_loader: PawnaDataLoader = Depends(get_data_loader)
) -> PawnaResult:
    """
    Pawsonality 검사 답변을 제출하고 결과를 받습니다.
    
    Args:
        submission: 12개 질문에 대한 답변
    
    Returns:
        PawnaResult: Pawsonality 유형 결과 (유형 코드, 설명, 솔루션 등)
    
    Raises:
        HTTPException: 유효하지 않은 답변이거나 유형을 찾을 수 없는 경우
    """
    # 답변 검증
    if len(submission.answers) != 12:
        raise HTTPException(
            status_code=400,
            detail=f"정확히 12개의 답변이 필요합니다. (현재: {len(submission.answers)}개)"
        )
    
    # 답변을 딕셔너리 리스트로 변환
    answers_dict = [answer.model_dump() for answer in submission.answers]
    
    # Pawna 코드 계산
    pawna_code = data_loader.calculate_pawna(answers_dict)
    
    # Pawna 유형 정보 조회
    pawna_info = data_loader.get_pawna_type(pawna_code)
    
    if not pawna_info:
        raise HTTPException(
            status_code=404,
            detail=f"Pawna 유형 '{pawna_code}'를 찾을 수 없습니다."
        )
    
    # 결과 생성
    personality = pawna_info.get("Personality", "").split(", ") if pawna_info.get("Personality") else []
    solution = pawna_info.get("Solution", "")
    
    result = PawnaResult(
        pawna_code=pawna_code,
        pawna_type=pawna_code,  # 호환성
        mbti_type=pawna_info.get("MBTI", ""),
        type_name=pawna_info.get("Type Name", ""),
        description=pawna_info.get("Description", ""),
        solution=solution,
        care_tips=[solution] if solution else [],  # solution을 care_tips로도 제공
        personality_traits=personality,
        compatibility={
            "best_match": ["모든 유형과 잘 어울립니다"],
            "good_match": ["친근한 성격의 강아지들"]
        },
        image_url=pawna_info.get("Img URL"),
        site_url=pawna_info.get("Site URL"),
        timestamp=datetime.now()
    )
    
    return result


@router.get(
    "/types/{pawna_code}",
    response_model=PawnaResult,
    summary="Pawsonality 유형 조회",
    description="특정 Pawsonality 유형 코드에 대한 상세 정보를 조회합니다."
)
async def get_pawna_type(
    pawna_code: str,
    data_loader: PawnaDataLoader = Depends(get_data_loader)
) -> PawnaResult:
    """
    Pawsonality 유형 코드로 상세 정보를 조회합니다.
    
    Args:
        pawna_code: Pawsonality 유형 코드 (예: WTIL, DTLP 등)
    
    Returns:
        PawnaResult: Pawsonality 유형 상세 정보
    
    Raises:
        HTTPException: 유형을 찾을 수 없는 경우
    """
    pawna_code = pawna_code.upper()
    pawna_info = data_loader.get_pawna_type(pawna_code)
    
    if not pawna_info:
        raise HTTPException(
            status_code=404,
            detail=f"Pawsonality 유형 '{pawna_code}'를 찾을 수 없습니다."
        )
    
    personality = pawna_info.get("Personality", "").split(", ") if pawna_info.get("Personality") else []
    solution = pawna_info.get("Solution", "")
    
    result = PawnaResult(
        pawna_code=pawna_code,
        pawna_type=pawna_code,  # 호환성
        mbti_type=pawna_info.get("MBTI", ""),
        type_name=pawna_info.get("Type Name", ""),
        description=pawna_info.get("Description", ""),
        solution=solution,
        care_tips=[solution] if solution else [],  # solution을 care_tips로도 제공
        personality_traits=personality,
        compatibility={
            "best_match": ["모든 유형과 잘 어울립니다"],
            "good_match": ["친근한 성격의 강아지들"]
        },
        image_url=pawna_info.get("Img URL"),
        site_url=pawna_info.get("Site URL"),
        timestamp=datetime.now()
    )
    
    return result

