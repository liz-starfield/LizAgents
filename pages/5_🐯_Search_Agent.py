from modules import utils
import streamlit as st

from langchain.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.callbacks import StreamlitCallbackHandler

st.set_page_config(page_title="Search Agent", page_icon="🐯", initial_sidebar_state="expanded")
st.header('🐯Search Agent')
st.write('I can search the internet for the latest information. What would you like to know? Let me help you.')

class SearchAgent:

    def __init__(self):
        utils.configure_openai_api_key()
        self.openai_model = "gpt-3.5-turbo"

    def setup_agent(self):
        # Define tool
        tools = [DuckDuckGoSearchRun(name="Search")]

        # Setup LLM and Agent
        llm = ChatOpenAI(model_name=self.openai_model, streaming=True)
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True,
            verbose=True
        )
        return agent

    @utils.enable_chat_history
    def main(self):
        # to show chat history on ui
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])
        agent = self.setup_agent()
        user_query = st.chat_input(placeholder="Ask me anything!")
        if user_query:
            st.chat_message("user").write(user_query)
            st.session_state.messages.append({"role": "user", "content": user_query})
            with st.chat_message("assistant"):
                stream_handler = StreamlitCallbackHandler(st.container())
                response = agent.run(user_query, callbacks=[stream_handler])
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.write(response)

if __name__ == "__main__":
    obj = SearchAgent()
    obj.main()