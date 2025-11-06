import Anthropic from '@anthropic-ai/sdk'
import { Message } from '../supabase/types'

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY!,
})

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export async function sendMessage(
  messages: ChatMessage[],
  systemPrompt: string,
  config: {
    model?: string
    max_tokens?: number
    temperature?: number
  } = {}
) {
  const {
    model = 'claude-3-5-sonnet-20241022',
    max_tokens = 4096,
    temperature = 0.7,
  } = config

  try {
    // 프롬프트 캐싱 적용 (토큰 비용 90% 절감)
    const systemWithCache = [
      {
        type: 'text' as const,
        text: systemPrompt,
        cache_control: { type: 'ephemeral' as const },
      },
    ]

    const response = await anthropic.messages.create({
      model,
      max_tokens,
      temperature,
      system: systemWithCache,
      messages: messages.map((m) => ({
        role: m.role,
        content: m.content,
      })),
    })

    // 토큰 사용량 계산
    const inputTokens = response.usage.input_tokens || 0
    const outputTokens = response.usage.output_tokens || 0
    const cacheReadTokens = (response.usage as any).cache_read_input_tokens || 0
    const cacheCreationTokens = (response.usage as any).cache_creation_input_tokens || 0

    const totalTokens = inputTokens + outputTokens + cacheReadTokens + cacheCreationTokens

    return {
      content: response.content[0].type === 'text' ? response.content[0].text : '',
      tokens: totalTokens,
      usage: {
        input: inputTokens,
        output: outputTokens,
        cacheRead: cacheReadTokens,
        cacheCreation: cacheCreationTokens,
      },
    }
  } catch (error) {
    console.error('Claude API Error:', error)
    throw error
  }
}

// 스트리밍 버전 (실시간 응답용)
export async function* streamMessage(
  messages: ChatMessage[],
  systemPrompt: string,
  config: {
    model?: string
    max_tokens?: number
    temperature?: number
  } = {}
) {
  const {
    model = 'claude-3-5-sonnet-20241022',
    max_tokens = 4096,
    temperature = 0.7,
  } = config

  try {
    const systemWithCache = [
      {
        type: 'text' as const,
        text: systemPrompt,
        cache_control: { type: 'ephemeral' as const },
      },
    ]

    const stream = await anthropic.messages.create({
      model,
      max_tokens,
      temperature,
      system: systemWithCache,
      messages: messages.map((m) => ({
        role: m.role,
        content: m.content,
      })),
      stream: true,
    })

    for await (const chunk of stream) {
      if (chunk.type === 'content_block_delta' && chunk.delta.type === 'text_delta') {
        yield chunk.delta.text
      }
    }
  } catch (error) {
    console.error('Claude Streaming Error:', error)
    throw error
  }
}
