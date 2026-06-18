import functools
import streamlit as st
from streamlit import logger
import anthropic
from anthropic import APIError, APIConnectionError, APITimeoutError, RateLimitError, APIStatusError
from utils import gs
import time
from datetime import datetime, timezone, timedelta

if "processing" not in st.session_state:
    st.session_state.processing = False

def disable_input(value):
    st.session_state.processing = value

def now_kst():
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst)

def format_elapsed(seconds):
    if seconds is None:
        return "-"

    seconds = max(0, int(round(seconds)))
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"

def format_message_meta(role, meta):
    meta = meta or {}

    timestamp = meta.get("timestamp")
    timestamp_text = timestamp.strftime("%H:%M:%S") if timestamp else "--:--:--"
    elapsed_text = format_elapsed(meta.get("elapsed_seconds"))
    if role == "user":
        return f"입력 시각 {timestamp_text} · 생각 소요 {elapsed_text}"
    if role == "assistant":
        return f"응답 시각 {timestamp_text} · 생성 소요 {elapsed_text}"
    return ""

def build_conversation_txt(messages, message_meta=None, user_name=None):
    created_at = now_kst().strftime("%Y-%m-%d %H:%M:%S KST")
    display_name = user_name or "unknown"
    role_labels = {
        "user": "[학생]",
        "assistant": "[챗봇]",
    }
    lines = [
        f"대화명: {display_name}",
        f"생성 시각: {created_at}",
        "",
    ]

    message_meta = message_meta or {}

    for idx, message in enumerate(messages):
        role = message.get("role")
        if role not in role_labels:
            continue

        content = str(message.get("content", "")).strip()
        lines.append(role_labels[role])
        meta_text = format_message_meta(role, message_meta.get(idx))
        if meta_text:
            lines.append(meta_text)
        lines.append(content)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"

def initialize(api_key, nick_name):
    """
    애플리케이션의 초기 설정을 수행하는 함수입니다. ...

    Parameters:
    api_key (str): Anthropic API 키
    nick_name (str): 사용자의 닉네임

    이 함수는 다음과 같은 작업을 수행합니다:
    1. Anthropic API 클라이언트를 초기화합니다.
    2. Google Sheets 연결을 설정합니다.
    3. 사용자별 워크시트를 가져오거나 생성합니다.

    이 함수는 이미 초기화가 완료된 경우 아무 작업도 수행하지 않습니다.
    """
    if "bot" and "sheet" in st.session_state:
        return
    
    log_p("초기화 시작")
    # Anthropic
    st.session_state["api_key"] = api_key
    st.session_state["bot"] = anthropic.Anthropic(api_key = api_key)
    st.session_state["user_name_1"] = nick_name

    # Google Spread Sheet
    gc = gs.get_authorize()
    sheet_url = st.session_state["setupInfo"]["url"]
    st.session_state["doc"] = gc.open_by_url(sheet_url)
    st.session_state["sheet"] = gs.get_worksheet(st.session_state["doc"], nick_name)
    log_p("초기화 완료")

def set_class_info():
    log_p("클래스 정보 설정")
    st.session_state['setupInfo'] = gs.getSetupInfo()

def process_data(function_name):
    with st.spinner('마무리 하는 중~'):
        function_name()
    st.success("완료.")


