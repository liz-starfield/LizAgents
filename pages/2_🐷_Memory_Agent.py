from modules import utils
import streamlit as st
from modules.streaming import StreamHandler
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from modules.sidebar import Sidebar
from langchain_core.messages.base import BaseMessage

st.set_page_config(page_title="Memory Agent", page_icon="🐷", initial_sidebar_state="expanded")
st.header('🐷Memory Agent')
st.write('I am an intelligent agent with memory, let me help you handle complex tasks, or come to chat with me.')

msgs = StreamlitChatMessageHistory()

class MemoryAgent:

    def __init__(self):
        utils.configure_openai_api_key()

    def setup_chain(_self):
        memory = ConversationBufferMemory(chat_memory=msgs, return_messages=True)
        llm = ChatOpenAI(model_name=st.session_state["model"], temperature=st.session_state["temperature"], streaming=True)
        chain = ConversationChain(llm=llm, memory=memory, verbose=True)
        return chain
    
    @utils.enable_chat_history
    def main(self):

        view_messages = st.expander("View the history contents")

        # to show chat history on ui
        if len(msgs.messages) == 0:
            msgs.clear()
            msgs.add_ai_message("How can I help you?")
            print(msgs)


        avatars = {"human": "user", "ai": "assistant"}
        for msg in msgs.messages:
            if isinstance(msg, BaseMessage):
                st.chat_message(avatars[msg.type]).write(msg.content)
            else:
                print(type(msgs.messages))
                print(msgs.messages)
                print(type(msg))
                print(msg)



        if user_query := st.chat_input(placeholder="Ask me anything!"):

            st.chat_message("user").write(user_query)

            with st.chat_message("assistant"):
                chain = self.setup_chain()
                stream_handler = StreamHandler(st.empty())
                chain.run(user_query, callbacks=[stream_handler])
        with view_messages:
            view_messages.json(msgs.messages)

        sidebar = Sidebar(msgs)
        sidebar.show_options()

if __name__ == "__main__":
    obj = MemoryAgent()
    obj.main()
