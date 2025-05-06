import streamlit as st
from PIL import Image
from pandasai.llm.openai import OpenAI
from streamlit_extras.switch_page_button import switch_page
import PIL
from pandasai.llm import BambooLLM
#from langchain_community.llms import Ollama
from pandasai import Agent
import pandas as pd
from pandasai.responses.streamlit_response import StreamlitResponse

im = Image.open("kn.jpg")
st.set_page_config(
    page_icon=im,
    page_title="Datability CoPilot"
)
    
def main():    
    #Side Menu Bar
    file_upload = st.file_uploader("Upload your Data",accept_multiple_files=False,type = ['csv','xls','xlsx'])

    st.markdown(":green[*Please ensure the first row has the column names.*]")


    if file_upload is not None:
        data  = extract_dataframes(file_upload)
        df = st.selectbox("Here's your uploaded data!",
                          tuple(data.keys()),index=0
                          )
        #st.dataframe(data[df])

        
        #llm = Ollama(model="llama3")
        #llm = BambooLLM(api_key="$2a$10$gYSHbf1rUYSiH2bWvkKgKeELF1vSG0bqB.vRDWhXAHFSvtKcL6aZ2")
        llm = OpenAI(api_token='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') 
        if llm:
            #Instattiating PandasAI agent
            analyst = get_agent(data,llm)

            #starting the chat with the PandasAI agent
            chat_window(analyst)
            
        

    else:
        st.warning("Please upload your data first! You can upload a CSV or an Excel file.")

#
   

#Functuion for chat window
def chat_window(analyst):
    with st.chat_message("assistant"):
        st.text("Explore your data with Datability Copilot?🧐")

    #Initilizing message history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    #Displaying the message history on re-reun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            #priting the questions
            if 'question' in message:
                st.markdown(message["question"])
            #printing the code generated and the evaluated code
            elif 'response' in message:
                #getting the response
                st.write(message['response'])
                
            #retrieving error messages
            elif 'error' in message:
                st.text(message['error'])
    #Getting the questions from the users
    user_question = st.chat_input("What are you curious about? ")

    
    if user_question:
        #Displaying the user question in the chat message
        with st.chat_message("user"):
            st.markdown(user_question)
        #Adding user question to chat history
        st.session_state.messages.append({"role":"user","question":user_question})
       
        try:
            with st.spinner("Analyzing..."):
                response = analyst.chat(user_question)
                st.write(response)
                st.session_state.messages.append({"role":"assistant","response":response})
        
        except Exception as e:
            st.write(e)
            error_message = "⚠️Sorry, Couldn't generate the answer! Please try rephrasing your question!"

    #Function to clear history
    def clear_chat_history():
        st.session_state.messages = []
    #Button for clearing history
    st.sidebar.text("Click to Clear Chat history")
    st.sidebar.button("CLEAR 🗑️",on_click=clear_chat_history)

        
def get_agent(data,llm):
    """
    The function creates an agent on the dataframes exctracted from the uploaded files
    Args: 
        data: A Dictionary with the dataframes extracted from the uploaded data
        llm:  llm object based on the ll type selected
    Output: PandasAI Agent
    """
    agent = Agent(list(data.values()),config = {"llm":llm,"verbose": True, "response_parser": StreamlitResponse})

    return agent


def extract_dataframes(raw_file):
    """
    This function extracts dataframes from the uploaded file/files
    Args: 
        raw_file: Upload_File object
    Processing: Based on the type of file read_csv or read_excel to extract the dataframes
    Output: 
        dfs:  a dictionary with the dataframes
    
    """
    dfs = {}
    if raw_file.name.split('.')[1] == 'csv':
        csv_name = raw_file.name.split('.')[0]
        df = pd.read_csv(raw_file)
        dfs[csv_name] = df

    elif (raw_file.name.split('.')[1] == 'xlsx') or (raw_file.name.split('.')[1] == 'xls') :
        # Read the Excel file
        xls = pd.ExcelFile(raw_file)

        # Iterate through each sheet in the Excel file and store them into dataframes
        dfs = {}
        for sheet_name in xls.sheet_names:
            dfs[sheet_name] = pd.read_excel(raw_file, sheet_name=sheet_name)

    #return the dataframes
    return dfs

if __name__ == "__main__":
    main()


