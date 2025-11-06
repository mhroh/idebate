// 데이터베이스 타입 정의

export interface Student {
  id: string
  name: string
  class: string | null
  created_at: string
  last_active: string
}

export interface Session {
  id: string
  student_id: string
  started_at: string
  ended_at: string | null
  status: 'active' | 'ended' | 'error'
  summary: string | null
  grade: string | null
  total_tokens: number
}

export interface Message {
  id: string
  session_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  tokens_used: number
  created_at: string
}

export interface ConfigCache {
  id: number
  config_key: string
  config_value: string
  updated_at: string
}

// Google Sheets에서 가져오는 설정 타입
export interface ChatConfig {
  serviceOnOff: 'on' | 'off'
  model: string
  max_tokens: number
  temperature: number
  system: string
  a_p: string  // 종합 평가 프롬프트
  e_p: string  // 평어 프롬프트
}
