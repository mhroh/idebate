# iDebate Streamlit / Google Sheet 운영 가이드

작성일: 2026-06-16

이 문서는 iDebate 운영자가 모델 변경, 설정 Sheet 확인, 장애 점검을 할 때 헷갈리지 않도록 만든 비개발자용 안내서입니다.

주의:

- API KEY, `private_key`, token, service account 값은 절대 문서나 메신저에 원문으로 공유하지 마세요.
- 이 문서에서는 모든 민감값을 `[REDACTED]`로 표시합니다.
- 이 문서는 운영 절차 안내이며, 코드 수정 지침이 아닙니다.

## 1. iDebate 앱 전체 구조

iDebate는 Streamlit으로 만든 챗봇 웹서비스입니다.

전체 흐름은 다음과 같습니다.

```text
사용자
  -> Streamlit 앱 app.py
  -> Streamlit Secrets에서 설정용 Google Sheet 주소 sheet_url 확인
  -> Google Sheet "정보" 시트에서 API KEY, model, 프롬프트 등 설정 읽기
  -> Anthropic Claude API 호출
  -> 응답을 Streamlit 화면에 표시
  -> 대화 기록을 Google Sheet에 저장
```

핵심 구성요소는 4개입니다.

| 구성요소 | 역할 |
|---|---|
| Streamlit 앱 | 사용자가 접속하는 챗봇 화면입니다. 주요 파일은 `app.py`입니다. |
| Streamlit Secrets | 앱별 비밀 설정을 저장합니다. Google service account 정보와 `sheet_url`이 들어갑니다. |
| Google Sheet 설정 파일 | `"정보"` 시트에 모델명, API KEY, 프롬프트, 서비스 on/off 값이 들어갑니다. |
| Anthropic Claude API | 실제 답변을 생성하는 AI API입니다. |

중요한 점:

- GitHub 코드 안에는 `idebate01`, `idebate02`, `idebate03`을 구분하는 코드가 없습니다.
- 앱별 차이는 Streamlit Cloud 각 앱의 Secrets, 특히 `sheet_url` 값으로 갈립니다.

## 2. 주요 파일 역할

| 파일 | 운영자가 알아야 할 역할 |
|---|---|
| `app.py` | Streamlit 화면, 사용자 입력, Claude API 호출을 담당합니다. |
| `utils/gs.py` | Google Sheet 인증과 설정값 읽기를 담당합니다. |
| `config.py` | Anthropic API 키를 Secrets에서 읽는 코드가 있으나, 현재 실제 채팅 흐름의 핵심은 `app.py`와 `utils/gs.py`입니다. |
| `requirements.txt` | 필요한 라이브러리 목록입니다. |

운영자가 평소에 직접 수정해야 하는 곳은 보통 GitHub 코드가 아니라 Google Sheet의 `"정보"` 시트입니다.

## 3. 설정값 위치

### 3.1 Streamlit Secrets의 `sheet_url`

`st.secrets["sheet_url"]`은 설정용 Google Sheet 주소입니다.

역할:

- 앱이 시작될 때 이 URL의 Google Sheet를 엽니다.
- 그 Sheet 안의 `"정보"` 워크시트에서 B열 설정값을 읽습니다.
- `idebate01`, `idebate02`, `idebate03`이 서로 다른 설정을 쓰려면 각 앱의 Secrets에 서로 다른 `sheet_url`이 들어 있어야 합니다.

예시 표기:

```text
sheet_url = [REDACTED]
```

절대 운영용 Google Sheet URL을 공개 문서나 외부 채팅에 원문으로 붙여넣지 마세요.

### 3.2 Google Sheet `"정보"` 시트 B열 설정값

앱은 설정용 Google Sheet의 `"정보"` 시트에서 B열 전체를 읽습니다.

현재 코드 기준 설정 위치는 다음과 같습니다.

