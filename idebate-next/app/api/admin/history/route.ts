import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase/client'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const sessionId = searchParams.get('sessionId')
    const studentName = searchParams.get('studentName')

    if (!sessionId && !studentName) {
      return NextResponse.json(
        { error: 'sessionId 또는 studentName이 필요합니다.' },
        { status: 400 }
      )
    }

    let query = supabase
      .from('sessions')
      .select(`
        id,
        started_at,
        ended_at,
        status,
        total_tokens,
        summary,
        grade,
        students (id, name, class)
      `)

    if (sessionId) {
      query = query.eq('id', sessionId)
    } else if (studentName) {
      // 학생 이름으로 검색
      const { data: student } = await supabase
        .from('students')
        .select('id')
        .eq('name', studentName)
        .single()

      if (!student) {
        return NextResponse.json(
          { error: '학생을 찾을 수 없습니다.' },
          { status: 404 }
        )
      }

      query = query.eq('student_id', student.id)
    }

    const { data: sessions, error } = await query.order('started_at', { ascending: false })

    if (error) throw error

    // 각 세션의 메시지 가져오기
    const sessionsWithMessages = await Promise.all(
      sessions.map(async (session) => {
        const { data: messages } = await supabase
          .from('messages')
          .select('role, content, tokens_used, created_at')
          .eq('session_id', session.id)
          .order('created_at', { ascending: true })

        return {
          ...session,
          messages: messages || [],
        }
      })
    )

    return NextResponse.json({
      sessions: sessionsWithMessages,
    })
  } catch (error: any) {
    console.error('History API Error:', error)
    return NextResponse.json(
      { error: error.message || '히스토리 조회 실패' },
      { status: 500 }
    )
  }
}
