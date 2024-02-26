import streamlit as st
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage
from datetime import datetime
class Sidebar:

    MODEL_OPTIONS = ["gpt-3.5-turbo", "gpt-4"]
    TEMPERATURE_MIN_VALUE = 0.0
    TEMPERATURE_MAX_VALUE = 1.0
    TEMPERATURE_DEFAULT_VALUE = 0.0
    TEMPERATURE_STEP = 0.01

    def __init__(self, msgs):
        self.msgs = msgs

    def reset_chat_button(self):
        if st.button("Reset Chat"):
            self.msgs.clear()
            self.msgs.add_ai_message("How can I help you?")
            st.rerun()



    def get_history_contents(self):
        lines = [
            "# History Contents\n"
        ]

        for msg in self.msgs.messages:
            lines.append("\n")
            if isinstance(msg, HumanMessage) :
                lines.append("## Human:\n")
                lines.append(msg.content)
            elif isinstance(msg, AIMessage):
                lines.append("## AI:\n")
                lines.append(msg.content)
        return "".join(lines)

    def model_selector(self):
        model = st.selectbox(label="Model", options=self.MODEL_OPTIONS)
        st.session_state["model"] = model

    def temperature_slider(self):
        temperature = st.slider(
            label="Temperature",
            min_value=self.TEMPERATURE_MIN_VALUE,
            max_value=self.TEMPERATURE_MAX_VALUE,
            value=self.TEMPERATURE_DEFAULT_VALUE,
            step=self.TEMPERATURE_STEP,
        )
        st.session_state["temperature"] = temperature
        
    def show_options(self):
        with st.sidebar.expander("🛠️ Tools", expanded=False):

            self.reset_chat_button()
            st.download_button(
                label="Download Chat",
                data=self.get_history_contents(),
                file_name=f"{datetime.now():%Y-%m-%d %H.%M}_history_chat.md",
                mime="text/markdown",
            )
            self.model_selector()
            self.temperature_slider()
            st.session_state.setdefault("model", self.MODEL_OPTIONS[0])
            st.session_state.setdefault("temperature", self.TEMPERATURE_DEFAULT_VALUE)

    