"""
Milvus Lite Vector Database Service
경량 벡터 DB를 사용한 의미 기반 검색
"""
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)
from typing import List, Dict, Optional
import logging
logger = logging.getLogger(__name__)


class VectorDBService:
    """
    Milvus Lite를 사용한 벡터 데이터베이스 서비스
    """
    
    def __init__(
        self,
        collection_name: str = "pawna_knowledge",
        dim: int = 384,
        db_file: str = "./milvus_pawna.db"
    ):
        """
        Args:
            collection_name: 컬렉션 이름
            dim: 임베딩 벡터 차원 (all-MiniLM-L6-v2 = 384)
            db_file: Milvus Lite DB 파일 경로
        """
        self.collection_name = collection_name
        self.dim = dim
        self.db_file = db_file
        self.collection: Optional[Collection] = None
        
    def connect(self):
        """Milvus Lite 연결"""
        try:
            logger.info("📡 Milvus Lite 연결 중...")
            connections.connect(
                alias="default",
                uri=self.db_file
            )
            logger.info(f"✅ Milvus Lite 연결 완료: {self.db_file}")
        except Exception as e:
            logger.error(f"❌ Milvus Lite 연결 실패: {e}")
            raise
    
    def create_collection(self):
        """
        컬렉션 생성 (이미 존재하면 로드)
        """
        # 연결 확인
        if not connections.has_connection("default"):
            self.connect()
        
        # 컬렉션이 이미 존재하는지 확인
        if utility.has_collection(self.collection_name):
            logger.info(f"📂 기존 컬렉션 로드: {self.collection_name}")
            self.collection = Collection(self.collection_name)
            self.collection.load()
            return
        
        # 스키마 정의
        logger.info(f"🏗️  새 컬렉션 생성: {self.collection_name}")
        
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="pawna_code", dtype=DataType.VARCHAR, max_length=10),
            FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=2000),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dim)
        ]
        
        schema = CollectionSchema(
            fields=fields,
            description="Pawna Knowledge Base for RAG"
        )
        
        # 컬렉션 생성
        self.collection = Collection(
            name=self.collection_name,
            schema=schema
        )
        
        # 인덱스 생성 (벡터 검색 최적화)
        index_params = {
            "metric_type": "COSINE",  # 코사인 유사도
            "index_type": "FLAT",     # 작은 데이터셋에는 FLAT이 효율적
            "params": {}
        }
        
        self.collection.create_index(
            field_name="embedding",
            index_params=index_params
        )
        
        logger.info(f"✅ 컬렉션 생성 완료: {self.collection_name}")
    
    def insert_documents(self, documents: List[Dict], embeddings: List[List[float]]):
        """
        문서와 임베딩을 컬렉션에 삽입
        
        Args:
            documents: 문서 리스트 (id, pawna_code, category, title, content)
            embeddings: 임베딩 벡터 리스트
        """
        if self.collection is None:
            raise ValueError("컬렉션이 초기화되지 않았습니다.")
        
        # 데이터 준비
        data = [
            [doc["id"] for doc in documents],              # id
            [doc["pawna_code"] for doc in documents],       # pawna_code
            [doc["category"] for doc in documents],        # category
            [doc["title"] for doc in documents],           # title
            [doc["content"] for doc in documents],         # content
            embeddings                                      # embedding
        ]
        
        # 삽입
        logger.info(f"📥 {len(documents)}개 문서 삽입 중...")
        self.collection.insert(data)
        self.collection.flush()
        
        logger.info(f"✅ {len(documents)}개 문서 삽입 완료")
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        pawna_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        벡터 검색 수행
        
        Args:
            query_embedding: 쿼리 임베딩 벡터
            top_k: 반환할 결과 개수
            pawna_filter: Pawna 코드로 필터링 (선택)
            
        Returns:
            List[Dict]: 검색 결과 (유사도 순)
        """
        if self.collection is None:
            raise ValueError("컬렉션이 초기화되지 않았습니다.")
        
        # 컬렉션 로드 (검색 전 필수)
        self.collection.load()
        
        # 검색 파라미터
        search_params = {
            "metric_type": "COSINE",
            "params": {}
        }
        
        # 필터 표현식
        expr = None
        if pawna_filter:
            expr = f'pawna_code == "{pawna_filter}"'
        
        # 검색
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=["id", "pawna_code", "category", "title", "content"]
        )
        
        # 결과 파싱
        search_results = []
        for hits in results:
            for hit in hits:
                search_results.append({
                    "id": hit.entity.get("id"),
                    "pawna_code": hit.entity.get("pawna_code"),
                    "category": hit.entity.get("category"),
                    "title": hit.entity.get("title"),
                    "content": hit.entity.get("content"),
                    "score": float(hit.score)  # 유사도 점수
                })
        
        return search_results
    
    def get_collection_stats(self) -> Dict:
        """컬렉션 통계 조회"""
        if self.collection is None:
            return {"error": "컬렉션이 초기화되지 않았습니다."}
        
        self.collection.load()
        num_entities = self.collection.num_entities
        
        return {
            "collection_name": self.collection_name,
            "num_documents": num_entities,
            "embedding_dim": self.dim
        }
    
    def drop_collection(self):
        """컬렉션 삭제 (주의!)"""
        if utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)
            logger.info(f"🗑️  컬렉션 삭제 완료: {self.collection_name}")


# 전역 벡터 DB 서비스 인스턴스
_vector_db_service: Optional[VectorDBService] = None


def get_vector_db_service() -> VectorDBService:
    """벡터 DB 서비스 싱글톤 인스턴스 반환"""
    global _vector_db_service
    if _vector_db_service is None:
        _vector_db_service = VectorDBService()
    return _vector_db_service

