import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from zoneinfo import ZoneInfo

def get_authorize():
    """
    Google Sheets API에 접근하기 위한 인증된 gspread 클라이언트를 생성하는 함수입니다.

    Returns:
        gspread.Client: 인증된 gspread 클라이언트 객체

    이 함수는 다음과 같은 작업을 수행합니다:
    1. Streamlit의 secrets에서 서비스 계정 키 정보를 가져옵니다.
    2. 가져온 정보를 사용하여 Credentials 객체를 생성합니다.
    3. 생성된 Credentials를 사용하여 인증된 gspread 클라이언트를 반환합니다.

    Note:
    - 이 함수는 Streamlit의 st.secrets를 사용하여 민감한 인증 정보를 안전하게 관리합니다.
    - Google Sheets API에 대한 접근 범위는 'https://www.googleapis.com/auth/spreadsheets'로 설정됩니다.
    """
    
    # 서비스 계정 key 정보를 딕셔너리 형태로 정의합니다.
    service_account_info = {
        "type": st.secrets["type"],
        "project_id": st.secrets["project_id"],
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"],
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"],
        "universe_domain": st.secrets["universe_domain"]
    }

    # Credentials 객체 생성
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

    # gspread 클라이언트 생성
    return gspread.authorize(creds)

def getSetupInfo():
    """
    Google Sheets에서 설정 정보를 가져오는 함수입니다.

    Returns:
        dict: 다음 키를 포함하는 설정 정보 딕셔너리
            - url: 수업할 시트의 URL
            - serviceOnOff: 서비스 활성화 여부
            - AI: 사용할 생성형 AI 서비스 이름
            - key: API 키
            - model: 사용할 AI 모델
            - max_tokens: 최대 토큰 수 (정수)
            - temperature: 온도 설정 (부동소수점)
            - select: 선택 옵션
            - system: 시스템 프롬프트
            - a_p: 종합 평가 프롬프트
            - e_p: 평어 프롬프트
            - stream: 스트리밍 모드 사용 여부 (불리언)

    Note:
    - 이 함수는 st.secrets["sheet_url"]에 저장된 URL의 Google Sheets에서 정보를 가져옵니다.
    - "정보" 워크시트의 2번째 열에서 데이터를 읽어옵니다.
    - 데이터는 0부터 11까지의 인덱스로 구성되며, 각 인덱스는 주석에 설명된 정보를 나타냅니다.
    0 수업할 시트
    1 서비스 여부
    2 생성형AI
    3 API KEY
    4 model
    5 max_tokens
    6 temperature
    7 select
    8 system
    9 a_p
    10 e_p
    11 stream
    """

    gc = get_authorize()
    ws = gc.open_by_url(st.secrets["sheet_url"]).worksheet("정보")
    
    # 정보 데이터 가져오기
    data = ws.col_values(2)
    temp = {}
    temp["url"] = data[0]
    temp["serviceOnOff"] = data[1].lower()
    temp["AI"] = data[2]
    temp["key"] = data[3]
    temp["model"] = data[4]
    temp["max_tokens"] = int(data[5])
    temp["temperature"] = float(data[6])
    temp["select"] = data[7]
    temp["system"] = data[8]
    temp["a_p"] = data[9]
    temp["e_p"] = data[10]
    temp["stream"] = True if data[11].lower() == 'true' else False   
    
    return temp

def add_Content(role, content):
    """
    대화 내용을 Google Sheets에 추가하는 함수입니다.

    Parameters:
        role (str): 메시지 작성자의 역할. "user" 또는 "assistant" 중 하나여야 합니다.
        content (str): 추가할 메시지 내용

    이 함수는 현재 시간, 역할, 그리고 메시지 내용을 포함하는 새로운 행을
    세션 상태에 저장된 Google Sheets 워크시트에 추가합니다.
    """
    contents = [get_timestamp()]

    if role == "user":
        contents += ["USER", content]
    elif role == "assistant":
        contents +=["ASSISTANT", content]

    st.session_state["sheet"].append_row(contents)

