# iDebate Streamlit 배포 인벤토리

작성일: 2026-06-16

## 1. 문서 목적

이 문서는 iDebate 계열 Streamlit 앱들이 어떤 GitHub 코드, 어떤 Streamlit Secrets, 어떤 Google Sheet 설정 파일에 연결되어 있는지 운영자가 추적하기 위한 실태조사 표입니다.

현재 확인된 공통 사실:

- 실제 코드 저장소는 `mhroh/idebate`입니다.
- 로컬 조사 위치는 `C:\Users\user\Documents\iDebate\github-idebate`입니다.
- 앱 진입 파일은 `app.py`입니다.
- 설정 시트 URL은 Streamlit Secrets의 `sheet_url`에서 옵니다.
- Google Sheet의 `"정보"` 시트 B4가 API KEY입니다.
- Google Sheet의 `"정보"` 시트 B5가 `model`입니다.
- `idebate01`, `idebate02`, `idebate03` 문자열은 코드 안에 없습니다.
- `idebate.streamlit.app` 역시 코드 안에서 별도 분기되는 단서는 현재 확인되지 않았습니다.
- 따라서 각 앱의 실제 설정 시트는 Streamlit Cloud 앱별 Settings 또는 Secrets에서 확인해야 합니다.

보안 규칙:

- `private_key`, API KEY, token, 전체 `sheet_url`, 전체 `client_email`은 이 문서에 쓰지 않습니다.
- 필요한 경우 `[REDACTED]`로 표시합니다.
- Google Sheet URL이나 service account 이메일은 운영상 필요할 때도 전체 원문을 외부에 공유하지 않습니다.

## 2. 배포 인벤토리 표

2026-06-16 기준 `idebate`, `idebate01`, `idebate02`, `idebate03` 운영 복구 및 Sonnet 4.6 전환 확인이 완료되었습니다.

| 앱 URL | Streamlit 앱 이름 | Repository | Branch | Main file path | sheet_url 확인 여부 | 연결된 Google Sheet 문서명 | Google service account client_email 확인 여부 | 현재 model 값 | 현재 API KEY 교체 필요 여부 | 상태 판단 | 다음 조치 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `https://idebate.streamlit.app` | `idebate` | `mhroh/idebate` | `main` | `app.py` | 확인됨 — 전체 URL은 문서에 기록하지 않음 | `iDebate 00.수업할 시트 설정` | 미기록 — 전체 값은 기록하지 않음 | `claude-sonnet-4-6` | 기록하지 않음 — 민감값은 `[REDACTED]` 처리 | 정상 확인 — 시각화 도구 UI 제거 후 정상 작동 | 운영 모니터링 |
| `https://idebate01.streamlit.app` | `ddd01` | `mhroh/idebate` | `main` | `app.py` | 확인됨 — ddd01 Secrets의 값 교체 완료, 전체 URL은 기록하지 않음 | `idebate01. 00.수업할 시트 설정` | 미기록 — 전체 값은 기록하지 않음 | `claude-sonnet-4-6` | 기록하지 않음 — 민감값은 `[REDACTED]` 처리 | 정상 확인 — idebate03 설정 시트 공유 문제 분리 완료 | 운영 모니터링 |
| `https://idebate02.streamlit.app` | `ddd02` | `mhroh/idebate` | `main` | `app.py` | 확인됨 — 전체 URL은 문서에 기록하지 않음 | 미기록 — 필요 시 문서명만 추가 | 미기록 — 전체 값은 기록하지 않음 | `claude-sonnet-4-6` | 기록하지 않음 — 민감값은 `[REDACTED]` 처리 | 정상 확인 | 운영 모니터링 |
| `https://idebate03.streamlit.app` | `ddd03` | `mhroh/idebate` | `main` | `app.py` | 확인됨 — 전체 URL은 문서에 기록하지 않음 | `idebate03. 00.수업할 시트 설정` | 미기록 — 전체 값은 기록하지 않음 | `claude-sonnet-4-6` | 기록하지 않음 — 민감값은 `[REDACTED]` 처리 | 정상 확인 — 설정 시트를 Google Drive `idebate03` 폴더로 이동 정리 | 운영 모니터링 |

## 3. 각 열에 무엇을 적어야 하는가

