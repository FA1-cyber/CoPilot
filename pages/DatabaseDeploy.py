import streamlit as st
from PIL import Image
from pandasai.llm.openai import OpenAI
from pandasai import Agent
import pandas as pd
from pandasai.responses.streamlit_response import StreamlitResponse
from pathlib import Path
import matplotlib as plt
from sqlalchemy import create_engine  # 🔄 Replaces pyodbc

# Set up page configuration
im = Image.open("kn.jpg")
st.set_page_config(page_icon=im, page_title="Datability CoPilot")

# Define column access for each user role
user_column_access = {
    "admin_user": ["SID", "RowKey", "CLIENT_SID", "PM_CLIENT_ID", "FULL_NAME_AR", "FULL_NAME_EN", "GENDER_CD", "GENDER_EN", "CREDIT_CARD_SEGMENT", "DATE_OF_BIRTH", "CREATION_DATE", "Suspended_flag", "TRANSACTION_COUNT"],
    "analyst_user": ["RowKey", "GENDER_CD", "GENDER_EN", "CREDIT_CARD_SEGMENT", "DATE_OF_BIRTH", "CREATION_DATE", "Suspended_flag"],
    "viewer_user": ["FULL_NAME_EN", "GENDER_EN", "DATE_OF_BIRTH"]
}

# Define available users
users = list(user_column_access.keys())

def main():
    # Display image and title in the header
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("kn.jpg", width=60)
    with col2:
        st.title("Datability CoPilot")

    global selected_user 
    selected_user = st.selectbox("Select a user:", users)

    # SQLAlchemy connection string using pytds
    conn_url = "mssql+pytds://dclean-user:dclean-user@sql19-srv:1433/Dclean_DWH"
    engine = create_engine(conn_url)

    tables_data = {}
    try:
        table_names = ["Dclean_DWH.old_dbo.CO_PILOT"]
        for table_name in table_names:
            query = f'SELECT * FROM {table_name};'
            try:
                df = pd.read_sql(query, engine)
                if not df.empty:
                    tables_data[table_name] = df
            except Exception as e:
                st.warning(f"Could not retrieve data from table {table_name}: {e}")
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return

    if tables_data:
        llm = OpenAI(api_token='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',
                     model='gpt-4o')
        analyst = get_agent(list(tables_data.values()), llm)
        chat_window(analyst)
    else:
        st.warning("No data was retrieved. Please check the table names or connection details.")

def chat_window(analyst):
    with st.chat_message("assistant"):
        st.text("Explore your data with Datability Copilot?🧐")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.conversation_context = ""

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if 'question' in message:
                st.markdown(message["question"])
            elif 'response' in message:
                st.write(message['response'])
            elif 'error' in message:
                st.text(message['error'])

    user_question = st.chat_input("What are you curious about? ")

    if user_question:
        with st.chat_message("user"):
            st.markdown(user_question)

        st.session_state.messages.append({"role": "user", "question": user_question})
        st.session_state.conversation_context += f"User: {user_question}\n"

        try:
            with st.spinner("Analyzing..."):
                temp = str(analyst.generate_code(st.session_state.conversation_context))

                allowed_columns = user_column_access[selected_user]
                if missing_any(temp, allowed_columns):
                    with st.chat_message("assistant"):
                        st.text("⚠️ Unauthorized access to restricted data ⚠️")
                        st.session_state.messages.append({"role": "assistant", "response": "⚠️ Unauthorized access to restricted data ⚠️"})
                else:
                    response = analyst.chat(st.session_state.conversation_context)
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "response": response})
                    st.session_state.conversation_context += f"Assistant: {response}\n"
        except Exception as e:
            st.write(e)
            error_message = "⚠️Sorry, Couldn't generate the answer! Please try rephrasing your question!"
            st.session_state.messages.append({"role": "assistant", "error": error_message})

    def clear_chat_history():
        st.session_state.messages = []
        st.session_state.conversation_context = ""

    st.sidebar.text("Click to Clear Chat history")
    st.sidebar.button("CLEAR 🗑️", on_click=clear_chat_history)

def get_agent(dataframes, llm):
    return Agent(dataframes, config={"llm": llm, "verbose": True, "response_parser": StreamlitResponse})

def missing_any(text, keywords):
    return any(keyword not in text for keyword in keywords)

if __name__ == "__main__":
    main()