| 위치 | 설정 이름 | 설명 | 보안 주의 |
|---|---|---|---|
| B1 | `url` | 대화 기록을 저장할 Google Sheet URL입니다. | 외부 공유 주의 |
| B2 | `serviceOnOff` | 서비스 사용 여부입니다. `on` 또는 `off`로 관리합니다. | 낮음 |
| B3 | `AI` | 사용할 AI 서비스 이름입니다. | 낮음 |
| B4 | `key` | Anthropic API KEY입니다. | 매우 높음, `[REDACTED]` |
| B5 | `model` | Anthropic Claude 모델명입니다. | 운영 중요 |
| B6 | `max_tokens` | 답변 최대 토큰 수입니다. 숫자여야 합니다. | 낮음 |
| B7 | `temperature` | 답변 다양성 설정입니다. 숫자여야 합니다. | 낮음 |
| B8 | `select` | 선택 옵션입니다. | 낮음 |
| B9 | `system` | Claude에 전달되는 시스템 프롬프트입니다. | 운영 중요 |
| B10 | `a_p` | 종합 평가용 프롬프트입니다. | 운영 중요 |
| B11 | `e_p` | 격려/평어 관련 프롬프트입니다. | 운영 중요 |
| B12 | `stream` | 스트리밍 응답 여부입니다. `true` 또는 `false`로 관리합니다. | 낮음 |

특히 중요한 셀:

- B4: API KEY입니다. 절대 외부에 공개하지 마세요.
- B5: 모델명입니다. Sonnet 4.6 변경 시 이 셀을 수정합니다.
- B2: 서비스 on/off입니다. 앱이 안 열리거나 중지 안내가 뜨면 먼저 확인합니다.

## 4. Anthropic Claude API 호출 흐름

Claude API 호출은 `app.py`에서 일어납니다.

운영자가 이해해야 할 흐름은 다음 정도면 충분합니다.

```text
Google Sheet "정보" 시트 B4
  -> API KEY
  -> Anthropic 클라이언트 생성

Google Sheet "정보" 시트 B5
  -> model
  -> Claude API 호출의 model 값
```

즉, 현재 구조에서는 모델명이 GitHub 코드에 직접 박혀 있지 않습니다.

운영자가 B5를 바꾸면 앱은 그 값을 읽어서 Claude API의 `model` 값으로 사용합니다. 다만 설정 읽기는 캐시될 수 있으므로 반영까지 약간의 시간이 걸릴 수 있습니다.

## 5. Sonnet 4.6으로 바꾸는 절차

목표 모델명:

```text
claude-sonnet-4-6
```

운영 절차:

1. 먼저 테스트용 앱 하나만 고릅니다.
2. Streamlit Cloud에서 그 앱의 Secrets를 엽니다.
3. `sheet_url` 값을 확인합니다.
4. 해당 Google Sheet를 엽니다.
5. `"정보"` 시트로 이동합니다.
6. B5 셀의 기존 모델명을 확인합니다.
7. B5 값을 `claude-sonnet-4-6`으로 바꿉니다.
8. 저장 후 약 5분 기다리거나 Streamlit 앱을 재부팅합니다.
9. 테스트 앱에서 짧은 질문을 보내 정상 응답을 확인합니다.
10. 오류가 없으면 `idebate01`, `idebate02`, `idebate03` 중 나머지 앱에도 같은 방식으로 순차 적용합니다.

권장 적용 순서:

```text
테스트 앱 1개
  -> 짧은 대화 테스트
  -> 오류 확인
  -> 두 번째 앱 적용
  -> 다시 테스트
  -> 세 번째 앱 적용
  -> 최종 테스트
```

주의:

- 세 앱을 동시에 바꾸지 마세요.
- 먼저 하나에서 정상 작동을 확인한 뒤 확대하세요.
- 모델명이 잘못되었거나 계정 권한이 없으면 Claude API 오류가 날 수 있습니다.
- 오류가 나면 B5 값을 이전 모델명으로 되돌린 뒤 다시 테스트하세요.

## 6. idebate01 / idebate02 / idebate03 설정 시트 찾는 법

GitHub 코드 안에는 `idebate01`, `idebate02`, `idebate03`을 구분하는 코드가 없습니다.

따라서 각 앱이 어떤 설정 Sheet를 쓰는지는 GitHub가 아니라 Streamlit Cloud에서 확인해야 합니다.

확인 방법:

1. Streamlit Cloud에 로그인합니다.
2. `idebate01` 앱 설정으로 들어갑니다.
3. Secrets 메뉴를 엽니다.
4. `sheet_url` 값을 찾습니다.
5. 이 URL이 `idebate01`의 설정용 Google Sheet입니다.
6. 같은 방법으로 `idebate02`, `idebate03`도 각각 확인합니다.

정리 표:

