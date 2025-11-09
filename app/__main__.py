"""
Entry point for running the app package directly
python -m app 으로 실행 가능
"""
import uvicorn
from .config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )

