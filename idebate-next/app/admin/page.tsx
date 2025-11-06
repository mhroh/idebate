'use client'

import { useState, useEffect } from 'react'

interface Stats {
  activeSessions: number
  todaySessions: number
  totalStudents: number
  todayMessages: number
  todayTokens: number
}

interface RecentStudent {
  name: string
  last_active: string
}

interface ActiveSession {
  id: string
  started_at: string
  total_tokens: number
  students: { name: string; class: string | null }
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [recentStudents, setRecentStudents] = useState<RecentStudent[]>([])
  const [activeSessions, setActiveSessions] = useState<ActiveSession[]>([])
  const [loading, setLoading] = useState(true)
  const [searchName, setSearchName] = useState('')

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 5000) // 5초마다 갱신
    return () => clearInterval(interval)
  }, [])

  const fetchStats = async () => {
    try {
      const res = await fetch('/api/admin/stats')
      const data = await res.json()
      if (res.ok) {
        setStats(data.stats)
        setRecentStudents(data.recentStudents)
        setActiveSessions(data.activeSessions)
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const searchHistory = async () => {
    if (!searchName.trim()) return
    window.location.href = `/admin/history?student=${encodeURIComponent(searchName)}`
  }

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000 / 60)

    if (diff < 1) return '방금 전'
    if (diff < 60) return `${diff}분 전`
    if (diff < 1440) return `${Math.floor(diff / 60)}시간 전`
    return date.toLocaleDateString('ko-KR')
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
            <h1 className="text-2xl font-bold text-gray-800">📊 iDebate 관리자</h1>
            <p className="text-sm text-gray-600">실시간 모니터링 대시보드</p>
          </div>
          <a
            href="/"
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            학생 페이지로
          </a>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">현재 대화 중</div>
            <div className="text-3xl font-bold text-green-600 mt-2">
              {stats?.activeSessions}명
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">오늘 세션</div>
            <div className="text-3xl font-bold text-blue-600 mt-2">
              {stats?.todaySessions}개
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">총 학생 수</div>
            <div className="text-3xl font-bold text-purple-600 mt-2">
              {stats?.totalStudents}명
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">오늘 메시지</div>
            <div className="text-3xl font-bold text-orange-600 mt-2">
              {stats?.todayMessages}개
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">오늘 토큰</div>
            <div className="text-2xl font-bold text-red-600 mt-2">
              {stats?.todayTokens.toLocaleString()}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 현재 활성 세션 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              🟢 현재 대화 중인 학생
            </h2>
            {activeSessions.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                현재 대화 중인 학생이 없습니다
              </p>
            ) : (
              <div className="space-y-3">
                {activeSessions.map((session) => (
                  <div
                    key={session.id}
                    className="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <div className="font-medium text-gray-800">
                        {session.students.name}
                      </div>
                      <div className="text-xs text-gray-500">
                        {session.students.class || '반 정보 없음'} • {formatTime(session.started_at)}
                      </div>
                    </div>
                    <div className="text-sm text-gray-600">
                      {session.total_tokens.toLocaleString()} 토큰
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 최근 활동 학생 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              ⏱️ 최근 활동 학생
            </h2>
            <div className="space-y-3">
              {recentStudents.map((student, idx) => (
                <div
                  key={idx}
                  className="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
                >
                  <div className="font-medium text-gray-800">{student.name}</div>
                  <div className="text-sm text-gray-500">
                    {formatTime(student.last_active)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 학생 검색 */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            🔍 학생 대화 내역 조회
          </h2>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="학생 이름 입력..."
              value={searchName}
              onChange={(e) => setSearchName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && searchHistory()}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
            <button
              onClick={searchHistory}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2 rounded-lg transition"
            >
              검색
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
