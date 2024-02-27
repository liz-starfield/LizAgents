import os
import streamlit as st
from modules import utils
from modules.browser import mark_page, unmark_page, open_browser, close_browser, send, toActionForResult, observe
from streamlit import _bottom

st.set_page_config(page_title="Vision Agent", page_icon="🦄", initial_sidebar_state="expanded")
st.header('🦄Vision Agent')
st.write('Give me a task, I will simulate the behavior of a human operating a browser to help you process and complete tasks step by step.')

class VisionAgent:

    def __init__(self):
        utils.configure_openai_api_key()

    @utils.enable_chat_history
    def main(self):
        # to show chat history on ui
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])

        user_query = st.chat_input(placeholder="Ask me anything!")

        genre = _bottom.radio(
            "Choose the mode",
            [":rainbow[Automatic]", "Manual"])

        if genre == ':rainbow[Automatic]':
            _bottom.write('It is currently in fully automatic mode.')
            if user_query:
                st.session_state.task = user_query
                st.chat_message("user").write(user_query)
                st.session_state.messages.append({"role": "user", "content": user_query})
                send()
        else:
            _bottom.write("It is currently in manual control mode.")
            col1, col2, col3, col4, col5, col6, col7 = _bottom.columns(7)

            with col1:
                if st.button("Open Browser"):
                    open_browser()
            with col2:
                if st.button("Close Browser"):
                    close_browser()
            with col3:
                mark_button = st.button("Mark Element")
            with col4:
                unmark_button = st.button("Unmark Element")
            with col5:
                observe_button = st.button("Observe")
            with col6:
                execute_button = st.button("Execute Action")
            with col7:
                observe_execute_button = st.button("Observe and Execute Action")

            if user_query:
                if "history_actions" in st.session_state:
                    st.session_state["history_actions"].clear()
                st.session_state.task = user_query
                st.chat_message("user").write(user_query)
                st.session_state.messages.append({"role": "user", "content": user_query})
                if "driver" in st.session_state:
                    st.session_state.driver.get("https://www.google.com/")
                else:
                    open_browser()

            if mark_button:
                mark_page()
                if not os.path.exists('tmp'):
                    os.makedirs('tmp')
                file_path = 'tmp/screenshot_mark.png'
                driver = st.session_state['driver']
                driver.get_screenshot_as_file(file_path)
                st.chat_message("assistant").image(file_path)

            if unmark_button:
                unmark_page()
                if not os.path.exists('tmp'):
                    os.makedirs('tmp')
                file_path = 'tmp/screenshot_unmark.png'
                driver = st.session_state['driver']
                driver.get_screenshot_as_file(file_path)
                st.chat_message("assistant").image(file_path)

            if observe_button:
                observe()

            if execute_button:
                toActionForResult()
                unmark_page()
                if not os.path.exists('tmp'):
                    os.makedirs('tmp')
                file_path = 'tmp/screenshot_unmark.png'
                driver = st.session_state['driver']
                driver.get_screenshot_as_file(file_path)
                st.chat_message("assistant").image(file_path)

            if observe_execute_button:
                if "task" in st.session_state:
                    observe()
                    toActionForResult()
                    unmark_page()
                    if not os.path.exists('tmp'):
                        os.makedirs('tmp')
                    file_path = 'tmp/screenshot_unmark.png'
                    driver = st.session_state['driver']
                    driver.get_screenshot_as_file(file_path)
                    st.chat_message("assistant").image(file_path)
                else:
                    st.chat_message("assistant").write("Please start a task")
                    st.session_state.messages.append({"role": "assistant", "content": "Please start a task"})

if __name__ == "__main__":
    obj = VisionAgent()
    obj.main()