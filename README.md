# 🐾 Pawsonality - Dog Personality Test

**Pawsonality**는 강아지의 성격 유형을 분석하고 AI 챗봇과 대화할 수 있는 웹 서비스입니다.

## 🌟 주요 기능

- 🐕 **16가지 Dog Personality 유형 테스트** - 12개 질문으로 강아지의 성격 파악
- 🤖 **AI 챗봇 상담** - RAG + OpenRouter LLM 기반 맞춤형 양육 조언
- 💕 **MBTI 매칭** - 내 MBTI와 잘 맞는 강아지 유형 추천
- 📊 **성격 분석 리포트** - 유형별 특성, 양육 팁, 궁합 정보 제공

## 🛠️ 기술 스택

### Backend

- **FastAPI** - 고성능 비동기 Python 웹 프레임워크
- **Pydantic** - 데이터 검증 및 직렬화
- **OpenRouter API** - Gemma 3 LLM 지원
- **Sentence Transformers** - 의미론적 임베딩 생성
- **NumPy/Pickle** - 간단한 벡터 DB (파일 기반)

### Frontend

- **React 19** - 최신 React
- **TypeScript** - 타입 안전성
- **Vite 7** - 빠른 빌드 도구
- **TanStack Query** - 서버 상태 관리
- **Tailwind CSS v4** - 유틸리티 기반 CSS
- **React Router 6** - 클라이언트 사이드 라우팅

## 📁 프로젝트 구조

```
Pawsonality/
├── app/                      # Backend (FastAPI)
│   ├── config.py            # 설정 관리
│   ├── main.py              # FastAPI 앱
│   ├── models/              # Pydantic 모델
│   │   ├── pawna.py         # Pawna 모델
│   │   ├── chat.py         # 챗봇 모델
│   │   └── mbti.py         # MBTI 모델
│   ├── routers/             # API 라우터
│   │   ├── pawna.py         # Pawna API
│   │   ├── chat.py         # 챗봇 API
│   │   └── mbti.py         # MBTI API
│   ├── services/            # 비즈니스 로직
│   │   ├── embeddings.py   # 임베딩 생성
│   │   ├── vector_db_simple.py  # 벡터 DB
│   │   ├── rag_simple.py   # RAG 서비스
│   │   ├── openrouter.py   # LLM 클라이언트
│   │   └── prompts.py      # 프롬프트 템플릿
│   └── data/                # 데이터 로더
│       └── pawna_data.py
│
├── src/                     # Frontend (React)
│   ├── components/          # UI 컴포넌트
│   │   └── ui/             # 재사용 가능한 UI
│   ├── pages/               # 페이지 컴포넌트
│   │   ├── HomePage.tsx
│   │   ├── PawnaTestPage.tsx
│   │   ├── PawnaResultPage.tsx
│   │   ├── ChatbotPage.tsx
│   │   └── MBTIMatchPage.tsx
│   ├── services/            # API 클라이언트
│   │   └── api.ts
│   ├── App.tsx             # 메인 앱
│   └── main.tsx            # 엔트리 포인트
│
├── data/                    # 데이터 파일
│   ├── raw/                # 원본 CSV 데이터
│   └── processed/          # 처리된 JSON 및 벡터 DB
│
├── scripts/                 # 유틸리티 스크립트
│   ├── migrate_pawna_to_pawna.py  # 데이터 마이그레이션
│   └── setup_vectordb_simple.py  # 벡터 DB 초기화
│
├── run_server.py           # Backend 실행 스크립트
├── requirements.txt        # Python 의존성
└── package.json            # Node.js 의존성
```

## 🔄 API 엔드포인트

### Pawsonality API (`/api/pawna`)

- `GET /api/pawna/questions` - 12개 질문 조회
- `POST /api/pawna/submit` - 답변 제출 및 결과 받기
- `GET /api/pawna/types/{pawna_code}` - 특정 유형 정보 조회

### Chatbot API (`/api/chat`)

- `POST /api/chat/` - 챗봇 메시지 전송 (RAG + LLM)

### MBTI API (`/api/mbti`)

- `POST /api/mbti/match` - MBTI 기반 강아지 추천

## 📦 설치 및 실행

### 1. 환경 변수 설정

```bash
cp env.example .env
```

`.env` 파일을 열어 필요한 값을 설정:

```env
# Server
DEBUG=True
HOST=0.0.0.0
PORT=8000

# OpenRouter API
OPENROUTER_API_KEY=your-api-key-here
OPENROUTER_MODEL=gpt4-mini

# CORS (개발 환경)
CORS_ORIGINS=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://localhost:5177"]
```

### 2. Backend 설치 및 실행

```bash
# Python 가상 환경 생성
python -m venv venv

# 가상 환경 활성화 (Windows)
venv\Scripts\activate

# 가상 환경 활성화 (Mac/Linux)
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 백엔드 서버 실행
python run_server.py
```

Backend는 `http://localhost:8000`에서 실행됩니다.

- API 문서: `http://localhost:8000/docs`

### 3. Frontend 설치 및 실행

```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

Frontend는 `http://localhost:5173`에서 실행됩니다.

## 🧪 개발 팁

### Backend 재시작

```bash
# 자동 리로드 모드로 실행 (코드 변경 시 자동 재시작)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 벡터 DB 재생성

데이터를 수정한 경우:

```bash
python scripts/setup_vectordb.py
```

### Frontend 빌드

```bash
npm run build
npm run preview  # 빌드 결과 미리보기
```

## 📝 라이선스

이 프로젝트는 개인 학습 및 포트폴리오 용도로 제작되었습니다.

## 👤 작성자

**DBTI → Pawsonality Migration**

- FastAPI + React 마이그레이션
- RAG + OpenRouter 통합
- 최신 기술 스택 적용
- 완전한 프로젝트 리브랜딩

---

© 2025 Pawsonality - Dog Personality Test