def get_timestamp():
    """
    현재 시간을 아시아/서울 시간대 기준으로 "시:분" 형식의 문자열로 반환합니다.

    Returns:
        str: "HH:MM" 형식의 현재 시간 문자열
    """
    return datetime.now(ZoneInfo("Asia/Seoul")).strftime("%H:%M")

def get_worksheet(doc, name):
    """
    Google Sheets 문서에서 특정 이름의 워크시트를 찾거나 생성하는 함수입니다.

    Parameters:
        doc (gspread.Spreadsheet): 워크시트를 찾을 Google Sheets 문서 객체
        name (str): 찾거나 생성할 워크시트의 이름

    Returns:
        gspread.Worksheet: 기본 워크시트 또는 새로 생성한 워크시트 객체

    이 함수는 먼저 주어진 이름의 워크시트를 찾습니다. 
    없으면 '템플릿' 시트를 복사하여 새 워크시트를 생성하고, 
    생성된 시트로의 하이퍼링크를 '수업요약' 시트에 추가합니다.
    """
    for sheet in doc.worksheets():
        if sheet.title == name:
            print("시트 찾음")
            return sheet

    # 복사할 원본 시트 선택
    source_worksheet = doc.worksheet('템플릿')
    # 새 시트 생성 (원본 시트 복사)
    new_worksheet = doc.duplicate_sheet(
        source_worksheet.id, 
        insert_sheet_index = 100, 
        new_sheet_name = name
    )

    add_Hyperlink(doc, new_worksheet.id, name)

    return new_worksheet

def add_Hyperlink(doc, id, nick_name):
    """
    Google Sheets 문서에 하이퍼링크를 추가하는 함수입니다.

    Parameters:
        doc (gspread.Spreadsheet): 하이퍼링크를 추가할 Google Sheets 문서 객체
        id (str): 링크의 대상이 될 시트의 gid
        nick_name (str): 하이퍼링크에 표시될 텍스트

    이 함수는 "수업요약" 시트의 A열 다음 빈 행에 하이퍼링크를 추가합니다.
    하이퍼링크는 같은 문서 내의 다른 시트로 연결됩니다.
    """

    
    sheet = doc.worksheet("수업요약")
    next_row = len(sheet.col_values(2)) + 1
    content = f'=HYPERLINK("#gid={id}", "{nick_name}")'
    sheet.update("A" + str(next_row), [[False]])
    sheet.update_acell("B" + str(next_row), content)

def delete_message():
    """
    대화 기록 중 마지막 대화를 삭제하는 함수입니다.

    이 함수는 다음과 같은 작업을 수행합니다:
    1. 세션 상태에서 현재 활성화된 워크시트를 가져옵니다.
    2. 워크시트의 첫 번째 열에서 데이터가 있는 마지막 행의 번호를 찾습니다.
    3. 해당 행을 삭제합니다(마지막 대화 삭제).
    """
    target = st.session_state["sheet"]
    target_row = len(target.col_values(1))
    target.delete_rows(target_row)

def get_summary_sheet(doc):
    """
    Returns:
        '수업요약' 시트를 리턴
    """
    return doc.worksheet("수업요약")

