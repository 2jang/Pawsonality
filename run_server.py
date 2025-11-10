"""
Pawna  Server Launcher
프로젝트 루트에서 서버를 실행하는 스크립트
"""
import uvicorn
from app.config import settings

if __name__ == "__main__":
    print("=" * 60)
    print("🐾 Pawna  Server Starting...")
    print("=" * 60)
    print(f"📌 Host: {settings.HOST}:{settings.PORT}")
    print(f"📌 Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"📌 Reload: {settings.RELOAD}")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )

