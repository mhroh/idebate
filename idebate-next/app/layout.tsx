import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'iDebate - AI 토론 튜터',
  description: '학생들을 위한 AI 기반 토론 및 논술 튜터링 시스템',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  )
}