| 앱 | 어디서 확인하나 | 확인할 값 | 그 다음 볼 곳 |
|---|---|---|---|
| `idebate01` | Streamlit Cloud Secrets | `sheet_url` | 해당 Google Sheet의 `"정보"` 시트 |
| `idebate02` | Streamlit Cloud Secrets | `sheet_url` | 해당 Google Sheet의 `"정보"` 시트 |
| `idebate03` | Streamlit Cloud Secrets | `sheet_url` | 해당 Google Sheet의 `"정보"` 시트 |

문서화할 때는 이렇게 적으세요.

```text
idebate01 sheet_url = [REDACTED]
idebate02 sheet_url = [REDACTED]
idebate03 sheet_url = [REDACTED]
```

## 7. API KEY 보안 운영 규칙

현재 구조에서는 Google Sheet `"정보"` 시트 B4에 Anthropic API KEY가 들어갑니다.

이 구조의 위험:

- Google Sheet 접근 권한이 있는 사람이 API KEY를 볼 수 있습니다.
- Sheet URL이나 권한이 잘못 공유되면 API KEY가 노출될 수 있습니다.
- API KEY가 노출되면 외부인이 비용을 발생시킬 수 있습니다.

운영 규칙:

1. B4 API KEY는 절대 캡처, 메신저, 문서, 이메일에 원문으로 공유하지 마세요.
2. 공유가 필요하면 항상 `[REDACTED]`로 가리세요.
3. API KEY가 노출되었다고 의심되면 즉시 Anthropic 콘솔에서 폐기하세요.
4. 폐기 후 새 키를 발급받아 운영 설정에 반영하세요.
5. 누가 Google Sheet를 볼 수 있는지 정기적으로 확인하세요.
6. 퇴사자, 외부자, 임시 계정의 Sheet 접근 권한은 제거하세요.

장기 개선 권장:

- API KEY를 Google Sheet B4에 두지 말고 Streamlit Secrets로 옮기는 것을 권장합니다.
- 예: `ANTHROPIC_API_KEY = [REDACTED]`
- 이렇게 하면 Sheet 편집자가 API KEY를 직접 볼 필요가 줄어듭니다.
- 이 개선은 코드 수정이 필요할 수 있으므로 개발자와 별도 일정으로 진행하세요.

## 8. 앱이 안 될 때 비개발자용 점검 체크리스트

아래 순서대로 확인하세요. GitHub 코드는 가장 마지막에 봅니다.

### 1단계: Streamlit 앱 상태 확인

- 앱 페이지가 열리는지 확인합니다.
- Streamlit Cloud에서 앱이 sleeping, rebooting, error 상태인지 확인합니다.
- 필요하면 앱을 재부팅합니다.

### 2단계: `sheet_url` 확인

- Streamlit Cloud의 해당 앱 Secrets를 엽니다.
- `sheet_url`이 비어 있지 않은지 확인합니다.
- `sheet_url`이 올바른 설정용 Google Sheet를 가리키는지 확인합니다.
- URL 원문은 외부에 공유하지 않습니다.

### 3단계: Google Sheet 접근 권한 확인

- 설정용 Google Sheet가 열리는지 확인합니다.
- Google service account가 해당 Sheet에 접근 권한을 가지고 있는지 확인합니다.
- 최근 Sheet 권한을 바꾼 적이 있다면 권한 문제일 수 있습니다.

### 4단계: 서비스 여부 `on` 확인

- 설정용 Google Sheet의 `"정보"` 시트를 엽니다.
- B2 셀 `serviceOnOff` 값을 확인합니다.
- 서비스하려면 `on`이어야 합니다.
- `off`이면 앱이 의도적으로 중지 상태가 됩니다.

### 5단계: `model` 값 확인

- `"정보"` 시트 B5를 확인합니다.
- Sonnet 4.6 적용 시 값은 `claude-sonnet-4-6`이어야 합니다.
- 모델명에 공백, 오타, 줄바꿈이 들어가지 않았는지 확인합니다.
- 오류가 나면 이전에 정상 작동하던 모델명으로 되돌려 테스트합니다.

### 6단계: API KEY 확인

- `"정보"` 시트 B4가 비어 있지 않은지 확인합니다.
- API KEY 원문은 공유하지 않습니다.
- 키가 만료, 폐기, 권한 없음 상태일 수 있습니다.
- 노출 의심 시 즉시 폐기하고 재발급합니다.

예시 표기:

```text
API KEY = [REDACTED]
```

