# 🔧 .env 파일 업데이트 필요!

## ❌ CORS 에러 발생 중

Frontend가 `http://localhost:5176`에서 실행되고 있지만, Backend CORS 설정에 이 포트가 없습니다.

**에러 메시지:**
```
Access to XMLHttpRequest at 'http://localhost:8000/api/dbti/questions' 
from origin 'http://localhost:5176' has been blocked by CORS policy
```

---

## ✅ 해결 방법

### 1. `.env` 파일 수정

프로젝트 루트의 `.env` 파일을 열어서 `CORS_ORIGINS`를 수정하세요:

```env
# 기존 (5176 포트 없음)
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# 수정 후 (5173-5177 범위 추가)
CORS_ORIGINS=["http://localhost:5173","http://localhost:5174","http://localhost:5175","http://localhost:5176","http://localhost:5177","http://localhost:3000"]
```

### 2. Backend 서버 재시작

```bash
# Ctrl+C로 기존 서버 종료 후
python run_server.py
```

---

## 🔍 왜 이런 일이 발생했나?

Vite 개발 서버는 포트가 이미 사용 중이면 **자동으로 다음 포트**를 찾습니다:
- 5173 사용 중 → 5174 시도
- 5174 사용 중 → 5175 시도
- 5175 사용 중 → **5176 사용** ✅

따라서 개발 환경에서는 **여러 포트를 미리 허용**해야 합니다.

---

## 💡 더 나은 방법 (선택사항)

개발 환경에서만 **모든 localhost 허용**:

### app/config.py 수정 (개발 전용)
```python
# DEBUG 모드일 때만 모든 localhost 허용
if DEBUG and "localhost" in CORS_ORIGINS[0]:
    CORS_ORIGINS = ["http://localhost:*"]  # 모든 포트 허용
```

하지만 보안을 위해 **명시적으로 포트를 나열**하는 것이 더 좋습니다.

---

## ⚠️ 주의사항

1. `.env` 파일은 Git에 커밋하지 마세요 (`.gitignore`에 포함됨)
2. 프로덕션 환경에서는 정확한 도메인만 허용하세요
3. CORS 설정은 JSON 배열 형식이어야 합니다

---

**지금 바로 `.env` 파일을 수정하고 Backend 서버를 재시작하세요!** 🚀