| 열 | 적는 방법 |
|---|---|
| 앱 URL | 실제 접속 URL을 적습니다. |
| Streamlit 앱 이름 | Streamlit Cloud에 표시되는 앱 이름을 적습니다. |
| Repository | Settings > General에서 연결된 GitHub 저장소를 확인합니다. 예: `mhroh/idebate` |
| Branch | Settings > General에서 배포 브랜치를 확인합니다. 예: `main` |
| Main file path | Settings > General에서 앱 진입 파일을 확인합니다. 예: `app.py` |
| sheet_url 확인 여부 | Secrets에서 `sheet_url` 존재 여부를 확인합니다. 전체 URL은 문서에 쓰지 않습니다. |
| 연결된 Google Sheet 문서명 | `sheet_url`로 열린 Google Sheet의 문서 제목만 적습니다. 전체 URL은 쓰지 않습니다. |
| Google service account client_email 확인 여부 | Secrets에 `client_email`이 있는지 확인합니다. 전체 이메일은 쓰지 않고 `[REDACTED]` 처리합니다. |
| 현재 model 값 | Google Sheet `"정보"` 시트 B5 값을 적습니다. |
| 현재 API KEY 교체 필요 여부 | B4 API KEY가 노출되었거나 오래되었거나 불명확하면 교체 필요로 적습니다. 키 원문은 쓰지 않습니다. |
| 상태 판단 | 정상 / 확인 필요 / 조치 필요 등으로 적습니다. |
| 다음 조치 | 운영자가 다음에 해야 할 일을 짧게 적습니다. |

## 4. 비개발자용 확인 절차

아래 절차를 앱별로 반복하세요.

대상 앱:

- `idebate.streamlit.app`
- `idebate01.streamlit.app`
- `idebate02.streamlit.app`
- `idebate03.streamlit.app`

### 1단계: Streamlit Cloud에서 앱 선택

1. Streamlit Cloud에 로그인합니다.
2. 앱 목록에서 확인할 앱을 선택합니다.
3. 앱 URL이 이 문서의 표와 맞는지 확인합니다.

### 2단계: Manage app 또는 Settings 열기

1. 앱 화면에서 `Manage app` 또는 `Settings`를 엽니다.
2. 설정 화면에 들어가면 `General`과 `Secrets`를 차례로 확인합니다.

### 3단계: General에서 GitHub 배포 정보 확인

`General`에서 아래 항목을 확인해 표에 적습니다.

- Repository
- Branch
- Main file path

예상되는 값:

```text
Repository = mhroh/idebate
Branch = main
Main file path = app.py
```

다만 실제 Streamlit Cloud 설정값이 우선입니다. 화면에 보이는 값을 그대로 기록하세요.

### 4단계: Secrets에서 `sheet_url` 확인

`Secrets`에서 `sheet_url`이 있는지 확인합니다.

문서에는 전체 URL을 쓰지 말고 아래처럼 적습니다.

```text
sheet_url = [REDACTED]
```

확인 결과는 표의 `sheet_url 확인 여부` 열에 적습니다.

예:

```text
확인됨 — 전체 URL은 [REDACTED]
```

### 5단계: 해당 Google Sheet 열기

1. Streamlit Secrets의 `sheet_url` 값을 복사합니다.
2. 브라우저에서 해당 Google Sheet를 엽니다.
3. 문서 제목을 확인합니다.
4. 표의 `연결된 Google Sheet 문서명` 열에 문서 제목만 적습니다.

주의:

- Google Sheet 전체 URL은 문서에 쓰지 않습니다.
- 시트 안의 API KEY도 문서에 쓰지 않습니다.

### 6단계: `"정보"` 시트 B4/B5 확인

Google Sheet에서 `"정보"` 시트를 엽니다.

확인할 셀:

- B4: API KEY
- B5: model

문서 기록 방법:

```text
B4 API KEY = [REDACTED]
B5 model = claude-sonnet-4-6
```

B4는 값이 있는지, 교체가 필요한지만 판단합니다. 원문을 절대 적지 않습니다.

B5는 현재 모델명입니다. Sonnet 4.6 적용 여부를 확인하려면 `claude-sonnet-4-6`인지 봅니다.

### 7단계: Google Drive에서 시트 소유 계정 확인

1. Google Sheet 상단의 공유 버튼을 누릅니다.
2. 소유자가 누구인지 확인합니다.
3. 운영자가 관리 가능한 계정인지 확인합니다.
4. 문서에는 계정 전체 이메일을 쓰지 말고 필요하면 `[REDACTED]` 처리합니다.

예:

```text
소유 계정 = 확인됨 — [REDACTED]
```

### 8단계: service account 공유 여부 확인

Google Sheet 공유 설정에서 service account의 `client_email`이 공유되어 있는지 확인합니다.

확인 방법:

1. Streamlit Secrets에서 `client_email` 항목이 있는지 확인합니다.
2. 전체 이메일은 문서에 쓰지 않습니다.
3. Google Sheet 공유 목록에 해당 service account가 있는지 확인합니다.

문서 기록 예:

```text
client_email = 확인됨 — [REDACTED]
Google Sheet 공유 여부 = 확인됨
```

만약 공유되어 있지 않다면 앱이 Google Sheet를 읽지 못할 수 있습니다.

## 5. 상태 판단 기준