### 7단계: 숫자 설정 확인

- B6 `max_tokens`는 숫자여야 합니다.
- B7 `temperature`도 숫자여야 합니다.
- 잘못된 문자나 빈칸이면 앱 오류가 날 수 있습니다.

### 8단계: Streamlit 재부팅

- 설정을 바꾼 뒤 바로 반영되지 않을 수 있습니다.
- 약 5분 기다리거나 Streamlit Cloud에서 앱을 재부팅하세요.

### 9단계: 짧은 테스트 대화

- 긴 질문보다 짧은 질문으로 먼저 확인합니다.
- 예: `안녕하세요`
- 정상 응답이 오면 모델/API/Sheet 기본 연결은 살아 있는 것입니다.

### 10단계: GitHub 코드는 마지막에 확인

아래 경우에만 GitHub 코드 확인이 필요할 가능성이 큽니다.

- 세 앱 모두 같은 오류가 발생합니다.
- Sheet와 Secrets 값이 정상인데도 계속 실패합니다.
- 최근 GitHub 배포 이후 갑자기 실패하기 시작했습니다.
- 라이브러리 버전 또는 Claude API 방식이 바뀌었습니다.

## 9. 운영자가 기억할 한 줄 요약

모델 변경은 GitHub 코드가 아니라 각 앱의 Streamlit Secrets `sheet_url`이 가리키는 Google Sheet `"정보"` 시트 B5에서 합니다.

```text
Streamlit 앱별 Secrets sheet_url
  -> Google Sheet "정보" 시트
  -> B5 model
  -> Claude API 호출 모델
```

API KEY는 현재 `"정보"` 시트 B4에 있으므로, 보안상 항상 `[REDACTED]`로 다루고 장기적으로는 Streamlit Secrets로 옮기는 개선을 권장합니다.

## 10. 2026-06-16 운영 복구 완료 상태

오늘 기준으로 아래 운영 복구가 완료되었습니다.

| 대상 | 완료 상태 |
|---|---|
| `idebate.streamlit.app` | GitHub `mhroh/idebate`, branch `main`, main file `app.py` 실행 확인. 설정 시트는 `iDebate 00.수업할 시트 설정`. model은 `claude-sonnet-4-6`. 시각화 도구 UI 제거 후 정상 작동 확인. |
| `idebate01` / `ddd01` | 기존에는 `idebate03` 설정 시트를 함께 보고 있었음. `idebate03` 설정 시트를 복사해 `idebate01. 00.수업할 시트 설정`을 새로 생성함. 생성 위치는 Google Drive `idebate01` 폴더. `ddd01` Streamlit Secrets의 `sheet_url`을 새 idebate01 설정 시트 URL로 교체함. model은 `claude-sonnet-4-6`. 정상 작동 확인. |
| `idebate02` / `ddd02` | model은 `claude-sonnet-4-6`. 정상 작동 확인. |
| `idebate03` / `ddd03` | 설정 시트는 `idebate03. 00.수업할 시트 설정`. model은 `claude-sonnet-4-6`. 정상 작동 확인. 해당 시트는 Google Drive `idebate03` 폴더로 이동해 정리함. |

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

운영자가 앞으로 기억할 점:

- 각 앱의 실제 설정 시트는 Streamlit Secrets의 `sheet_url`로 결정됩니다.
- 전체 `sheet_url`, 전체 `client_email`, `private_key`, token, API KEY 원문은 문서에 기록하지 않습니다.
- 민감값을 기록해야 할 것 같으면 반드시 `[REDACTED]`로 처리합니다.

## 11. 캐싱 및 세션 상태 점검 결과

작성일: 2026-06-16

### 11.1 코드에서 확인된 캐싱 종류

현재 코드(`app.py`, `utils/gs.py`)에서 발견된 캐싱은 다음 3가지입니다.

| 위치 | 방식 | 캐시 유지 범위 | 만료 조건 |
|---|---|---|---|
| `utils/gs.py` `get_authorize()` | `@st.cache_resource` | 앱 프로세스 전체 | 앱 Reboot 시만 초기화됨 |
| `utils/gs.py` `getSetupInfo()` | `@st.cache_data(ttl=300)` | 앱 프로세스 전체 | 5분(300초) 경과 또는 앱 Reboot 시 초기화됨 |
| `app.py` `log_p()` | `@st.cache_data` | 앱 프로세스 전체 | 앱 Reboot 시만 초기화됨 (로그 기능 전용, 운영 영향 없음) |

