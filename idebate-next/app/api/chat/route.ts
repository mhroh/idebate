import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase/client'
import { sendMessage } from '@/lib/claude/client'
import { getConfig } from '@/lib/google-sheets/client'

export async function POST(request: NextRequest) {
  try {
    const { sessionId, message } = await request.json()

    if (!sessionId || !message) {
      return NextResponse.json(
        { error: 'sessionId와 message는 필수입니다.' },
        { status: 400 }
      )
    }

    // 1. 설정 정보 가져오기 (캐싱됨)
    const config = await getConfig()

    if (config.serviceOnOff === 'off') {
      return NextResponse.json(
        { error: '현재 서비스가 중지되었습니다.' },
        { status: 503 }
      )
    }

    // 2. 세션 확인
    const { data: session, error: sessionError } = await supabase
      .from('sessions')
      .select('*')
      .eq('id', sessionId)
      .eq('status', 'active')
      .single()

    if (sessionError || !session) {
      return NextResponse.json(
        { error: '유효하지 않은 세션입니다.' },
        { status: 404 }
      )
    }

    // 3. 사용자 메시지 저장
    await supabase.from('messages').insert({
      session_id: sessionId,
      role: 'user',
      content: message,
      tokens_used: 0,
    })

    // 4. 대화 히스토리 가져오기 (최근 50개)
    const { data: history } = await supabase
      .from('messages')
      .select('role, content')
      .eq('session_id', sessionId)
      .order('created_at', { ascending: true })
      .limit(50)

    const messages = (history || [])
      .filter((m) => m.role !== 'system')
      .map((m) => ({
        role: m.role as 'user' | 'assistant',
        content: m.content,
      }))

    // 5. Claude API 호출
    const response = await sendMessage(messages, config.system, {
      model: config.model,
      max_tokens: config.max_tokens,
      temperature: config.temperature,
    })

    // 6. AI 응답 저장
    await supabase.from('messages').insert({
      session_id: sessionId,
      role: 'assistant',
      content: response.content,
      tokens_used: response.tokens,
    })

    // 7. 세션 토큰 업데이트
    await supabase
      .from('sessions')
      .update({
        total_tokens: session.total_tokens + response.tokens,
      })
      .eq('id', sessionId)

    return NextResponse.json({
      response: response.content,
      tokens: response.tokens,
      usage: response.usage,
    })
  } catch (error: any) {
    console.error('Chat API Error:', error)
    return NextResponse.json(
      { error: error.message || '서버 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}
