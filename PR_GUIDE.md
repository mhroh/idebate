# 🔄 Pull Request 생성 가이드

## PR 생성 (main ← claude/analyze-unknown-task-011CUqkenKT94Az5cryNitAm)

### 자동 링크로 바로 생성:

**👉 이 링크 클릭하면 자동으로 PR 생성 페이지 열림:**
```
https://github.com/mhroh/idebate/compare/main...claude/analyze-unknown-task-011CUqkenKT94Az5cryNitAm
```

### PR 제목 및 설명 (복사해서 붙여넣기):

**Title:**
```
🚀 Streamlit 앱 20명 안정 사용 최적화
```

**Description:**
```markdown
## 📋 변경 사항

### ✅ 성능 최적화
- Google Sheets Rate Limit 자동 재시도 (exponential backoff)
- 메모리 최적화 (대화 50개 제한)
- Claude API 프롬프트 캐싱 (토큰 90% 절감)

### ✅ 안정성 강화
- 에러 복구 로직 강화
- 평가 기능 버그 수정
- 세션 관리 개선

### ✅ 배포 준비
- requirements.txt 버전 고정
- .streamlit/config.toml 설정 추가
- STREAMLIT_DEPLOY.md 배포 가이드

### 📦 추가 기능
- Next.js + Supabase 버전 (idebate-next/) - 200+ 사용자용
- 관리자 대시보드
- 자동 평가 시스템

## 🎯 예상 효과

- **동시 접속**: 10-15명 → **20-25명**
- **토큰 비용**: **90% 절감**
- **에러율**: **대폭 감소**

## 🧪 테스트 계획

1. ✅ claude 브랜치로 Streamlit Cloud 배포 (선택2)
2. ⏳ 24-48시간 모니터링
3. ✅ 안정성 확인 후 이 PR 승인

---

**현재 상태**: claude 브랜치로 배포 중 (테스트 단계)
**승인 시점**: 안정성 확인 후 (24-48시간 뒤)
```

### PR 생성 후 할 일:

- ✅ PR 생성 (아직 머지 안 함!)
- ⏸️ 승인 대기 (24-48시간)
- 🔍 모니터링 후 문제 없으면 승인

---

## 중요!

**지금은 PR만 생성하고 머지하지 마세요!**
claude 브랜치 배포 후 안정성 확인이 먼저입니다.
