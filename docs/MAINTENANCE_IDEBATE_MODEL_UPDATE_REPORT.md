# iDebate 모델 업데이트 구조 조사 보고서

작성일: 2026-06-16

## 1. 조사 기준 저장소

이번 조사는 GitHub 저장소 `mhroh/idebate`를 기준으로 진행했습니다.

- 원격 저장소: `https://github.com/mhroh/idebate.git`
- 로컬 조사 경로: `C:\Users\user\Documents\iDebate\github-idebate`
- 현재 브랜치: `main`
- 최신화 상태: `git pull --ff-only` 결과 `Already up to date.`

기존 `C:\Users\user\Documents\iDebate` 폴더는 앱 코드가 없는 빈 Git 저장소 상태였으므로, 실제 GitHub 저장소를 `github-idebate` 폴더에 clone하여 조사했습니다.

## 2. 앱 진입 파일명

앱 진입 파일은 `app.py`입니다.

근거:

- `app.py` 하단에 `if __name__ == "__main__": main()` 구조가 있습니다.
- `app.py`에서 Streamlit UI, Google Sheet 초기화, Anthropic 호출이 모두 연결됩니다.

## 3. 폴더 구조 요약

현재 저장소의 주요 구조는 다음과 같습니다.

```text
github-idebate/
  app.py
  config.py
  mermaid_utils.py
  requirements.txt
  README.md
  utils/
    gs.py
  docs/
    MAINTENANCE_IDEBATE_MODEL_UPDATE_REPORT.md
```

핵심 역할:

- `app.py`: Streamlit 앱 본문, 사용자 입력 처리, Anthropic 메시지 호출
- `config.py`: Anthropic 클라이언트 초기화 코드가 있으나 현재 `app.py`에서는 직접 import되지 않음
- `utils/gs.py`: Google Sheets 인증, 설정값 읽기, 대화 기록 Sheet 처리
- `requirements.txt`: `streamlit`, `anthropic`, `gspread`, `google-auth` 의존성 선언

## 4. Streamlit 앱 파일 목록

Streamlit 관련 파일:

- `app.py`
- `config.py`
- `utils/gs.py`

확인된 Streamlit 사용:

- `app.py`: `import streamlit as st`
- `config.py`: `import streamlit as st`
- `utils/gs.py`: `import streamlit as st`

`.streamlit/secrets.toml` 파일은 저장소에 포함되어 있지 않습니다. 실제 운영 비밀값은 Streamlit Cloud 또는 로컬 secrets 설정에 따로 있을 가능성이 큽니다.

## 5. Google Sheets API 또는 gspread 사용 위치

Google Sheets 연동은 `utils/gs.py`에 집중되어 있습니다.

주요 위치:

- `utils/gs.py:2`: `import gspread`
- `utils/gs.py:3`: `from google.oauth2.service_account import Credentials`
- `utils/gs.py:8`: `get_authorize()`
- `utils/gs.py:28-38`: `st.secrets`에서 service account 항목을 읽음
- `utils/gs.py:42`: Google Sheets API scope 설정
- `utils/gs.py:43`: `Credentials.from_service_account_info(...)`
- `utils/gs.py:46`: `gspread.authorize(creds)`
- `utils/gs.py:49`: `getSetupInfo()`
- `utils/gs.py:88`: `gc.open_by_url(st.secrets["sheet_url"]).worksheet("정보")`
- `utils/gs.py:91`: `ws.col_values(2)`로 B열 전체를 읽음

비밀값 취급:

- `private_key`, `client_email`, `token_uri` 등 service account 값은 `st.secrets`에서 읽습니다.
- 실제 값은 저장소에 없으며, 보고서에는 원문을 쓰지 않습니다.
- 민감값 표기: `[REDACTED]`

## 6. Anthropic API 호출 위치

Anthropic 관련 코드는 두 곳에 있습니다.

### 실제 앱 실행 경로

실제 메시지 호출은 `app.py`에서 일어납니다.

