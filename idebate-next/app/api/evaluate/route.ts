import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase/client'
import { sendMessage } from '@/lib/claude/client'
import { getConfig, saveEvaluationToSheets } from '@/lib/google-sheets/client'

export async function POST(request: NextRequest) {
  try {
    const { sessionId } = await request.json()

    if (!sessionId) {
      return NextResponse.json(
        { error: 'sessionId가 필요합니다.' },
        { status: 400 }
      )
    }

    // 1. 세션 정보 가져오기
    const { data: session, error: sessionError } = await supabase
      .from('sessions')
      .select(`
        id,
        student_id,
        students (name)
      `)
      .eq('id', sessionId)
      .single()

    if (sessionError || !session) {
      return NextResponse.json(
        { error: '세션을 찾을 수 없습니다.' },
        { status: 404 }
      )
    }

    // 2. 대화 내역 가져오기
    const { data: messages } = await supabase
      .from('messages')
      .select('role, content')
      .eq('session_id', sessionId)
      .order('created_at', { ascending: true })

    if (!messages || messages.length === 0) {
      return NextResponse.json(
        { error: '대화 내역이 없습니다.' },
        { status: 400 }
      )
    }

    // 3. 설정 정보 가져오기 (평가 프롬프트)
    const config = await getConfig()

    // 4. 종합 평가 생성
    const evaluationMessages = [
      ...messages
        .filter((m) => m.role !== 'system')
        .map((m) => ({
          role: m.role as 'user' | 'assistant',
          content: m.content,
        })),
      {
        role: 'user' as const,
        content: config.a_p, // 종합 평가 프롬프트
      },
    ]

    const summaryResponse = await sendMessage(evaluationMessages, config.system, {
      model: config.model,
      max_tokens: config.max_tokens,
      temperature: config.temperature,
    })

    // 5. 평어 생성
    const gradeMessages = [
      ...evaluationMessages,
      {
        role: 'assistant' as const,
        content: summaryResponse.content,
      },
      {
        role: 'user' as const,
        content: config.e_p, // 평어 프롬프트
      },
    ]

    const gradeResponse = await sendMessage(gradeMessages, config.system, {
      model: config.model,
      max_tokens: config.max_tokens,
      temperature: config.temperature,
    })

    // 6. 평가 결과 저장 (Supabase)
    await supabase
      .from('sessions')
      .update({
        summary: summaryResponse.content,
        grade: gradeResponse.content,
        status: 'ended',
        ended_at: new Date().toISOString(),
      })
      .eq('id', sessionId)

    // 7. Google Sheets에도 저장
    try {
      await saveEvaluationToSheets(
        (session.students as any).name,
        summaryResponse.content,
        gradeResponse.content
      )
    } catch (sheetError) {
      console.error('Google Sheets 저장 실패:', sheetError)
      // Google Sheets 실패는 무시 (Supabase에는 저장됨)
    }

    return NextResponse.json({
      summary: summaryResponse.content,
      grade: gradeResponse.content,
      tokens: summaryResponse.tokens + gradeResponse.tokens,
    })
  } catch (error: any) {
    console.error('Evaluate API Error:', error)
    return NextResponse.json(
      { error: error.message || '평가 생성 실패' },
      { status: 500 }
    )
  }
}
