import functools
import streamlit as st
from streamlit import logger
import anthropic
from anthropic import APIError, APIConnectionError, APITimeoutError, RateLimitError, APIStatusError
from utils import gs
import time

if "processing" not in st.session_state:
    st.session_state.processing = False

def disable_input(value):
    st.session_state.processing = value

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


def main():
    if "setupInfo" not in st.session_state:
        set_class_info()
        
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

        if st.button("대화 종료", on_click=disable_input, args=(True,), disabled=st.session_state.processing):
            process_data(end_conversation)


    # 시스템 메시지 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": st.session_state["setupInfo"]['system']}]

    # 챗 메시지 출력
    for idx, message in enumerate(st.session_state.messages):
        if idx > 0:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("대화 내용을 입력해 주세요.", on_submit=disable_input, args=(True,), disabled=st.session_state.processing):
        if not user_name:
            st.warning('대화명을 입력해 주세요!', icon='⚠️')

            time.sleep(3)
            disable_input(False)
            st.rerun()

            return
        
        add_message(st.session_state.messages, "user", prompt)
        
        with st.chat_message("user"):
            st.markdown(prompt)

        # OpenAI 모델 호출
        if "api_key" in st.session_state:
            full_response = ""
            # setupInfo = st.session_state['setupInfo']

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.write("......")
                stream = execute_prompt(st.session_state.messages[1:])

                if stream == None:
                    delete_message()

                    disable_input(False)
                    time.sleep(3)
                    st.rerun()

                    return

                full_response = message_processing(stream, message_placeholder)
                message_placeholder.write(full_response)

            add_message(st.session_state.messages, "assistant", full_response)
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
    add_message(messages, "user", a_p, withGS = False)
    stream = execute_prompt(messages)
    full_response = message_processing(stream)
    add_message(messages, "assistant", full_response, withGS = False)
    
    cell = sheet.find(st.session_state["user_name_1"], in_column = 1)
    sheet.update_cell(cell.row, cell.col + 1, full_response)
    st.success("1/2 완료")
    
    # 평어
    st.success("2/2 작업중......")
    full_response = ""
    add_message(messages, "user", e_p, withGS = False)
    stream = execute_prompt(messages)
    full_response = message_processing(stream)
    add_message(messages, "assistant", full_response, withGS = False)

    sheet.update_cell(cell.row, cell.col + 2, full_response)
    st.success("2/2 완료")
    log_p("평가 완료")

def add_message(all_messages, role, message, withGS : bool = True):
    """
    메시지를 대화 기록에 추가하고 Google Sheets에도 저장하는 함수입니다.

    Parameters:
    all_messages (list): 전체 대화 기록을 저장하는 리스트
    role (str): 메시지 작성자의 역할 ("user" 또는 "assistant")
    message (str): 추가할 메시지 내용

    이 함수는 새 메시지를 all_messages 리스트에 추가하고,
    동시에 Google Sheets에도 해당 메시지를 저장합니다.
    """
    all_messages.append({"role": role, "content": message})
    if withGS:
        gs.add_Content(role, message)

def delete_message():
    message = st.session_state.messages

    while message[-1]["role"] == "user":
        message.pop()


if __name__ == "__main__":
    main()