- `app.py:4`: `import anthropic`
- `app.py:36`: `st.session_state["bot"] = anthropic.Anthropic(api_key = api_key)`
- `app.py:181`: `client.messages.create(...)`
- `app.py:182`: `model = setupInfo['model']`
- `app.py:183`: `max_tokens = setupInfo['max_tokens']`
- `app.py:184`: `temperature = setupInfo['temperature']`
- `app.py:185`: `system = setupInfo['system']`
- `app.py:187`: `stream = setupInfo['stream']`

### 별도 설정 파일

`config.py`에도 Anthropic 클라이언트 초기화가 있습니다.

- `config.py:3`: `from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT`
- `config.py:14`: `anthropic_api_key = st.secrets.get("ANTHROPIC_API_KEY", "")`
- `config.py:15`: `anthropic = Anthropic(api_key=anthropic_api_key)`

다만 현재 조사한 코드 기준으로 `app.py`는 `config.py`를 import하지 않습니다. 실제 채팅 호출에는 `app.py`의 `initialize(api_key, nick_name)`에서 만든 `st.session_state["bot"]`이 사용됩니다.

## 7. 현재 모델명 결정 방식

현재 모델명은 코드에 직접 하드코딩되어 있지 않고, Google Sheet 설정값에서 읽어옵니다.

흐름:

```text
Streamlit Secrets의 sheet_url
  -> utils/gs.py getSetupInfo()
  -> Google Sheet의 "정보" 워크시트
  -> B열 전체 읽기
  -> B5 위치에 해당하는 data[4]를 temp["model"]에 저장
  -> app.py execute_prompt()
  -> Anthropic client.messages.create(model=setupInfo["model"])
```

근거:

- `utils/gs.py:88`: `st.secrets["sheet_url"]`로 설정용 Google Sheet를 엽니다.
- `utils/gs.py:91`: `ws.col_values(2)`로 B열을 읽습니다.
- `utils/gs.py:97`: `temp["model"] = data[4]`
- `app.py:182`: `model = setupInfo['model']`

결론:

- Google Sheet의 `model` 값이 그대로 Anthropic API 호출의 `model` 인자로 전달됩니다.
- `app.py` 안에는 특정 Claude 모델명이 하드코딩되어 있지 않습니다.
- `requirements.txt`나 Git 로그에 Claude 4.5 Sonnet 관련 흔적은 있지만, 실행 시 모델 선택은 Sheet 값이 결정합니다.

## 8. 현재 Google Sheet 설정값을 읽는 방식

`getSetupInfo()`는 `st.secrets["sheet_url"]`에 들어 있는 Google Sheet URL을 열고, 그 안의 `"정보"` 워크시트에서 B열 값을 읽습니다.

코드 기준 매핑:

| Google Sheet 위치 | 코드 인덱스 | 설정 키 | 의미 |
|---|---:|---|---|
| 정보 시트 B1 | `data[0]` | `url` | 수업/대화 기록용 Google Sheet URL |
| 정보 시트 B2 | `data[1]` | `serviceOnOff` | 서비스 on/off |
| 정보 시트 B3 | `data[2]` | `AI` | AI 서비스 이름 |
| 정보 시트 B4 | `data[3]` | `key` | Anthropic API key, 보고서 표기 시 `[REDACTED]` |
| 정보 시트 B5 | `data[4]` | `model` | Anthropic 모델명 |
| 정보 시트 B6 | `data[5]` | `max_tokens` | 최대 토큰 수, 정수 변환 |
| 정보 시트 B7 | `data[6]` | `temperature` | temperature, 실수 변환 |
| 정보 시트 B8 | `data[7]` | `select` | 선택 옵션 |
| 정보 시트 B9 | `data[8]` | `system` | 시스템 프롬프트 |
| 정보 시트 B10 | `data[9]` | `a_p` | 종합 평가 프롬프트 |
| 정보 시트 B11 | `data[10]` | `e_p` | 격려/평가 프롬프트 |
| 정보 시트 B12 | `data[11]` | `stream` | `true`이면 스트리밍 사용 |

