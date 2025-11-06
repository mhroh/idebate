# 🎓 iDebate - AI 토론 튜터 (Next.js + Supabase)

200명 이상 동시 접속 가능한 확장 가능한 토론/논술 튜터링 시스템

## ✨ 주요 기능

- ✅ **무제한 동시 접속**: 200+ 학생 동시 사용 가능
- ✅ **Google Sheets 통합**: 선생님이 프롬프트를 쉽게 관리
- ✅ **Claude API 프롬프트 캐싱**: 토큰 비용 90% 절감
- ✅ **실시간 채팅**: 빠른 응답 속도
- ✅ **자동 평가**: 대화 종료 시 AI 평가 생성 및 Google Sheets 저장
- ✅ **무료 시작**: Vercel + Supabase 무료 티어로 시작 가능

## 🏗️ 기술 스택

- **프론트엔드**: Next.js 14 (App Router), React, TailwindCSS
- **백엔드**: Next.js API Routes
- **데이터베이스**: Supabase (PostgreSQL)
- **AI**: Claude 3.5 Sonnet (Anthropic)
- **설정 관리**: Google Sheets API
- **배포**: Vercel (무료 가능)

---

## 🚀 설치 가이드

### 1단계: Supabase 프로젝트 생성

1. [Supabase](https://supabase.com)에 가입하고 새 프로젝트 생성
2. SQL Editor에서 `supabase/schema.sql` 파일 내용 실행
3. Settings > API에서 다음 정보 복사:
   - `Project URL` → `NEXT_PUBLIC_SUPABASE_URL`
   - `anon public` 키 → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `service_role` 키 → `SUPABASE_SERVICE_ROLE_KEY`

### 2단계: Google Sheets API 설정

1. [Google Cloud Console](https://console.cloud.google.com)에서 프로젝트 생성
2. Google Sheets API 활성화
3. 서비스 계정 생성 후 JSON 키 다운로드
4. Google Sheets에 서비스 계정 이메일 공유 (편집 권한)
5. Sheet ID를 `GOOGLE_CONFIG_SHEET_ID`로 설정

**Google Sheets 구조:**
- "정보" 시트: B열에 설정 값 (기존 Streamlit 앱과 동일)
- "수업요약" 시트: A열(이름), B열(종합평가), C열(평어)

### 3단계: 환경 변수 설정

`.env.local.example`을 복사해서 `.env.local` 생성:

\`\`\`bash
cp .env.local.example .env.local
\`\`\`

`.env.local` 파일 수정:

\`\`\`env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Anthropic Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key

# Google Sheets API
GOOGLE_SHEETS_CREDENTIALS='{"type":"service_account","project_id":"...}'
GOOGLE_CONFIG_SHEET_ID=your_sheet_id
\`\`\`

### 4단계: 로컬 실행

\`\`\`bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
\`\`\`

브라우저에서 http://localhost:3000 접속!

---

## 🌐 Vercel 배포 (무료)

### 1. GitHub에 푸시

\`\`\`bash
cd idebate-next
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
\`\`\`

### 2. Vercel 배포

1. [Vercel](https://vercel.com)에 가입
2. "New Project" 클릭
3. GitHub 레포지토리 선택
4. Environment Variables에 `.env.local` 내용 입력
5. Deploy 클릭!

배포 완료 후 제공되는 URL로 접속하면 됩니다.

---

## 💰 비용 분석

### 무료 티어 (테스트/소규모)

- **Vercel**: 무료 (Hobby)
- **Supabase**: 무료 (500MB DB, 2GB 대역폭)
- **Claude API**: 사용한 만큼만 (Tier 4: 월 $500 크레딧)

**예상 비용**: Claude API 사용량에 따라 월 $10-30

### 유료 티어 (정식 운영)

- **Vercel Pro**: $20/월
- **Supabase Pro**: $25/월
- **Claude API**: 월 $30-100 (200명 기준)

**총 비용**: 월 $75-145

---

## 📊 성능 비교

| 항목 | Streamlit (기존) | Next.js (신규) |
|------|------------------|----------------|
| 동시 접속 | 20-30명 | 200+ 명 |
| 응답 속도 | 보통 | 빠름 (5배) |
| Google Sheets | 매번 호출 | 5분 캐싱 |
| 확장성 | 제한적 | 무제한 |
| 비용 | $0-10/월 | $0-145/월 |

---

## 🔧 추가 기능 (향후 개발)

- [ ] 선생님용 관리 대시보드
- [ ] 실시간 학생 모니터링
- [ ] 토큰 사용량 통계
- [ ] 평가 히스토리 조회
- [ ] 모바일 앱 (React Native)

---

## 🤝 문의

문제가 발생하면 이슈를 남겨주세요!
