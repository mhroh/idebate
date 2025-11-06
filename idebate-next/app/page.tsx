'use client'

import { useState, useEffect, useRef } from 'react'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [studentName, setStudentName] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [evaluating, setEvaluating] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const startSession = async () => {
    if (!studentName.trim()) {
      alert('대화명을 입력해주세요!')
      return
    }

    try {
      setLoading(true)
      const res = await fetch('/api/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ studentName }),
      })

      const data = await res.json()
      if (res.ok) {
        setSessionId(data.sessionId)
      } else {
        alert(data.error || '세션 생성 실패')
      }
    } catch (error) {
      alert('서버 연결 실패')
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || !sessionId) return

    const userMessage = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId,
          message: userMessage,
        }),
      })

      const data = await res.json()
      if (res.ok) {
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: data.response },
        ])
      } else {
        alert(data.error || '메시지 전송 실패')
      }
    } catch (error) {
      alert('서버 연결 실패')
    } finally {
      setLoading(false)
    }
  }

  const endConversation = async () => {
    if (!sessionId) return

    if (!confirm('대화를 종료하고 평가를 받으시겠습니까?')) return

    setEvaluating(true)

    try {
      // 세션 종료
      await fetch('/api/session', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId }),
      })

      // 평가 생성
      const res = await fetch('/api/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId }),
      })

      const data = await res.json()
      if (res.ok) {
        alert(`평가 완료!\n\n종합평가: ${data.summary}\n\n평어: ${data.grade}`)
        setSessionId(null)
        setMessages([])
        setStudentName('')
      } else {
        alert(data.error || '평가 생성 실패')
      }
    } catch (error) {
      alert('서버 연결 실패')
    } finally {
      setEvaluating(false)
    }
  }

  if (!sessionId) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
          <h1 className="text-3xl font-bold text-gray-800 mb-2 text-center">
            🎓 iDebate
          </h1>
          <p className="text-gray-600 mb-6 text-center">
            AI 토론 튜터와 함께 논술 실력을 키워보세요
          </p>
          <input
            type="text"
            placeholder="대화명을 입력하세요"
            value={studentName}
            onChange={(e) => setStudentName(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && startSession()}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none mb-4"
          />
          <button
            onClick={startSession}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '시작 중...' : '대화 시작하기'}
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* 헤더 */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-xl font-bold text-gray-800">iDebate</h1>
            <p className="text-sm text-gray-600">{studentName}</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={endConversation}
              disabled={evaluating}
              className="text-sm bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium disabled:opacity-50"
            >
              {evaluating ? '평가 중...' : '📝 평가 받기'}
            </button>
            <button
              onClick={() => {
                if (confirm('평가 없이 종료하시겠습니까?')) {
                  setSessionId(null)
                  setMessages([])
                  setStudentName('')
                }
              }}
              className="text-sm text-red-600 hover:text-red-700 font-medium"
            >
              종료
            </button>
          </div>
        </div>
      </div>

      {/* 메시지 영역 */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-20">
              <p className="text-lg">안녕하세요! 무엇을 도와드릴까요?</p>
            </div>
          )}
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[70%] px-4 py-3 rounded-2xl ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-gray-200 text-gray-800'
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 px-4 py-3 rounded-2xl">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* 입력 영역 */}
      <div className="bg-white border-t border-gray-200 p-6">
        <div className="max-w-4xl mx-auto flex gap-2">
          <input
            type="text"
            placeholder="메시지를 입력하세요..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !loading && !evaluating && sendMessage()}
            disabled={loading || evaluating}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:opacity-50"
          />
          <button
            onClick={sendMessage}
            disabled={loading || evaluating || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            전송
          </button>
        </div>
      </div>
    </div>
  )
}
