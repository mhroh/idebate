import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase/client'

export async function POST(request: NextRequest) {
  try {
    const { studentName, studentClass } = await request.json()

    if (!studentName) {
      return NextResponse.json(
        { error: '학생 이름은 필수입니다.' },
        { status: 400 }
      )
    }

    // 1. 학생 찾기 또는 생성
    let { data: student } = await supabase
      .from('students')
      .select('*')
      .eq('name', studentName)
      .single()

    if (!student) {
      const { data: newStudent, error } = await supabase
        .from('students')
        .insert({
          name: studentName,
          class: studentClass || null,
        })
        .select()
        .single()

      if (error) throw error
      student = newStudent
    }

    // 2. 새 세션 생성
    const { data: session, error: sessionError } = await supabase
      .from('sessions')
      .insert({
        student_id: student.id,
        status: 'active',
      })
      .select()
      .single()

    if (sessionError) throw sessionError

    return NextResponse.json({
      sessionId: session.id,
      studentId: student.id,
      studentName: student.name,
    })
  } catch (error: any) {
    console.error('Session API Error:', error)
    return NextResponse.json(
      { error: error.message || '서버 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}

// 세션 종료 API
export async function PUT(request: NextRequest) {
  try {
    const { sessionId } = await request.json()

    if (!sessionId) {
      return NextResponse.json(
        { error: 'sessionId는 필수입니다.' },
        { status: 400 }
      )
    }

    // 세션 종료
    await supabase
      .from('sessions')
      .update({
        status: 'ended',
        ended_at: new Date().toISOString(),
      })
      .eq('id', sessionId)

    return NextResponse.json({ success: true })
  } catch (error: any) {
    console.error('Session End Error:', error)
    return NextResponse.json(
      { error: error.message || '서버 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}
