"""
Prompt Templates for Pawsonality Chatbot
Pawsonality 챗봇을 위한 프롬프트 템플릿
"""
from typing import Optional, List


class PromptTemplates:
    """
    Pawsonality 챗봇 프롬프트 템플릿 모음
    """
    
    @staticmethod
    def get_system_prompt(pawna_type: Optional[str] = None) -> str:
        """
        시스템 프롬프트 생성
        
        Args:
            pawna_type: 사용자의 Pawna 유형 (선택)
            
        Returns:
            str: 시스템 프롬프트
        """
        base_prompt = """당신은 Pawsonality (Dog Personality Test) 전문가입니다.
반려견의 성격과 행동을 분석하고, 맞춤형 양육 가이드를 제공하는 AI 어시스턴트입니다.

## 역할
- 반려견의 Pawsonality 유형에 대해 설명
- 각 유형별 특성과 성격 소개
- 맞춤형 양육 방법 및 솔루션 제공
- 훈련, 산책, 사회화 등에 대한 조언

## 답변 스타일
- 친근하고 따뜻한 톤 사용
- 구체적이고 실용적인 조언 제공
- 이모지를 적절히 사용하여 읽기 쉽게 (🐾, 💡, 📌 등)
- 불필요하게 길지 않게, 핵심만 명확히

## 주의사항
- 수의학적 진단이나 치료는 수의사 상담 권장
- 참고 정보를 기반으로 정확한 답변 제공
- 모르는 내용은 솔직하게 인정"""
        
        if pawna_type:
            base_prompt += f"""

## 사용자 정보
- 반려견 Pawna 유형: {pawna_type}
- 이 유형의 특성을 고려하여 맞춤형 답변 제공"""
        
        return base_prompt
    
    @staticmethod
    def get_rag_prompt(query: str, context: str, pawna_type: Optional[str] = None) -> str:
        """
        RAG 기반 질문-답변 프롬프트
        
        Args:
            query: 사용자 질문
            context: RAG 컨텍스트
            pawna_type: Pawna 유형
            
        Returns:
            str: 프롬프트
        """
        prompt = f"""다음은 Pawsonality 지식 베이스에서 검색된 관련 정보입니다:

{context}

---

위 정보를 참고하여 다음 질문에 답변해주세요:
질문: {query}"""
        
        if pawna_type:
            prompt += f"\n(사용자의 반려견은 {pawna_type} 유형입니다)"
        
        prompt += """

답변 시 다음을 지켜주세요:
1. 제공된 참고 정보를 최대한 활용
2. 구체적이고 실용적인 조언 제공
3. 친근하고 이해하기 쉬운 표현 사용
4. 필요하면 이모지로 가독성 향상 (🐾, 💡, ⚠️ 등)"""
        
        return prompt
    
    @staticmethod
    def get_fallback_prompt() -> str:
        """
        폴백 프롬프트 (RAG 컨텍스트가 없을 때)
        """
        return """Pawsonality 지식 베이스에서 관련 정보를 찾지 못했습니다.
하지만 반려견 양육에 대한 일반적인 조언을 해드릴 수 있습니다.

질문에 대해 알고 있는 내용을 바탕으로 도움을 드리겠습니다.
단, 구체적인 Pawna 유형 정보는 제한적일 수 있습니다."""
    
    @staticmethod
    def get_greeting_prompt(pawna_type: Optional[str] = None) -> str:
        """
        인사 프롬프트
        """
        if pawna_type:
            return f"""안녕하세요! 🐾
{pawna_type} 유형 반려견의 보호자님이시군요!

{pawna_type} 유형에 대해 궁금하신 점이나, 
양육 방법, 훈련 팁 등 무엇이든 물어보세요!"""
        else:
            return """안녕하세요! 🐾
Pawsonality 챗봇입니다.

반려견의 Dog Personality 유형에 대해 궁금하신 점이나,
양육 방법에 대해 무엇이든 물어보세요!"""
    
    @staticmethod
    def format_response_with_sources(response: str, sources: List[str]) -> str:
        """
        응답에 출처 추가
        
        Args:
            response: LLM 응답
            sources: 참고한 문서 제목 리스트
            
        Returns:
            str: 출처가 포함된 응답
        """
        if not sources:
            return response
        
        formatted_response = response + "\n\n---\n📚 **참고 자료**:\n"
        for i, source in enumerate(sources, 1):
            formatted_response += f"{i}. {source}\n"
        
        return formatted_response