중요한 연결:

- B1의 `url`은 실제 학생/사용자별 대화 기록을 저장할 Google Sheet URL입니다.
- B5의 `model`은 Anthropic API 호출에 그대로 들어갑니다.
- B4의 `key`는 앱 실행 중 Anthropic 클라이언트 생성에 사용됩니다. 이 값은 민감값이므로 `[REDACTED]`로만 다뤄야 합니다.

## 9. idebate01, idebate02, idebate03 각각의 연결 단서

저장소 코드 안에는 `idebate01`, `idebate02`, `idebate03` 문자열이 직접 존재하지 않습니다.

확인 결과:

| 서비스 | 코드 내 직접 단서 | 설정 Sheet 연결 방식 추정 |
|---|---|---|
| `idebate01` | 없음 | 해당 Streamlit 배포 환경의 `st.secrets["sheet_url"]` 값으로 결정 |
| `idebate02` | 없음 | 해당 Streamlit 배포 환경의 `st.secrets["sheet_url"]` 값으로 결정 |
| `idebate03` | 없음 | 해당 Streamlit 배포 환경의 `st.secrets["sheet_url"]` 값으로 결정 |

현재 코드 구조상 각 서비스가 서로 다른 설정 파일에 연결되는 단서는 저장소 파일이 아니라 배포 환경의 Streamlit Secrets에 있을 가능성이 가장 큽니다.

운영자가 확인해야 할 값:

- `idebate01` 앱의 Streamlit Secrets 안 `sheet_url`
- `idebate02` 앱의 Streamlit Secrets 안 `sheet_url`
- `idebate03` 앱의 Streamlit Secrets 안 `sheet_url`

각 `sheet_url`이 가리키는 Google Sheet의 `"정보"` 워크시트 B5가 해당 서비스의 모델명을 결정합니다.

## 10. Streamlit Secrets, 환경변수, 하드코딩된 URL/ID 사용 여부

### Streamlit Secrets 사용

사용합니다.

`utils/gs.py`에서 읽는 secrets 키:

- `type`
- `project_id`
- `private_key_id`
- `private_key`
- `client_email`
- `client_id`
- `auth_uri`
- `token_uri`
- `auth_provider_x509_cert_url`
- `client_x509_cert_url`
- `universe_domain`
- `sheet_url`

`config.py`에서 읽는 secrets 키:

- `ANTHROPIC_API_KEY`
- 주석 처리된 키: `PROMPTLAYER_API_KEY`, `OPENAI_API_KEY`

### 환경변수 사용

현재 조사 범위에서는 `os.getenv(...)`, `os.environ[...]` 사용이 발견되지 않았습니다.

### 하드코딩된 URL/ID

현재 조사 범위에서는 Google Sheet URL, spreadsheet ID가 코드에 하드코딩되어 있지 않습니다.

Google Sheet 연결은 다음 두 단계로 이루어집니다.

1. 설정용 Sheet: `st.secrets["sheet_url"]`
2. 기록용 Sheet: 설정용 Sheet의 `"정보"` 워크시트 B1 값

### 하드코딩된 모델명

현재 조사 범위에서는 모델명이 코드에 하드코딩되어 있지 않습니다.

모델명은 `"정보"` 워크시트 B5 값입니다.

## 11. Sonnet 4.6으로 바꾸려면 수정해야 할 위치

현재 코드 구조 기준으로는 코드 수정이 아니라 Google Sheet 설정 수정이 우선입니다.

각 서비스별로 해야 할 일:

1. Streamlit Cloud에서 해당 앱의 Secrets를 엽니다.
2. `sheet_url` 값을 확인합니다.
3. 그 URL의 Google Sheet를 엽니다.
4. `"정보"` 워크시트로 이동합니다.
5. B5 셀, 즉 `model` 값을 Sonnet 4.6 모델명으로 변경합니다.
6. 앱에서 설정 캐시가 최대 300초 유지될 수 있으므로, 변경 후 약 5분 기다리거나 앱을 재시작합니다.