`functools` 캐시는 `app.py`에서 `functools.wraps`가 데코레이터 패턴으로만 쓰이고 있으며, 실제 설정값 캐싱에는 사용되지 않습니다.

### 11.2 `st.session_state['setupInfo']`의 생성 및 갱신 시점

`setupInfo`는 `app.py`의 `main()` 함수 첫 줄에서 아래 조건으로 생성됩니다.

```python
if "setupInfo" not in st.session_state:
    set_class_info()
```

- **생성**: 해당 브라우저 탭에서 세션이 처음 시작될 때 1회 생성됩니다.
- **갱신**: 세션이 살아있는 동안은 절대 갱신되지 않습니다. Google Sheet 값을 바꿔도 현재 세션의 `setupInfo`는 그대로입니다.
- **초기화**: 브라우저 탭을 닫고 다시 열거나, 앱 Reboot 이후 새 세션이 시작될 때만 새 값을 읽어옵니다.

즉, 현재 접속 중인 사용자는 설정을 바꿔도 해당 세션이 끝날 때까지 이전 설정으로 대화가 진행됩니다.

### 11.3 시스템 프롬프트(`messages`)의 초기화 시점

대화 기록 `st.session_state.messages`는 아래 조건으로 초기화됩니다.

```python
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": st.session_state["setupInfo"]['system']}]
```

- 세션 시작 후 최초 1회만 `system` 프롬프트가 설정됩니다.
- `system` 값을 Google Sheet에서 바꿔도 현재 진행 중인 대화의 시스템 프롬프트는 바뀌지 않습니다.
- 새 대화(새 세션)부터 반영됩니다.

### 11.4 Google Sheet 설정 변경 후 반영 여부 요약

| 변경 항목 | 브라우저 새로고침만으로 반영되나? | Rerun으로 반영되나? | 확실히 반영되는 시점 |
|---|---|---|---|
| `model` (B5) | 아니오 | 아니오 | 5분 경과 후 새 세션, 또는 앱 Reboot 후 새 세션 |
| `system` (B9) | 아니오 | 아니오 | 5분 경과 후 새 세션, 또는 앱 Reboot 후 새 세션 |
| `select` (B8) | 아니오 | 아니오 | 5분 경과 후 새 세션, 또는 앱 Reboot 후 새 세션 |
| `serviceOnOff` (B2) | 아니오 | 아니오 | 5분 경과 후 새 세션, 또는 앱 Reboot 후 새 세션 |
| `key` / API KEY (B4) | 아니오 | 아니오 | 5분 경과 후 새 세션, 또는 앱 Reboot 후 새 세션 |
| Streamlit Secrets의 `sheet_url` | 아니오 | 아니오 | 앱 Reboot 필수 |

**브라우저 새로고침**은 Streamlit 세션 자체를 재시작하지만, `@st.cache_data`·`@st.cache_resource` 캐시는 앱 프로세스 수준이므로 새로고침으로 초기화되지 않습니다. 새 세션이 시작되어도 5분 내라면 캐시된 설정값을 그대로 읽습니다.

**Rerun**은 Streamlit Cloud Manage app 패널의 Rerun 버튼으로, 스크립트를 재실행하지만 세션 상태와 캐시는 그대로 유지됩니다. 설정 변경 반영에는 효과가 없습니다.

**Reboot**은 앱 서버 프로세스를 완전히 재시작합니다. 모든 캐시(`@st.cache_data`, `@st.cache_resource`)와 모든 세션 상태(`st.session_state`)가 초기화됩니다. Reboot 이후 처음 접속하는 사람부터 최신 Google Sheet 값을 읽습니다.

### 11.5 `sheet_url` 변경 후 예전 설정이 보일 수 있는 원인

Streamlit Secrets의 `sheet_url`을 변경했는데도 예전 설정이 보이는 경우의 원인 후보입니다.

1. **앱 Reboot 미실행**: `sheet_url` 변경은 반드시 앱 Reboot이 있어야 반영됩니다. Rerun만으로는 반영되지 않습니다.
2. **`@st.cache_resource` 캐시 잔존**: `get_authorize()`가 캐시되어 있어 새 `sheet_url`로 재인증하지 않고 이전 연결을 재사용합니다. Reboot 없이는 해결되지 않습니다.
3. **`@st.cache_data` TTL 잔존**: `getSetupInfo()`가 5분 캐시이므로 Reboot 없이 TTL 내에 접속하면 이전 Sheet 데이터를 읽습니다.
4. **세션 상태 잔존**: Reboot 이전에 이미 접속 중이던 사용자는 기존 `setupInfo`를 그대로 사용합니다.