def get_conversation_sessions(sheet):
    """
    워크시트에서 대화 기록을 읽어와 시간별로 세션을 그룹핑하는 함수입니다.

    Parameters:
        sheet (gspread.Worksheet): 대화 기록이 저장된 워크시트

    Returns:
        list: 세션 정보를 담은 딕셔너리 리스트
            각 세션은 다음 키를 포함:
            - session_id: 세션 고유 ID (시작 행 번호)
            - start_time: 세션 시작 시간
            - end_time: 세션 종료 시간
            - message_count: 메시지 개수
            - first_message: 첫 번째 사용자 메시지 (미리보기용)

    Note:
        - 30분 이상 간격이 있으면 새로운 세션으로 간주
        - 시스템 메시지는 제외
    """
    from datetime import datetime, timedelta

    # 모든 데이터 가져오기 (A, B, C 컬럼: 시간, 역할, 내용)
    all_data = sheet.get_all_values()

    if len(all_data) <= 1:  # 헤더만 있거나 비어있음
        return []

    sessions = []
    current_session = None
    last_time = None
    SESSION_GAP_MINUTES = 30  # 30분 간격으로 세션 구분

    for idx, row in enumerate(all_data[1:], start=2):  # 헤더 제외, 행 번호는 2부터
        if len(row) < 3:
            continue

        time_str, role, content = row[0], row[1], row[2]

        if not time_str or not content:
            continue

        try:
            # 시간 파싱 (HH:MM 형식)
            current_time = datetime.strptime(time_str, "%H:%M")

            # 새 세션 시작 조건: 첫 메시지이거나 30분 이상 간격
            if current_session is None:
                current_session = {
                    "session_id": idx,
                    "start_time": time_str,
                    "end_time": time_str,
                    "message_count": 1,
                    "first_message": content[:50] + "..." if len(content) > 50 else content,
                    "row_start": idx,
                    "row_end": idx
                }
                last_time = current_time
            else:
                # 시간 차이 계산
                time_diff = abs((current_time - last_time).total_seconds() / 60)

                if time_diff > SESSION_GAP_MINUTES:
                    # 이전 세션 저장
                    sessions.append(current_session)
                    # 새 세션 시작
                    current_session = {
                        "session_id": idx,
                        "start_time": time_str,
                        "end_time": time_str,
                        "message_count": 1,
                        "first_message": content[:50] + "..." if len(content) > 50 else content,
                        "row_start": idx,
                        "row_end": idx
                    }
                else:
                    # 현재 세션에 추가
                    current_session["end_time"] = time_str
                    current_session["message_count"] += 1
                    current_session["row_end"] = idx

                last_time = current_time

        except ValueError:
            # 시간 파싱 실패 시 건너뛰기
            continue

    # 마지막 세션 저장
    if current_session is not None:
        sessions.append(current_session)

    return sessions

def get_session_messages(sheet, row_start, row_end):
    """
    특정 세션의 모든 메시지를 가져오는 함수입니다.

    Parameters:
        sheet (gspread.Worksheet): 워크시트
        row_start (int): 세션 시작 행
        row_end (int): 세션 종료 행

    Returns:
        list: 메시지 리스트 [{"role": "user", "content": "..."}, ...]
    """
    messages = []

    # 해당 범위의 데이터 가져오기
    if row_start == row_end:
        range_str = f"A{row_start}:C{row_start}"
    else:
        range_str = f"A{row_start}:C{row_end}"

    data = sheet.get(range_str)

    for row in data:
        if len(row) >= 3:
            role = "user" if row[1] == "USER" else "assistant"
            messages.append({"role": role, "content": row[2]})

    return messages

def generate_session_title(messages, client, model):
    """
    대화 내용을 분석하여 적절한 제목을 생성하는 함수입니다.

    Parameters:
        messages (list): 메시지 리스트
        client: Anthropic API 클라이언트
        model (str): 사용할 AI 모델

    Returns:
        str: 생성된 제목
    """
    # 대화 내용 요약을 위한 프롬프트
    conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages[:10]])  # 처음 10개만

    prompt = f"""다음 대화 내용을 분석하여 간단하고 명확한 제목을 한국어로 생성해주세요.
제목은 20자 이내로 작성하고, 대화의 핵심 주제를 나타내야 합니다.
제목만 출력하고 다른 설명은 하지 마세요.

대화 내용:
{conversation_text}"""

    try:
        response = client.messages.create(
            model=model,
            max_tokens=100,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        title = response.content[0].text.strip()
        # 따옴표 제거
        title = title.strip('"').strip("'")
        return title
    except Exception as e:
        return f"대화 세션 (오류: {str(e)[:20]})"

def save_session_title(sheet, row_num, title):
    """
    생성된 제목을 Google Sheets의 D열에 저장하는 함수입니다.

    Parameters:
        sheet (gspread.Worksheet): 워크시트
        row_num (int): 저장할 행 번호
        title (str): 저장할 제목
    """
    sheet.update_cell(row_num, 4, title)  # D열 (4번째 컬럼)