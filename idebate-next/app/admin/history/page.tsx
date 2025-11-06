'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'

interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  tokens_used: number
  created_at: string
}

interface Session {
  id: string
  started_at: string
  ended_at: string | null
  status: string
  total_tokens: number
  summary: string | null
  grade: string | null
  students: { id: string; name: string; class: string | null }
  messages: Message[]
}

export default function HistoryPage() {
  const searchParams = useSearchParams()
  const studentName = searchParams.get('student')

  const [sessions, setSessions] = useState<Session[]>([])
  const [selectedSession, setSelectedSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (studentName) {
      fetchHistory()
    }
  }, [studentName])

  const fetchHistory = async () => {
    try {
      const res = await fetch(`/api/admin/history?studentName=${encodeURIComponent(studentName!)}`)
      const data = await res.json()
      if (res.ok) {
        setSessions(data.sessions)
        if (data.sessions.length > 0) {
          setSelectedSession(data.sessions[0])
        }
      }
    } catch (error) {
      console.error('Failed to fetch history:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ko-KR')
  }

  const formatDuration = (start: string, end: string | null) => {
    if (!end) return '진행 중'
    const duration = Math.floor((new Date(end).getTime() - new Date(start).getTime()) / 1000 / 60)
    return `${duration}분`
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl text-gray-600">로딩 중...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">
              📜 {studentName}의 대화 기록
            </h1>
            <p className="text-sm text-gray-600">총 {sessions.length}개 세션</p>
          </div>
          <a
            href="/admin"
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            ← 대시보드
          </a>
        </div>
      </div>

      {sessions.length === 0 ? (
        <div className="max-w-7xl mx-auto p-6">
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="text-6xl mb-4">📭</div>
            <p className="text-xl text-gray-600">아직 대화 기록이 없습니다</p>
          </div>
        </div>
      ) : (
        <div className="max-w-7xl mx-auto p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 세션 목록 */}
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="font-semibold text-gray-800 mb-4">세션 목록</h2>
              <div className="space-y-2">
                {sessions.map((session) => (
                  <button
                    key={session.id}
                    onClick={() => setSelectedSession(session)}
                    className={`w-full text-left p-3 rounded-lg transition ${
                      selectedSession?.id === session.id
                        ? 'bg-blue-50 border-2 border-blue-500'
                        : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                  >
                    <div className="text-sm font-medium text-gray-800">
                      {formatDate(session.started_at)}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {formatDuration(session.started_at, session.ended_at)} • {session.total_tokens} 토큰
                    </div>
                    {session.status === 'active' && (
                      <span className="inline-block mt-1 text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
                        진행 중
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* 대화 내역 */}
            <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
              {selectedSession && (
                <>
                  {/* 세션 정보 */}
                  <div className="mb-6 pb-4 border-b border-gray-200">
                    <div className="flex justify-between items-start mb-2">
                      <h2 className="text-lg font-semibold text-gray-800">
                        대화 내용
                      </h2>
                      <span className="text-sm text-gray-600">
                        {selectedSession.messages.length}개 메시지
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      시작: {formatDate(selectedSession.started_at)}
                      {selectedSession.ended_at && (
                        <> • 종료: {formatDate(selectedSession.ended_at)}</>
                      )}
                    </div>
                  </div>

                  {/* 평가 정보 */}
                  {(selectedSession.summary || selectedSession.grade) && (
                    <div className="mb-6 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                      {selectedSession.summary && (
                        <div className="mb-3">
                          <div className="text-sm font-semibold text-gray-700 mb-1">
                            종합 평가:
                          </div>
                          <div className="text-sm text-gray-800">
                            {selectedSession.summary}
                          </div>
                        </div>
                      )}
                      {selectedSession.grade && (
                        <div>
                          <div className="text-sm font-semibold text-gray-700 mb-1">
                            평어:
                          </div>
                          <div className="text-sm text-gray-800">
                            {selectedSession.grade}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* 메시지 목록 */}
                  <div className="space-y-4 max-h-[600px] overflow-y-auto">
                    {selectedSession.messages
                      .filter((msg) => msg.role !== 'system')
                      .map((msg, idx) => (
                        <div
                          key={idx}
                          className={`flex ${
                            msg.role === 'user' ? 'justify-end' : 'justify-start'
                          }`}
                        >
                          <div
                            className={`max-w-[80%] px-4 py-3 rounded-2xl ${
                              msg.role === 'user'
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            <div className="whitespace-pre-wrap">{msg.content}</div>
                            <div
                              className={`text-xs mt-2 ${
                                msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                              }`}
                            >
                              {new Date(msg.created_at).toLocaleTimeString('ko-KR')}
                              {msg.tokens_used > 0 && ` • ${msg.tokens_used} 토큰`}
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
