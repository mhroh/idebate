# 🌐 Vercel 배포 가이드

## 준비물 ✅

로컬 테스트가 성공했다면 준비 완료!
- [x] Supabase 프로젝트 생성
- [x] 환경 변수 준비 (.env.local)
- [x] 로컬에서 작동 확인

---

## 배포 단계

### 1단계: GitHub에 푸시 (이미 완료!)

프로젝트가 이미 GitHub에 있으므로 이 단계는 완료! ✅

### 2단계: Vercel 계정 생성

1. https://vercel.com 접속
2. "Start Deploying" 또는 "Sign Up" 클릭
3. GitHub 계정으로 로그인
4. Vercel이 GitHub 접근 권한 요청 → 승인

### 3단계: 프로젝트 Import

1. Vercel 대시보드에서 "Add New..." 클릭
2. "Project" 선택
3. GitHub 레포지토리 목록에서 `idebate` 레포지토리 선택
   - 안 보이면 "Adjust GitHub App Permissions" 클릭
4. "Import" 클릭

### 4단계: 프로젝트 설정

1. **Root Directory 설정**
   - "Edit" 클릭
   - Root Directory: `idebate-next` 입력
   - "Continue" 클릭

2. **Framework Preset**
   - 자동으로 "Next.js" 감지됨 → 그대로 둠

3. **Environment Variables (중요!)**

   `.env.local` 파일 내용을 복사해서 하나씩 입력:

   | Name | Value |
   |------|-------|
   | `NEXT_PUBLIC_SUPABASE_URL` | `https://xxxxx.supabase.co` |
   | `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `eyJxxx...` |
   | `SUPABASE_SERVICE_ROLE_KEY` | `eyJxxx...` |
   | `ANTHROPIC_API_KEY` | `sk-ant-xxx...` |
   | `GOOGLE_SHEETS_CREDENTIALS` | `{"type":"service_account",...}` |
   | `GOOGLE_CONFIG_SHEET_ID` | `your_sheet_id` |

   **주의:**
   - 각 변수를 "Add" 버튼으로 하나씩 추가
   - `GOOGLE_SHEETS_CREDENTIALS`는 JSON 전체를 따옴표 없이 붙여넣기

4. **Deploy 클릭!**

### 5단계: 배포 완료 (2-3분)

- 빌드 로그가 실시간으로 표시됨
- "Building..." → "Deploying..." → "Ready!"
- ✅ 완료되면 URL 제공: `https://idebate-xxxxx.vercel.app`

### 6단계: 도메인 확인

제공된 URL로 접속해서 테스트!

---

## 무료 플랜 제한

Vercel 무료(Hobby) 플랜:
- ✅ 무제한 배포
- ✅ 자동 HTTPS
- ✅ 글로벌 CDN
- ⚠️ 100GB 대역폭/월
- ⚠️ 6시간 빌드 시간/월

→ **소규모 테스트에는 충분합니다!**

정식 운영 시 Pro 플랜($20/월) 권장

---

## 업데이트 방법

코드 수정 후:

```bash
git add .
git commit -m "Update"
git push
```

→ Vercel이 자동으로 재배포! 🚀

---

## 커스텀 도메인 연결 (선택)

1. Vercel 프로젝트 → Settings → Domains
2. 도메인 입력 (예: debate.yourschool.com)
3. DNS 설정 안내 따라하기
4. 완료!

---

## 문제 해결

### 빌드 실패: "Module not found"
→ Root Directory가 `idebate-next`로 설정되었는지 확인

### 런타임 에러: "Supabase connection failed"
→ Environment Variables가 모두 입력되었는지 확인

### 배포 후 작동 안 함
→ Vercel 로그 확인: 프로젝트 → Deployments → 최신 배포 클릭

---

## 성능 모니터링

Vercel 대시보드에서 확인 가능:
- 실시간 접속자 수
- 응답 시간
- 에러 로그
- 대역폭 사용량

---

## 다음: 학생들에게 URL 공유!

배포 완료 → URL 복사 → 학생들에게 공유 → 끝! 🎉