### 11.6 설정 변경 후 권장 반영 절차

#### model 변경 후 확인 절차

1. 해당 앱의 Streamlit Secrets에서 `sheet_url`이 가리키는 Google Sheet를 엽니다.
2. `"정보"` 시트 B5 값을 원하는 모델명으로 수정합니다. 예: `claude-sonnet-4-6`
3. Streamlit Cloud Manage app 패널에서 해당 앱을 **Reboot**합니다.
4. Reboot 완료 후 앱에 새 브라우저 탭으로 접속합니다.
5. 짧은 질문을 입력해 응답이 오는지 확인합니다.
6. 오류가 없으면 반영 완료입니다.

#### select 변경 후 확인 절차

1. 해당 앱의 Google Sheet `"정보"` 시트 B8 값을 수정합니다.
2. Streamlit Cloud에서 해당 앱을 **Reboot**합니다.
3. Reboot 완료 후 새 브라우저 탭으로 접속해 `select` 값이 반영되었는지 확인합니다.

`select` 값은 `st.session_state['setupInfo']['select']`로 접근되며, Reboot 없이는 새 세션에서도 5분 이내라면 이전 값이 사용될 수 있습니다.

#### sheet_url 변경 후 확인 절차

1. Streamlit Cloud 해당 앱의 Secrets에서 `sheet_url`을 새 Google Sheet URL로 수정하고 저장합니다.
2. 반드시 해당 앱을 **Reboot**합니다. (Rerun은 효과 없음)
3. Reboot 완료 후 새 브라우저 탭으로 접속합니다.
4. 앱이 정상 로드되면 새 `sheet_url`이 반영된 것입니다.
5. 앱이 오류 없이 대화 가능한지 짧은 질문으로 확인합니다.

### 11.7 문제 발생 시 권장 순서

아래 순서대로 시도합니다.

```text
1단계: 브라우저 새로고침 (F5 또는 Ctrl+R)
  -> 세션을 새로 시작하므로 새 설정을 읽을 가능성 있음
  -> 단, 5분 캐시가 살아있으면 Google Sheet 최신값이 아닐 수 있음

2단계: Streamlit Manage app → Rerun
  -> 스크립트를 재실행하지만 캐시·세션 상태는 유지됨
  -> 설정 변경 반영에는 효과 없음
  -> 화면이나 상태 이상 증상 해소에 시도해볼 수 있음

3단계: Streamlit Manage app → Reboot
  -> 앱 프로세스 전체 재시작
  -> 모든 캐시(get_authorize, getSetupInfo)와 세션 상태 초기화
  -> 설정 변경이 확실히 반영되어야 할 때 사용
  -> Reboot 후 첫 접속자부터 최신 Google Sheet 값을 읽음
```

일반 운영 시 설정 변경은 **Reboot**으로 마무리하는 것을 권장합니다. 5분을 기다리는 방법은 TTL이 지난 후 새 세션이 필요하므로, 기존 접속자에게는 여전히 반영되지 않습니다.

### 11.8 운영상 주의사항

1. **`getSetupInfo()` 5분 캐시**: Google Sheet 설정을 바꾼 직후에는 최대 5분간 이전 값이 사용됩니다. 즉각 반영이 필요하면 Reboot을 사용하세요.
2. **세션 중 설정 불변**: 현재 접속 중인 사용자의 `model`, `system`, `select`는 세션이 끝날 때까지 바뀌지 않습니다. Reboot을 해도 이미 접속 중인 탭은 영향을 받지 않습니다. 새 탭으로 재접속해야 합니다.
3. **`get_authorize()` 영구 캐시**: Google 인증 클라이언트는 Reboot 없이는 갱신되지 않습니다. service account 정보나 `sheet_url`을 바꾼 경우 반드시 Reboot이 필요합니다.
4. **수업 중 Reboot 주의**: Reboot을 하면 현재 대화 중인 모든 사용자의 세션이 초기화됩니다. 수업 중에는 Reboot을 피하고, 수업 전후에 진행하세요.

