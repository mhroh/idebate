"""
Mermaid 차트 생성 및 렌더링 유틸리티
교육용 토론 챗봇을 위한 시각화 도구
"""
import streamlit as st
from streamlit_mermaid import st_mermaid


def render_simple_chart():
    """
    간단한 테스트 차트 렌더링
    Phase 1 테스트용
    """
    mermaid_code = """
    graph TD
        A[🎯 토론 시작] --> B[💭 찬성 의견]
        A --> C[💭 반대 의견]
        B --> D[✅ 결론]
        C --> D
        
        style A fill:#f9f,stroke:#333,stroke-width:4px
        style B fill:#bbf,stroke:#333,stroke-width:2px
        style C fill:#fbb,stroke:#333,stroke-width:2px
        style D fill:#bfb,stroke:#333,stroke-width:3px
    """
    
    st_mermaid(mermaid_code)


def create_debate_chart(topic, pros, cons):
    """
    토론 주제에 대한 찬반 차트 생성
    
    Parameters:
    topic (str): 토론 주제
    pros (list): 찬성 논거 리스트
    cons (list): 반대 논거 리스트
    
    Returns:
    str: Mermaid 차트 코드
    """
    mermaid_code = f"""
    graph TD
        A[{topic}]
        A --> B[👍 찬성]
        A --> C[👎 반대]
    """
    
    # 찬성 논거 추가
    for i, pro in enumerate(pros):
        if pro.strip():  # 빈 문자열 체크
            node_id = f"P{i}"
            # 특수문자 처리
            clean_pro = pro.strip().replace('"', "'").replace('[', '(').replace(']', ')')
            mermaid_code += f"\n        B --> {node_id}[{clean_pro}]"
            mermaid_code += f"\n        style {node_id} fill:#bbf,stroke:#333,stroke-width:2px"
    
    # 반대 논거 추가
    for i, con in enumerate(cons):
        if con.strip():  # 빈 문자열 체크
            node_id = f"C{i}"
            # 특수문자 처리
            clean_con = con.strip().replace('"', "'").replace('[', '(').replace(']', ')')
            mermaid_code += f"\n        C --> {node_id}[{clean_con}]"
            mermaid_code += f"\n        style {node_id} fill:#fbb,stroke:#333,stroke-width:2px"
    
    # 메인 노드 스타일
    mermaid_code += """
        
        style A fill:#f9f,stroke:#333,stroke-width:4px
        style B fill:#bfb,stroke:#333,stroke-width:3px
        style C fill:#fbb,stroke:#333,stroke-width:3px
    """
    
    return mermaid_code


def render_debate_chart(topic, pros, cons):
    """
    토론 차트를 화면에 렌더링
    
    Parameters:
    topic (str): 토론 주제
    pros (list): 찬성 논거 리스트
    cons (list): 반대 논거 리스트
    """
    mermaid_code = create_debate_chart(topic, pros, cons)
    st_mermaid(mermaid_code)


def create_argument_structure(claim, evidence_list, counterargument=None):
    """
    주장-근거-반론 구조 차트 생성
    
    Parameters:
    claim (str): 주장
    evidence_list (list): 근거 리스트
    counterargument (str): 반론 (선택)
    
    Returns:
    str: Mermaid 차트 코드
    """
    clean_claim = claim.replace('"', "'").replace('[', '(').replace(']', ')')
    
    mermaid_code = f"""
    graph TD
        A[주장: {clean_claim}]
    """
    
    # 근거 추가
    for i, evidence in enumerate(evidence_list):
        if evidence.strip():
            node_id = f"E{i}"
            clean_evidence = evidence.strip().replace('"', "'").replace('[', '(').replace(']', ')')
            mermaid_code += f"\n        A --> {node_id}[근거 {i+1}: {clean_evidence}]"
            mermaid_code += f"\n        style {node_id} fill:#e1f5e1,stroke:#333,stroke-width:2px"
    
    # 반론 추가 (있으면)
    if counterargument and counterargument.strip():
        clean_counter = counterargument.replace('"', "'").replace('[', '(').replace(']', ')')
        mermaid_code += f"\n        A -.->|반론| R[{clean_counter}]"
        mermaid_code += "\n        style R fill:#ffe1e1,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5"
    
    mermaid_code += "\n        style A fill:#fff4e1,stroke:#333,stroke-width:4px"
    
    return mermaid_code


# 차트 타입별 템플릿
CHART_TEMPLATES = {
    "debate": """
graph TD
    A[{topic}]
    A -->|찬성| B[{pro1}]
    A -->|찬성| C[{pro2}]
    A -->|반대| D[{con1}]
    A -->|반대| E[{con2}]
    
    style A fill:#f9f,stroke:#333,stroke-width:4px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
    style E fill:#fbb,stroke:#333,stroke-width:2px
""",
    
    "logic_flow": """
graph LR
    A[전제1] --> C[결론]
    B[전제2] --> C
    C --> D[함의]
    
    style A fill:#e1f5e1
    style B fill:#e1f5e1
    style C fill:#fff4e1
    style D fill:#e1f0ff
""",
    
    "argument_tree": """
graph TD
    A[중심 주장]
    A --> B[주장1]
    A --> C[주장2]
    B --> D[근거1-1]
    B --> E[근거1-2]
    C --> F[근거2-1]
    
    style A fill:#f9f,stroke:#333,stroke-width:4px
"""
}
