# 🚀 지금 바로 배포하기 (claude 브랜치)

## ⚡ 빠른 배포 (5분 완성)

### 1단계: Streamlit Cloud 접속

**링크:** https://share.streamlit.io

- GitHub 계정으로 로그인

### 2단계: 새 앱 배포

1. **"New app"** 버튼 클릭

2. **설정 입력:**
   - Repository: `mhroh/idebate`
   - Branch: `claude/analyze-unknown-task-011CUqkenKT94Az5cryNitAm` ⭐ (중요!)
   - Main file path: `app.py`
   - App URL (선택): `idebate-optimized` (또는 원하는 이름)

3. **"Deploy!" 클릭**

### 3단계: Secrets 설정 (필수!)

앱 배포 시작되면 **Settings → Secrets** 클릭 후 아래 내용 붙여넣기:

```toml
# Anthropic API Key
ANTHROPIC_API_KEY = "sk-ant-api03-여기에_실제_키_입력"

# Google Sheets API (Service Account JSON)
type = "service_account"
project_id = "여기에_프로젝트_ID"
private_key_id = "여기에_키_ID"
private_key = "-----BEGIN PRIVATE KEY-----\n여기에_실제_키\n-----END PRIVATE KEY-----\n"
client_email = "여기에_서비스계정_이메일@xxx.iam.gserviceaccount.com"
client_id = "여기에_클라이언트_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "여기에_인증서_URL"
universe_domain = "googleapis.com"

# Google Sheets Document URL
sheet_url = "https://docs.google.com/spreadsheets/d/여기에_시트_ID/edit"
```

**⚠️ 중요:**
- `private_key`는 반드시 따옴표 안에 `\n`을 포함한 전체 키 입력
- 각 필드는 실제 값으로 교체

### 4단계: 배포 완료 대기

- 배포 시간: 약 2-3분
- 화면에서 빌드 로그 확인
- "Your app is live!" 메시지 나오면 완료

### 5단계: 앱 접속 테스트

배포 완료되면 제공되는 URL로 접속:
```
https://idebate-optimized.streamlit.app
```

**테스트 체크리스트:**
- [ ] 페이지 로딩됨
- [ ] 대화명 입력 가능
- [ ] 메시지 전송 가능
- [ ] AI 응답 정상
- [ ] 평가 받기 버튼 작동

---

## 🔍 배포 후 모니터링 (24-48시간)

### Streamlit Cloud 대시보드

**Analytics 탭에서 확인:**
- 📊 동시 접속자 수
- ⏱️ 응답 시간
- 🔴 에러 발생 여부
- 💾 메모리 사용량

### Logs 탭에서 확인:

```bash
# 정상 로그 예시:
INFO: 초기화 시작
INFO: 초기화 완료
INFO: 메시지 스트리밍 중
INFO: 메시지 스트리밍 완료
```

### 문제 발생 시:

**에러 패턴별 대응:**

1. **"Memory limit exceeded"**
   - 현상: 앱 크래시
   - 원인: 메모리 부족
   - 해결: Railway.app으로 이전 또는 Next.js 사용

2. **"Rate limit exceeded" (Google Sheets)**
   - 현상: 대화 저장 실패
   - 원인: 동시 요청 과다
   - 해결: 자동 재시도로 복구 (이미 구현됨)

3. **"API error" (Claude)**
   - 현상: AI 응답 없음
   - 원인: API 키 또는 할당량
   - 해결: Secrets 확인 또는 크레딧 충전

---

## 📊 성공 기준

### 24시간 후 확인:

- ✅ 동시 접속 20명 이상 처리
- ✅ 에러율 5% 미만
- ✅ 평균 응답 시간 5초 미만
- ✅ 메모리 사용량 안정

→ **모든 조건 충족 시 PR 승인 진행!**

---

## 🆘 긴급 롤백

문제 발생 시 즉시 이전 버전으로 복구:

1. Streamlit Cloud → Settings
2. Branch를 `main`으로 변경
3. "Reboot app" 클릭

→ 구 버전으로 즉시 복구됨

---

## 다음 단계

1. ✅ 지금: Streamlit Cloud 배포
2. ⏰ 24-48시간: 모니터링
3. ✅ 문제 없으면: PR 승인 → main 머지
4. 🎉 완료: 자동 재배포 (main 브랜치)
