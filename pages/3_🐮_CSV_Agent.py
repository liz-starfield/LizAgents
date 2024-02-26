import os
from modules import utils
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
import pandas as pd
from langchain.agents import AgentType
from langchain.callbacks import StreamlitCallbackHandler

st.set_page_config(page_title="CSV Agent", page_icon="🐮", initial_sidebar_state="expanded")
st.header('🐮CSV Agent')
st.write('Provide me with a CSV file and ask me about it, and I will tell you everything about the CSV file.')

file_formats = {
    "csv": pd.read_csv,
    "xls": pd.read_excel,
    "xlsx": pd.read_excel,
    "xlsm": pd.read_excel,
    "xlsb": pd.read_excel,
}

@st.cache_data(ttl="2h")
def load_data(uploaded_file):
    try:
        ext = os.path.splitext(uploaded_file.name)[1][1:].lower()
    except:
        ext = uploaded_file.split(".")[-1]
    if ext in file_formats:
        return file_formats[ext](uploaded_file)
    else:
        st.error(f"Unsupported file format: {ext}")
        return None

class CsvAgent:

    def __init__(self):
        utils.configure_openai_api_key()
        self.openai_model = "gpt-3.5-turbo"

    def save_file(self, file):
        folder = 'tmp'
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        file_path = f'./{folder}/{file.name}'
        with open(file_path, 'wb') as f:
            f.write(file.getvalue())
        return file_path

    def setup_qa_chain(self, df):

        # Setup LLM and QA chain
        llm = ChatOpenAI(model_name=self.openai_model, temperature=0, streaming=True)
        pandas_df_agent = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            handle_parsing_errors=True,
        )
        return pandas_df_agent

    @utils.enable_chat_history
    def main(self):
        # to show chat history on ui
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])

        # User Inputs
        uploaded_files = st.sidebar.file_uploader(label='Upload CSV files', type=list(file_formats.keys()))
        if not uploaded_files:
            st.error("Please upload CSV documents to continue!")
            st.stop()

        if uploaded_files:
            df = load_data(uploaded_files)

        user_query = st.chat_input(placeholder="Ask me anything!")

        if uploaded_files and user_query:
            st.chat_message("user").write(user_query)
            st.session_state.messages.append({"role": "user", "content": user_query})
            qa_chain = self.setup_qa_chain(df)

            with st.chat_message("assistant"):
                st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)
                response = qa_chain.run(user_query, callbacks=[st_cb])

                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    obj = CsvAgent()
    obj.main()