| 상태 판단 | 의미 | 다음 조치 |
|---|---|---|
| 정상 | Repository, Branch, Main file path, `sheet_url`, Google Sheet B4/B5, service account 공유가 모두 확인됨 | 정기 점검만 유지 |
| 확인 필요 | 일부 항목을 아직 확인하지 못함 | Streamlit Cloud와 Google Sheet에서 추가 확인 |
| 조치 필요 | `sheet_url` 없음, B4 API KEY 없음, B5 모델명 오류, service account 미공유 등 문제가 확인됨 | 해당 설정 수정 후 앱 재부팅 |
| 보안 조치 필요 | API KEY 또는 private key 노출 의심 | 즉시 키 폐기 및 재발급 |

## 6. 보안상 문서에 쓰면 안 되는 값

아래 값은 절대 원문으로 기록하지 않습니다.

- Anthropic API KEY
- Google service account `private_key`
- `private_key_id`
- token 값
- 전체 `sheet_url`
- 전체 `client_email`
- Streamlit Secrets 전체 내용

대신 이렇게 씁니다.

```text
API KEY = [REDACTED]
private_key = [REDACTED]
token = [REDACTED]
sheet_url = [REDACTED]
client_email = [REDACTED]
```

## 7. 다음 운영 조치

1. `idebate.streamlit.app`부터 Streamlit Cloud 설정을 확인합니다.
2. Repository, Branch, Main file path를 표에 채웁니다.
3. Secrets에서 `sheet_url` 존재 여부를 확인합니다.
4. 연결된 Google Sheet 문서명을 표에 적습니다.
5. `"정보"` 시트 B5의 현재 model 값을 표에 적습니다.
6. B4 API KEY는 원문을 적지 말고 교체 필요 여부만 판단합니다.
7. Google Sheet가 service account `client_email`에 공유되어 있는지 확인합니다.
8. 같은 절차를 `idebate01`, `idebate02`, `idebate03`에도 반복합니다.

## 8. 2026-06-16 운영 반영 기록

`idebate.streamlit.app`에 대해 아래 사실을 확인하고 운영 기록에 반영했습니다.

| 항목 | 기록 |
|---|---|
| 실행 저장소 | `mhroh/idebate` |
| 실행 브랜치 | `main` |
| 실행 파일 | `app.py` |
| 연결된 설정 시트 제목 | `iDebate 00.수업할 시트 설정` |
| `"정보"` 시트 B5 `model` | `claude-sonnet-4-6` |
| 적용 commit | `8f10cb9 Remove visualization UI from main chatbot screen` |
| 적용 내용 | `app.py`에서 메인 챗봇 화면의 시각화 도구 UI 제거 |
| 확인 결과 | `idebate.streamlit.app`에서 시각화 도구 UI가 사라지고 상대심문 연습 도우미가 정상 출력됨 |

민감 정보 원문은 기록하지 않았습니다.

## 9. 2026-06-16 최종 운영 복구 완료 기록

오늘 완료된 운영 복구 결과입니다.

| 구분 | 완료 내용 |
|---|---|
| `idebate.streamlit.app` | `mhroh/idebate` `main` 브랜치의 `app.py` 실행 확인. 설정 시트 제목은 `iDebate 00.수업할 시트 설정`. model은 `claude-sonnet-4-6`. 시각화 도구 UI 제거 후 정상 작동 확인. |
| `idebate01` / `ddd01` | 기존에는 `idebate03` 설정 시트를 함께 보고 있었음. `idebate03` 설정 시트를 복사해 `idebate01. 00.수업할 시트 설정`을 새로 생성함. 생성 위치는 Google Drive `idebate01` 폴더. `ddd01` Streamlit Secrets의 `sheet_url`을 새 idebate01 설정 시트 URL로 교체함. model은 `claude-sonnet-4-6`. 정상 작동 확인. |
| `idebate02` / `ddd02` | model을 `claude-sonnet-4-6`으로 확인. 정상 작동 확인. |
| `idebate03` / `ddd03` | 설정 시트 제목은 `idebate03. 00.수업할 시트 설정`. model은 `claude-sonnet-4-6`. 정상 작동 확인. 해당 시트는 Google Drive `idebate03` 폴더로 이동해 정리함. |

코드 변경 기록:

| 항목 | 내용 |
|---|---|
| commit | `8f10cb9 Remove visualization UI from main chatbot screen` |
| 변경 파일 | `app.py` |
| 제거한 UI | 시각화 도구, 테스트 차트 보기, 수동 차트 만들기, Mermaid 차트 표시 블록 |
| 유지한 기능 | 기본 챗봇 UI, 대화명 입력, 대화 종료, 채팅 입력, Claude 호출 흐름 |

최종 결론:

- `idebate`, `idebate01`, `idebate02`, `idebate03` 모두 Sonnet 4.6 전환 완료.
- `idebate.streamlit.app` 인터페이스 복구 완료.
- `idebate01`과 `idebate03` 설정 시트 공유 문제 분리 완료.
- 민감 정보 원문은 기록하지 않았으며, 필요한 경우 `[REDACTED]`로만 표기합니다.
