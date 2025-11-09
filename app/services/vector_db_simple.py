"""
간단한 파일 기반 벡터 DB (Milvus Lite 대안)
NumPy와 Pickle을 사용한 경량 벡터 검색 시스템
"""
import pickle
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SimpleVectorDB:
    """
    파일 기반 간단한 벡터 데이터베이스
    Windows 환경에서 Milvus Lite 설치 이슈를 회피
    """
    
    def __init__(self, db_path: str = "data/processed/vector_db.pkl"):
        """
        Args:
            db_path: 벡터 DB 저장 경로
        """
        self.db_path = Path(db_path)
        self.documents: List[Dict] = []
        self.embeddings: Optional[np.ndarray] = None
        
    def save(self):
        """벡터 DB를 파일로 저장"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "documents": self.documents,
            "embeddings": self.embeddings
        }
        
        with open(self.db_path, 'wb') as f:
            pickle.dump(data, f)
        
        logger.info(f"✅ 벡터 DB 저장 완료: {self.db_path}")
    
    def load(self):
        """벡터 DB를 파일에서 로드"""
        if not self.db_path.exists():
            logger.warning(f"⚠️  벡터 DB 파일을 찾을 수 없습니다: {self.db_path}")
            return False
        
        with open(self.db_path, 'rb') as f:
            data = pickle.load(f)
        
        self.documents = data["documents"]
        self.embeddings = data["embeddings"]
        
        logger.info(f"✅ 벡터 DB 로드 완료: {len(self.documents)}개 문서")
        return True
    
    def insert_documents(self, documents: List[Dict], embeddings: np.ndarray):
        """
        문서와 임베딩을 DB에 삽입
        
        Args:
            documents: 문서 리스트
            embeddings: 임베딩 배열 (N x D)
        """
        self.documents = documents
        self.embeddings = embeddings
        
        logger.info(f"📥 {len(documents)}개 문서 삽입 완료")
        self.save()
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        dbti_filter: Optional[str] = None,
        min_score: float = 0.0
    ) -> List[Dict]:
        """
        코사인 유사도 기반 벡터 검색
        
        Args:
            query_embedding: 쿼리 임베딩 벡터
            top_k: 반환할 결과 개수
            dbti_filter: DBTI 코드로 필터링
            min_score: 최소 유사도 점수
            
        Returns:
            List[Dict]: 검색 결과 (유사도 순)
        """
        if self.embeddings is None or len(self.documents) == 0:
            logger.warning("⚠️  벡터 DB가 비어있습니다.")
            return []
        
        # 쿼리 벡터 정규화
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        
        # 모든 문서 벡터 정규화
        embeddings_norm = self.embeddings / np.linalg.norm(
            self.embeddings, axis=1, keepdims=True
        )
        
        # 코사인 유사도 계산 (내적)
        similarities = np.dot(embeddings_norm, query_norm)
        
        # DBTI 필터링
        if dbti_filter:
            filtered_indices = [
                i for i, doc in enumerate(self.documents)
                if doc.get('dbti_code') == dbti_filter
            ]
            if filtered_indices:
                filtered_similarities = similarities[filtered_indices]
                filtered_documents = [self.documents[i] for i in filtered_indices]
            else:
                return []
        else:
            filtered_similarities = similarities
            filtered_documents = self.documents
        
        # Top-K 추출
        top_indices = np.argsort(filtered_similarities)[::-1][:top_k]
        
        # 결과 생성
        results = []
        for idx in top_indices:
            score = float(filtered_similarities[idx])
            if score >= min_score:
                doc = filtered_documents[idx].copy()
                doc['score'] = score
                results.append(doc)
        
        return results
    
    def get_stats(self) -> Dict:
        """통계 정보 반환"""
        return {
            "num_documents": len(self.documents),
            "embedding_dim": self.embeddings.shape[1] if self.embeddings is not None else 0,
            "db_path": str(self.db_path)
        }


# 전역 벡터 DB 인스턴스
_simple_vector_db: Optional[SimpleVectorDB] = None


def get_simple_vector_db() -> SimpleVectorDB:
    """간단한 벡터 DB 싱글톤 인스턴스 반환"""
    global _simple_vector_db
    if _simple_vector_db is None:
        _simple_vector_db = SimpleVectorDB()
        _simple_vector_db.load()  # 저장된 DB 로드 시도
    return _simple_vector_db

