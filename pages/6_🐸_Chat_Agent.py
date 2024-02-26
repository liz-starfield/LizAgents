from modules import utils
import streamlit as st
from modules.streaming import StreamHandler
from langchain_openai import ChatOpenAI

st.set_page_config(page_title="Chat Agent", page_icon="🐸", initial_sidebar_state="expanded")
st.header('🐸Chat Agent')
st.write('I am a basic intelligent agent; ask me a question, and I will give you the answer.')

class ChatAgent:

    def __init__(self):
        utils.configure_openai_api_key()
        self.openai_model = "gpt-3.5-turbo"
    
    @utils.enable_chat_history
    def main(self):
        # to show chat history on ui
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])

        if user_query := st.chat_input(placeholder="Ask me anything!"):
            st.chat_message("user").write(user_query)
            st.session_state.messages.append({"role": "user", "content": user_query})
            with st.chat_message("assistant"):
                stream_handler = StreamHandler(st.empty())
                llm = ChatOpenAI(streaming=True, model_name=self.openai_model, temperature=0, verbose=True, callbacks=[stream_handler])
                response = llm.invoke(user_query)
                st.session_state.messages.append({"role": "assistant", "content": response.content})

if __name__ == "__main__":
    obj = ChatAgent()
    obj.main()