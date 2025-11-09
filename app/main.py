"""
DBTI v2 FastAPI Application
Dog Behavior Type Indicator & AI Chatbot API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import settings
from .routers import dbti, chat, mbti
import logging

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS 설정
# 개발 환경에서는 모든 localhost 허용
if settings.DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 개발 환경: 모든 origin 허용
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,  # 프로덕션: 특정 origin만 허용
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 라우터 등록
app.include_router(dbti.router, prefix="/api/dbti", tags=["DBTI"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chatbot"])
app.include_router(mbti.router, prefix="/api/mbti", tags=["MBTI"])


@app.on_event("startup")
async def startup_event():
    """
    애플리케이션 시작 시 실행
    """
    logger.info("=" * 60)
    logger.info("🐾 DBTI v2 API Starting...")
    logger.info("=" * 60)
    logger.info(f"📌 Version: {settings.VERSION}")
    logger.info(f"📌 Debug Mode: {settings.DEBUG}")
    logger.info(f"📌 CORS Origins: {settings.CORS_ORIGINS}")
    logger.info(f"📌 API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    
    # RAG 서비스 초기화
    try:
        from .services.rag_simple import get_simple_rag_service
        logger.info("🚀 RAG 서비스 초기화 중...")
        rag_service = get_simple_rag_service()
        rag_service.initialize()
        logger.info("✅ RAG 서비스 초기화 완료")
    except Exception as e:
        logger.warning(f"⚠️  RAG 서비스 초기화 실패: {e}")
        logger.warning("   벡터 DB가 없을 수 있습니다. scripts/setup_vectordb_simple.py를 실행하세요.")
    
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """
    애플리케이션 종료 시 실행
    """
    logger.info("🛑 DBTI v2 API Shutting down...")


@app.get("/", tags=["Root"])
async def root():
    """
    API 루트 엔드포인트
    """
    return {
        "message": "🐾 DBTI v2 API",
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "dbti": "/api/dbti",
            "chat": "/api/chat",
            "mbti": "/api/mbti"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    헬스 체크 엔드포인트
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
    }


@app.get("/info", tags=["Info"])
async def get_info():
    """
    API 정보 조회
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "tech_stack": {
            "framework": "FastAPI 0.118.2",
            "validation": "Pydantic 2.11.7",
            "server": "Uvicorn 0.32.0",
            "llm": "OpenRouter (GPT-4, Claude, Llama)",
            "embeddings": "sentence-transformers",
            "python": "3.14+"
        },
        "openrouter_available": bool(settings.OPENROUTER_API_KEY),
        "openrouter_model": settings.OPENROUTER_MODEL if settings.OPENROUTER_API_KEY else None
    }


# 전역 예외 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    전역 예외 처리
    """
    logger.error(f"❌ Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
        debug=True
    )