주의:

- 정확한 Sonnet 4.6 API 모델명 문자열은 Anthropic 공식 문서 또는 현재 계정에서 사용 가능한 모델 목록으로 확인해야 합니다.
- 현재 날짜 기준 최신 모델명은 바뀔 수 있으므로, 코드나 운영 Sheet에 입력하기 전에 반드시 공식 Anthropic 문서 기준으로 확인해야 합니다.

코드 수정이 필요한 경우:

- 모델명을 Sheet가 아니라 코드에서 강제로 고정하고 싶을 때
- `idebate01/02/03` 별 설정을 하나의 코드에서 명시적으로 분기하고 싶을 때
- API key를 Google Sheet B4가 아니라 Streamlit Secrets의 `ANTHROPIC_API_KEY`로 일원화하고 싶을 때

이번 요청 범위에서는 코드 수정은 하지 않았습니다.

## 12. 비개발자인 운영자가 다음에 해야 할 일

운영자가 해야 할 가장 중요한 확인은 각 Streamlit 앱의 Secrets에 있는 `sheet_url`입니다.

서비스별 체크리스트:

| 서비스 | 확인할 곳 | 확인할 값 | 이후 확인할 Google Sheet 셀 |
|---|---|---|---|
| `idebate01` | Streamlit Secrets | `sheet_url` | `"정보"` 시트 B5 |
| `idebate02` | Streamlit Secrets | `sheet_url` | `"정보"` 시트 B5 |
| `idebate03` | Streamlit Secrets | `sheet_url` | `"정보"` 시트 B5 |

운영 절차:

1. Streamlit Cloud에 로그인합니다.
2. `idebate01`, `idebate02`, `idebate03` 앱을 각각 엽니다.
3. 앱별 Secrets 설정에서 `sheet_url`을 찾습니다.
4. `sheet_url` 원문은 외부에 공유하지 말고, 필요한 경우 `[REDACTED]`로 가립니다.
5. 해당 Google Sheet의 `"정보"` 워크시트를 엽니다.
6. B5 셀의 모델명을 확인합니다.
7. Sonnet 4.6으로 바꾸려면 B5 셀만 바꾸는 방식이 현재 코드 구조와 맞습니다.
8. 변경 후 5분 정도 기다리거나 앱을 재시작합니다.
9. 간단한 테스트 대화를 보내 정상 응답 여부를 확인합니다.

## 13. 보안 주의

절대 외부에 그대로 공유하면 안 되는 값:

- Anthropic API key
- Google service account `private_key`
- `private_key_id`
- OAuth token 또는 token URI 관련 민감 설정
- Google Sheet URL 중 공개하면 안 되는 운영용 URL
- Streamlit Secrets 전체 내용

보고서나 문의 문서에는 아래처럼 표기하세요.

```text
ANTHROPIC_API_KEY = [REDACTED]
private_key = [REDACTED]
sheet_url = [REDACTED]
```

## 14. 최종 결론

현재 `mhroh/idebate` 저장소 기준으로 모델명은 코드에 하드코딩되어 있지 않습니다.

모델명 결정 위치는 다음 한 줄입니다.

```text
utils/gs.py의 getSetupInfo()가 Google Sheet "정보" 시트 B5 값을 읽어 temp["model"]에 저장
```

그리고 실제 Anthropic 호출은 다음 위치에서 그 값을 그대로 사용합니다.

```text
app.py의 execute_prompt()에서 client.messages.create(model=setupInfo["model"])
```

따라서 `idebate01`, `idebate02`, `idebate03`의 Sonnet 4.6 변경은 각 앱의 Streamlit Secrets에 들어 있는 `sheet_url`이 가리키는 Google Sheet의 `"정보"` 워크시트 B5 값을 확인하고 수정하는 방식으로 진행하는 것이 현재 코드 구조상 가장 직접적인 방법입니다.

