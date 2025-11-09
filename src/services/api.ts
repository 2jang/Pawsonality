/**
 * API Client for DBTI Backend
 * FastAPI 백엔드와 통신하는 API 클라이언트
 */
import axios from 'axios'

// API Base URL (환경 변수로 관리)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Axios 인스턴스 생성
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 요청 인터셉터
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

// 응답 인터셉터
apiClient.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, response.status)
    return response
  },
  (error) => {
    console.error('[API Response Error]', error.response?.status, error.response?.data)
    return Promise.reject(error)
  }
)

// ===== API Types =====

export interface DBTIQuestion {
  id: number
  title: string
  type: string
  option_a: string
  option_b: string
}

export interface DBTIAnswer {
  question_id: number
  selected: string
}

export interface DBTISubmission {
  answers: DBTIAnswer[]
}

export interface DBTIResult {
  dbti_code: string
  dbti_type?: string  // Backend 호환
  mbti_type?: string  // Backend 호환
  type_name: string
  description: string
  solution?: string   // Backend 호환
  personality_traits: string[]
  care_tips?: string[]
  compatibility?: {
    best_match: string[]
    good_match: string[]
  }
  image_url?: string
  site_url?: string
  timestamp?: string
}

export interface ChatRequest {
  message: string
  dbti_type?: string
  conversation_history?: Array<{ role: string; content: string }>
}

export interface ChatResponse {
  message: string
  sources: string[]
  confidence: number
  timestamp: string
}

export interface MBTIRequest {
  mbti: string
}

export interface MBTIDogMatch {
  dbti_code: string
  type_name: string
  match_score: number
  compatibility_reason: string
}

export interface MBTIResponse {
  mbti: string
  mbti_type_name: string
  mbti_description: string
  recommended_dogs: MBTIDogMatch[]
  care_tips: string[]
}

// ===== API Functions =====

/**
 * DBTI 질문 목록 조회
 */
export const getDBTIQuestions = async (): Promise<DBTIQuestion[]> => {
  const response = await apiClient.get<DBTIQuestion[]>('/api/dbti/questions')
  return response.data
}

/**
 * DBTI 테스트 제출 및 결과 조회
 */
export const submitDBTI = async (submission: DBTISubmission): Promise<DBTIResult> => {
  const response = await apiClient.post<DBTIResult>('/api/dbti/submit', submission)
  return response.data
}

/**
 * DBTI 유형 정보 조회
 */
export const getDBTIType = async (code: string): Promise<DBTIResult> => {
  const response = await apiClient.get<DBTIResult>(`/api/dbti/types/${code}`)
  return response.data
}

/**
 * 챗봇 메시지 전송
 */
export const sendChatMessage = async (request: ChatRequest): Promise<ChatResponse> => {
  const response = await apiClient.post<ChatResponse>('/api/chat/', request)
  return response.data
}

/**
 * MBTI 기반 강아지 매칭
 */
export const getMBTIMatch = async (request: MBTIRequest): Promise<MBTIResponse> => {
  const response = await apiClient.post<MBTIResponse>('/api/mbti/match', request)
  return response.data
}

/**
 * API 정보 조회
 */
export const getAPIInfo = async () => {
  const response = await apiClient.get('/info')
  return response.data
}

/**
 * 헬스 체크
 */
export const healthCheck = async () => {
  const response = await apiClient.get('/health')
  return response.data
}

