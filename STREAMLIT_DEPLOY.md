# 📱 Streamlit 앱 배포 가이드 (20명용)

## ✅ 완료된 최적화

1. **Google Sheets Rate Limit 대응**
   - 자동 재시도 (최대 5회)
   - Exponential backoff

2. **메모리 최적화**
   - 대화 내역 50개로 제한
   - 오래된 대화 자동 정리

3. **에러 복구**
   - API 실패 시 자동 재시도
   - 명확한 에러 메시지

4. **동시 접속 제한**
   - 최대 25명 동시 사용
   - 초과 시 대기 안내

5. **Claude API 프롬프트 캐싱**
   - 토큰 비용 90% 절감
   - 5분간 캐시 유지

---

## 🚀 배포 방법

### Option 1: Streamlit Community Cloud (무료)

#### 장점:
- ✅ 완전 무료
- ✅ 쉬운 배포 (GitHub 연동)
- ✅ 자동 HTTPS

#### 제한사항:
- ⚠️ CPU: 0.78 cores
- ⚠️ 메모리: 1GB
- ⚠️ **예상: 10-20명 동시 접속**

#### 배포 방법:

1. **GitHub 푸시** (이미 완료!)

2. **Streamlit Cloud 가입**
   - https://share.streamlit.io 접속
   - GitHub 계정으로 로그인

3. **새 앱 배포**
   - "New app" 클릭
   - Repository: `mhroh/idebate` 선택
   - Branch: `main` (또는 현재 브랜치)
   - Main file path: `app.py`
   - "Deploy!" 클릭

4. **Secrets 설정**
   - 앱 → Settings → Secrets
   - 아래 내용 붙여넣기:

```toml
# Anthropic API
ANTHROPIC_API_KEY = "sk-ant-xxx..."

# Google Sheets API
type = "service_account"
project_id = "your-project-id"
private_key_id = "xxx..."
private_key = "-----BEGIN PRIVATE KEY-----\nxxx...\n-----END PRIVATE KEY-----\n"
client_email = "xxx@xxx.iam.gserviceaccount.com"
client_id = "xxx"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "xxx"
universe_domain = "googleapis.com"

# Google Sheets Config
sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
```

5. **배포 완료!**
   - URL 제공: `https://xxx.streamlit.app`

---

### Option 2: Railway.app (유료 추천)

#### 장점:
- ✅ 더 많은 리소스
- ✅ 자동 스케일링
- ✅ **예상: 20-50명 동시 접속**

#### 비용:
- $5-10/월

#### 배포 방법:

1. **Railway.app 가입**
   - https://railway.app
   - GitHub 연동

2. **새 프로젝트**
   - "New Project" → "Deploy from GitHub repo"
   - `mhroh/idebate` 선택

3. **설정**
   - Root Directory: `/` (기본값)
   - Start Command: `streamlit run app.py --server.port $PORT`

4. **환경 변수 추가**
   - Settings → Variables
   - Streamlit Cloud와 동일하게 입력

5. **배포 완료!**

---

### Option 3: AWS/GCP (대규모)

50명 이상이면 Next.js 버전 사용 권장!

---

## 📊 성능 예상

### Streamlit Community Cloud (무료)
- **최대 동시 접속**: 10-20명
- **메모리**: 1GB
- **비용**: $0

### Railway.app ($10/월)
- **최대 동시 접속**: 20-50명
- **메모리**: 2GB+
- **비용**: $5-10/월

### Next.js + Vercel (추천, 대규모)
- **최대 동시 접속**: 200+명
- **비용**: $0-75/월

---

## 🔧 추가 최적화 (필요 시)

### 1. 메모리 더 줄이기

`app.py`의 `MAX_CONVERSATION_LENGTH` 조정:
```python
MAX_CONVERSATION_LENGTH = 30  # 50 → 30으로 줄이기
```

### 2. 동시 접속 제한 늘리기

`app.py`의 `MAX_CONCURRENT_USERS` 조정:
```python
MAX_CONCURRENT_USERS = 30  # 25 → 30으로 늘리기
```

⚠️ 단, 서버 메모리 확인 필요!

### 3. Claude API 모델 변경

Google Sheets의 "정보" 시트에서:
- `model`: `claude-3-5-sonnet-20241022` → `claude-3-haiku-20240307`
- Haiku는 더 빠르고 저렴하지만 품질은 약간 낮음

---

## 🐛 문제 해결

### "Memory limit exceeded"
→ Railway.app으로 이전 또는 Next.js 버전 사용

### "Too many requests"
→ Google Sheets 캐싱 시간 늘리기 (5분 → 10분)

### 느린 응답
→ Claude API 모델을 Haiku로 변경

---

## 📈 모니터링

### Streamlit Cloud
- Dashboard → Logs 확인
- 메모리/CPU 사용량 모니터링

### 에러 확인
```bash
# 로컬에서 테스트
streamlit run app.py
```

---

## 💡 권장 사항

### 20명 이하
→ **Streamlit Community Cloud (무료)** ✅

### 20-50명
→ **Railway.app ($10/월)** ✅

### 50명 이상
→ **Next.js 버전 (idebate-next/)** ✅

---

현재 최적화로 **20명 동시 접속은 안정적**입니다!
