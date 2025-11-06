# 🚀 iDebate 빠른 시작 가이드

## 1단계: Supabase 설정 (5분)

### A. Supabase 프로젝트 생성

1. **Supabase 가입**
   - https://supabase.com 접속
   - "Start your project" 클릭
   - GitHub 계정으로 로그인

2. **새 프로젝트 생성**
   - "New Project" 클릭
   - Project name: `idebate`
   - Database Password: 안전한 비밀번호 입력 (잘 보관!)
   - Region: `Northeast Asia (Seoul)` 선택 (가장 빠름!)
   - "Create new project" 클릭
   - ⏳ 2-3분 대기 (프로젝트 생성 중)

3. **데이터베이스 스키마 생성**
   - 왼쪽 메뉴에서 "SQL Editor" 클릭
   - "New query" 클릭
   - `idebate-next/supabase/schema.sql` 파일 내용 전체 복사
   - 붙여넣기 후 "Run" 버튼 클릭
   - ✅ Success 메시지 확인!

4. **API 키 복사**
   - 왼쪽 메뉴에서 "Project Settings" (톱니바퀴) 클릭
   - "API" 탭 클릭
   - 다음 3가지 복사해서 메모장에 저장:
     ```
     Project URL: https://xxxxx.supabase.co
     anon public: eyJxxx...
     service_role: eyJxxx... (Show 버튼 클릭 후 복사)
     ```

---

## 2단계: Google Sheets 확인

현재 사용 중인 Google Sheets가 있으면 그대로 사용!

**필요한 정보:**
- Sheet URL에서 ID 부분 복사:
  `https://docs.google.com/spreadsheets/d/[여기가_SHEET_ID]/edit`

- Google 서비스 계정 JSON (기존 Streamlit에서 사용 중인 것)

---

## 3단계: 환경 변수 설정

`idebate-next/.env.local` 파일 생성:

```bash
# Supabase (위에서 복사한 값)
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxx...
SUPABASE_SERVICE_ROLE_KEY=eyJxxx...

# Anthropic Claude API (기존 사용 중인 키)
ANTHROPIC_API_KEY=sk-ant-xxx...

# Google Sheets API
GOOGLE_SHEETS_CREDENTIALS='{"type":"service_account","project_id":"...전체_JSON_내용..."}'
GOOGLE_CONFIG_SHEET_ID=your_sheet_id
```

**주의:**
- `GOOGLE_SHEETS_CREDENTIALS`는 JSON 전체를 작은따옴표로 감싸기!
- 줄바꿈 없이 한 줄로!

---

## 4단계: 로컬 테스트

```bash
cd idebate-next
npm install
npm run dev
```

브라우저에서 http://localhost:3000 접속! 🎉

### 테스트 체크리스트:
- [ ] 대화명 입력 후 시작
- [ ] 메시지 보내기
- [ ] AI 응답 받기
- [ ] 여러 창에서 동시 접속 테스트

---

## 문제 해결

### "Cannot find module" 에러
```bash
rm -rf node_modules package-lock.json
npm install
```

### "Supabase connection failed"
→ `.env.local` 파일의 URL과 키를 다시 확인

### "Google Sheets API error"
→ 서비스 계정이 Sheet에 편집 권한이 있는지 확인

---

## 다음 단계

로컬 테스트 성공 → Vercel 배포!
