"""
OpenRouter API Client
다양한 LLM 모델을 사용할 수 있는 OpenRouter API 클라이언트
"""
from typing import List, Dict, Optional, AsyncGenerator
import httpx
import logging
from ..config import settings

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """
    OpenRouter API 클라이언트
    Claude, GPT-4, Llama 등 다양한 모델 지원
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1"
    ):
        """
        Args:
            api_key: OpenRouter API 키 (없으면 설정에서 가져옴)
            base_url: OpenRouter API 기본 URL
        """
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.base_url = base_url
        
        if not self.api_key:
            logger.warning("⚠️  OpenRouter API 키가 설정되지 않았습니다.")
        
        self.client = httpx.AsyncClient(timeout=60.0)
        
        # 추천 모델 목록
        self.models = {
            "claude": "anthropic/claude-3.5-sonnet",  # 고품질, 빠름
            "gpt4": "openai/gpt-4o",                   # 최신 GPT-4
            "gpt4-mini": "openai/gpt-4o-mini",         # 경제적
            "llama": "meta-llama/llama-3.3-70b-instruct",  # 오픈소스
            "free": "google/gemini-2.0-flash-exp:free"  # 무료 (테스트용)
        }
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt4-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> Dict:
        """
        채팅 완성 API 호출
        
        Args:
            messages: 대화 메시지 리스트 [{"role": "user", "content": "..."}]
            model: 모델 이름 (claude, gpt4, gpt4-mini, llama, free)
            temperature: 창의성 (0.0~1.0)
            max_tokens: 최대 토큰 수
            stream: 스트리밍 여부
            
        Returns:
            Dict: API 응답
        """
        if not self.api_key:
            raise ValueError("OpenRouter API 키가 설정되지 않았습니다.")
        
        # 모델 이름 매핑
        model_id = self.models.get(model, model)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/yourusername/Pawna",  # 선택
            "X-Title": "Pawna Chatbot"  # 선택
        }
        
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        try:
            logger.info(f"🤖 OpenRouter API 호출: {model_id}")
            
            if stream:
                # 스트리밍은 별도 메서드로
                return await self._stream_completion(headers, payload)
            else:
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ OpenRouter API 오류: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ OpenRouter API 호출 실패: {e}")
            raise
    
    async def _stream_completion(
        self,
        headers: Dict,
        payload: Dict
    ) -> AsyncGenerator[str, None]:
        """
        스트리밍 응답 처리
        """
        async with self.client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    yield line[6:]  # "data: " 제거
    
    def format_messages(
        self,
        system_prompt: str,
        user_message: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> List[Dict[str, str]]:
        """
        OpenRouter 메시지 형식으로 포맷팅
        
        Args:
            system_prompt: 시스템 프롬프트
            user_message: 사용자 메시지
            context: RAG 컨텍스트 (선택)
            conversation_history: 대화 히스토리 (선택)
            
        Returns:
            List[Dict]: OpenRouter 메시지 형식
        """
        messages = []
        
        # 1. 시스템 프롬프트
        full_system_prompt = system_prompt
        if context:
            full_system_prompt += f"\n\n# 참고 정보\n{context}"
        
        messages.append({
            "role": "system",
            "content": full_system_prompt
        })
        
        # 2. 대화 히스토리 (있으면)
        if conversation_history:
            messages.extend(conversation_history[-5:])  # 최근 5개만
        
        # 3. 현재 사용자 메시지
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    async def close(self):
        """클라이언트 종료"""
        await self.client.aclose()


# 전역 OpenRouter 클라이언트
_openrouter_client: Optional[OpenRouterClient] = None


def get_openrouter_client() -> OpenRouterClient:
    """OpenRouter 클라이언트 싱글톤 인스턴스 반환"""
    global _openrouter_client
    if _openrouter_client is None:
        _openrouter_client = OpenRouterClient()
    return _openrouter_client
