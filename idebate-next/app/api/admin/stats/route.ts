import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase/client'

export async function GET(request: NextRequest) {
  try {
    // 1. 활성 세션 수 (현재 대화 중인 학생)
    const { count: activeSessions } = await supabase
      .from('sessions')
      .select('*', { count: 'exact', head: true })
      .eq('status', 'active')

    // 2. 오늘 총 세션 수
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const { count: todaySessions } = await supabase
      .from('sessions')
      .select('*', { count: 'exact', head: true })
      .gte('started_at', today.toISOString())

    // 3. 총 학생 수
    const { count: totalStudents } = await supabase
      .from('students')
      .select('*', { count: 'exact', head: true })

    // 4. 오늘 총 메시지 수
    const { count: todayMessages } = await supabase
      .from('messages')
      .select('*', { count: 'exact', head: true })
      .gte('created_at', today.toISOString())

    // 5. 오늘 토큰 사용량
    const { data: tokenData } = await supabase
      .from('messages')
      .select('tokens_used')
      .gte('created_at', today.toISOString())

    const todayTokens = tokenData?.reduce((sum, msg) => sum + (msg.tokens_used || 0), 0) || 0

    // 6. 최근 활동 학생 (최근 10명)
    const { data: recentStudents } = await supabase
      .from('students')
      .select('name, last_active')
      .order('last_active', { ascending: false })
      .limit(10)

    // 7. 활성 세션 상세 정보
    const { data: activeSessionsDetail } = await supabase
      .from('sessions')
      .select(`
        id,
        started_at,
        total_tokens,
        students (name, class)
      `)
      .eq('status', 'active')
      .order('started_at', { ascending: false })

    return NextResponse.json({
      stats: {
        activeSessions: activeSessions || 0,
        todaySessions: todaySessions || 0,
        totalStudents: totalStudents || 0,
        todayMessages: todayMessages || 0,
        todayTokens,
      },
      recentStudents: recentStudents || [],
      activeSessions: activeSessionsDetail || [],
    })
  } catch (error: any) {
    console.error('Admin Stats Error:', error)
    return NextResponse.json(
      { error: error.message || '통계 조회 실패' },
      { status: 500 }
    )
  }
}
