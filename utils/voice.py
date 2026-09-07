from pathlib import Path

import streamlit as st
from streamlit.components.v1 import declare_component

_component = declare_component('idebate_voice', path=str(Path(__file__).parent / 'voice_frontend'))


def voice_input(enabled):
    event = _component(
        enabled=enabled,
        busy=st.session_state.get('processing', False),
        reply=st.session_state.get('voice_reply'),
        key='voice_control',
        default=None,
    )
    if not isinstance(event, dict):
        return None
    event_id, text = event.get('id'), event.get('text')
    if not isinstance(event_id, str) or not isinstance(text, str):
        return None
    if event_id == st.session_state.get('voice_seen'):
        return None
    st.session_state.voice_seen = event_id
    if enabled and text.strip() and len(text) <= 10000:
        return event_id, text.strip()
    return None
