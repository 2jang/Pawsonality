"""
Embedding Service using Sentence Transformers
텍스트를 벡터로 변환하는 서비스
"""
from sentence_transformers import SentenceTransformer
from typing import List, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Sentence Transformers를 사용한 임베딩 생성 서비스
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Args:
            model_name: Sentence Transformers 모델 이름
        """
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self.embedding_dim = 384  # all-MiniLM-L6-v2의 차원
        
    def load_model(self):
        """모델 로드 (lazy loading)"""
        if self.model is None:
            logger.info(f"📥 임베딩 모델 로드 중: {self.model_name}")
            try:
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"✅ 임베딩 모델 로드 완료 (차원: {self.embedding_dim})")
            except Exception as e:
                logger.error(f"❌ 임베딩 모델 로드 실패: {e}")
                raise
    
    def encode_text(self, text: str) -> np.ndarray:
        """
        단일 텍스트를 벡터로 변환
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            np.ndarray: 임베딩 벡터 (384차원)
        """
        if self.model is None:
            self.load_model()
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        여러 텍스트를 배치로 벡터 변환 (효율적)
        
        Args:
            texts: 임베딩할 텍스트 리스트
            batch_size: 배치 크기
            
        Returns:
            np.ndarray: 임베딩 벡터 배열 (N x 384)
        """
        if self.model is None:
            self.load_model()
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 100
        )
        return embeddings
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        두 텍스트 간의 유사도 계산 (코사인 유사도)
        
        Args:
            text1: 첫 번째 텍스트
            text2: 두 번째 텍스트
            
        Returns:
            float: 유사도 (0~1)
        """
        emb1 = self.encode_text(text1)
        emb2 = self.encode_text(text2)
        
        # 코사인 유사도 계산
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)


# 전역 임베딩 서비스 인스턴스
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> EmbeddingService:
    """
    임베딩 서비스 싱글톤 인스턴스 반환
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService(model_name)
    return _embedding_service