def hide_streamlit_chrome():
    st.markdown(
        """
        <style>
        [data-testid="stToolbar"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }
        [data-testid="stDecoration"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }
        [data-testid="stStatusWidget"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }
        [data-testid="stHeader"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }
        #MainMenu {
            display: none !important;
            visibility: hidden !important;
        }
        footer {
            display: none !important;
            visibility: hidden !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    hide_streamlit_chrome()

    if "setupInfo" not in st.session_state:
        set_class_info()

    if "message_meta" not in st.session_state:
        st.session_state.message_meta = {}

    if "last_assistant_done_at" not in st.session_state:
        st.session_state.last_assistant_done_at = now_kst()

    if st.session_state["setupInfo"]["serviceOnOff"] == "off":
        st.title("❤🥰지금은 휴식중입니다.🥰❤")
        return

    # 사이드바 
    # user_name = ''

    with st.sidebar:
        # 페이지 제목 설정
        st.title("교육용 챗봇")

        api_key = st.session_state["setupInfo"]["key"]
        user_name = st.text_input("대화명을 입력하세요:")

        if api_key and user_name:
            initialize(api_key, user_name)

        if "messages" in st.session_state and len(st.session_state.messages) > 1:
            conversation_user_name = st.session_state.get("user_name_1", user_name)
            current_time = now_kst()
            safe_user_name = "".join(
                char if char.isalnum() or char in ("-", "_") else "_"
                for char in str(conversation_user_name or "unknown")
            )
            file_name = f"idebate_conversation_{safe_user_name}_{current_time.strftime('%Y%m%d_%H%M%S')}.txt"
            st.download_button(
                "대화 TXT 다운로드",
                data=build_conversation_txt(
                    st.session_state.messages,
                    st.session_state.message_meta,
                    conversation_user_name,
                ).encode("utf-8-sig"),
                file_name=file_name,
                mime="text/plain",
                disabled=st.session_state.processing,
            )


    # 시스템 메시지 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": st.session_state["setupInfo"]['system']}]

    # 챗 메시지 출력
    for idx, message in enumerate(st.session_state.messages):
        if idx > 0:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "user":
                    meta_text = format_message_meta(
                        message["role"],
                        st.session_state.message_meta.get(idx),
                    )
                    if meta_text:
                        st.caption(meta_text)

    if prompt := st.chat_input("대화 내용을 입력해 주세요.", on_submit=disable_input, args=(True,), disabled=st.session_state.processing):
        if not user_name:
            st.warning('대화명을 입력해 주세요!', icon='⚠️')

            time.sleep(3)
            disable_input(False)
            st.rerun()

            return

        user_message_idx = len(st.session_state.messages)
        user_timestamp = now_kst()
        last_assistant_done_at = st.session_state.get("last_assistant_done_at")
        add_message(st.session_state.messages, "user", prompt)
        st.session_state.message_meta[user_message_idx] = {
            "timestamp": user_timestamp,
            "elapsed_seconds": (user_timestamp - last_assistant_done_at).total_seconds() if last_assistant_done_at else None,
        }

        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(format_message_meta("user", st.session_state.message_meta[user_message_idx]))

        # OpenAI 모델 호출
        if "api_key" in st.session_state:
            full_response = ""
            # setupInfo = st.session_state['setupInfo']

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.write("......")
                assistant_started_at = time.perf_counter()
                stream = execute_prompt(st.session_state.messages[1:])

                if stream == None:
                    delete_message()

                    disable_input(False)
                    time.sleep(3)
                    st.rerun()

                    return

                full_response = message_processing(stream, message_placeholder)
                message_placeholder.write(full_response)

            assistant_message_idx = len(st.session_state.messages)
            assistant_timestamp = now_kst()
            assistant_elapsed = time.perf_counter() - assistant_started_at
            add_message(st.session_state.messages, "assistant", full_response)
            st.session_state.message_meta[assistant_message_idx] = {
                "timestamp": assistant_timestamp,
                "elapsed_seconds": assistant_elapsed,
            }
            st.session_state.last_assistant_done_at = assistant_timestamp
            disable_input(False)
            st.rerun()

@st.cache_data 
def log_p(message):
    """
    콘솔에 메세지 출력하기
    """
    logger.get_logger(__name__).info(message)

def execute_prompt(messages):
    """
    AI 모델에 프롬프트를 전송하고 응답 스트림을 받아오는 함수입니다.

    Parameters:
    messages (list): 대화 기록을 담고 있는 메시지 리스트. 각 메시지는 'role'과 'content' 키를 가진 딕셔너리 형태입니다.

    Returns:
    stream: AI 모델의 응답 스트림

    이 함수는 세션 상태에서 설정 정보와 AI 클라이언트를 가져와 사용합니다.
    설정된 파라미터에 따라 AI 모델에 요청을 보내고, 응답 스트림을 반환합니다.
    """
    setupInfo = st.session_state['setupInfo']
    client = st.session_state["bot"]
    
    try:
        stream = client.messages.create(
                        model = setupInfo['model'],
                        max_tokens = setupInfo['max_tokens'],
                        temperature = setupInfo['temperature'],
                        system = setupInfo['system'],
                        messages = messages,
                        stream = setupInfo['stream']
        )

        return stream
    except APITimeoutError as e:
        log_p(f"ERROR: API 타임아웃 오류 발생: {str(e)}")
        st.error("AI 서비스의 응답이 너무 오래 걸립니다. 잠시 후 다시 시도해 주세요.")
    except APIConnectionError as e:
        log_p(f"ERROR: API 연결 오류 발생: {str(e)}")
        st.error("AI 서비스와의 연결에 실패했습니다. 인터넷 연결을 확인해 주세요.")
    except RateLimitError as e:
        log_p(f"ERROR: API 사용량 제한 오류 발생: {str(e)}")
        st.error("AI 서비스 사용량이 한도를 초과했습니다. 잠시 후 다시 시도해 주세요.")
    except APIStatusError as e:
        log_p(f"API 상태 오류가 발생했습니다. 상태 코드: {e.status_code}, 오류 메시지: {e.message}")
        st.error(f"API 상태 오류가 발생했습니다. 상태 코드: {e.status_code}, 오류 메시지: {e.message}")
    except APIError as e:
        log_p(f"ERROR: API 오류 발생: {str(e)}")
        st.error("AI 서비스와 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")
    except Exception as e:
        log_p(f"ERROR:예상치 못한 오류 발생: {str(e)}")
        st.error("예상치 못한 오류가 발생했습니다. 관리자에게 문의해 주세요.")
    finally:
        pass

    return None

def wiget_on_off(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        st.session_state["processing"] = True
        
        result = func(*args, **kwargs)

        st.session_state["processing"] = False
        return result    
    return wrapper

def message_processing(stream, output = None):
    """
    스트리밍 응답을 처리하고 전체 응답을 구성하는 함수입니다.

    Parameters:
    stream (iterable): 응답 청크를 포함하는 스트림 객체
    output (streamlit.delta_generator.DeltaGenerator, optional): Streamlit 출력 객체. 기본값은 None입니다.

    Returns:
    str: 완성된 전체 응답 문자열

    이 함수는 스트림에서 청크를 반복적으로 읽어 전체 응답을 구성합니다.
    또한 Streamlit 출력 객체가 제공된 경우, 실시간으로 응답을 업데이트합니다.
    """
    log_p("메시지 스트리밍 중")
    full_response = ""

    for chunk in stream:
        if chunk.type == "content_block_delta":
            full_response += chunk.delta.text
        elif chunk.type == "message_start":
            # 메시지 시작 이벤트 처리 (필요한 경우)
            pass
        elif chunk.type == "message_delta":
            # 메시지 델타 이벤트 처리 (필요한 경우)
            pass
        elif chunk.type == "message_stop":
            # 메시지 종료 이벤트 처리 (필요한 경우)
            break
        if output != None:
            output.write(full_response + "▌")
    log_p("메시지 스트리밍 완료")

    return full_response

def end_conversation():
    """
    대화를 종료하고 종합 평가 및 평어를 생성하여 Google Sheets에 저장하는 함수입니다.

    이 함수는 다음과 같은 작업을 수행합니다:
    1. 종합 평가 프롬프트를 사용하여 AI로부터 종합 평가를 생성합니다.
    2. 생성된 종합 평가를 Google Sheets에 저장합니다.
    3. 평어 프롬프트를 사용하여 AI로부터 평어를 생성합니다.
    4. 생성된 평어를 Google Sheets에 저장합니다.

    이 함수는 세션 상태에 저장된 설정 정보와 메시지 기록을 사용합니다.
    """
    st.success("1/2 작업중......")
    time.sleep(2)
    st.success("1/2 완료")
    time.sleep(2)
    st.success("2/2 작업중......")
    time.sleep(2)
    st.success("2/2 완료")
    time.sleep(2)
    
    return 

    log_p("평가 시작")

    # TODO 종합평가, 평어를 시트에 저장
    sheet = gs.get_summary_sheet(st.session_state["doc"])
    setupInfo = st.session_state['setupInfo']
    a_p = setupInfo["a_p"]
    e_p = setupInfo["e_p"]
    messages = st.session_state.messages[1:]
    full_response = ""

    # 종합평가
    st.success("1/2 작업중......")
    add_message(messages, "user", a_p)
    stream = execute_prompt(messages)
    full_response = message_processing(stream)
    add_message(messages, "assistant", full_response)
    
    cell = sheet.find(st.session_state["user_name_1"], in_column = 1)
    sheet.update_cell(cell.row, cell.col + 1, full_response)
    st.success("1/2 완료")
    
    # 평어
    st.success("2/2 작업중......")
    full_response = ""
    add_message(messages, "user", e_p)
    stream = execute_prompt(messages)
    full_response = message_processing(stream)
    add_message(messages, "assistant", full_response)

    sheet.update_cell(cell.row, cell.col + 2, full_response)
    st.success("2/2 완료")
    log_p("평가 완료")

def add_message(all_messages, role, message):
    """
    메시지를 현재 브라우저 세션의 대화 기록에만 추가합니다.
    Google Sheet 자동저장은 개인정보보호/속도 문제로 테스트 브랜치에서 비활성화했습니다.
    """
    all_messages.append({"role": role, "content": message})

def delete_message():
    message = st.session_state.messages

    while message[-1]["role"] == "user":
        removed_idx = len(message) - 1
        message.pop()
        st.session_state.message_meta.pop(removed_idx, None)


if __name__ == "__main__":
    main()
