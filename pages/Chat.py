import streamlit as st
from PIL import Image
import openai
import os
from openai import OpenAI
# Set up page configuration
im = Image.open("kn.jpg")
st.set_page_config(page_icon=im, page_title="Datability CoPilot")

# Set your OpenAI API key
openai.api_key = os.getenv('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')  # Ensure this is set in your environment variables
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="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",
)
def main():
    # Display image and title in the header
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("kn.jpg", width=60)
    with col2:
        st.title("Datability CoPilot")

    chat_window()

def chat_window():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.conversation_context = ""

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    user_input = st.chat_input("How can I assist you?")
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.conversation_context += f"User: {user_input}\n"

        try:
            with st.spinner("Thinking..."):
                # Call OpenAI API directly for response
                response = client.chat.completions.create(
                    model="gpt-4o",  # Replace with 'gpt-3.5-turbo' if needed
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        *[
                            {"role": msg["role"], "content": msg["content"]}
                            for msg in st.session_state.messages
                        ],
                        {"role": "user", "content": user_input}
                    ]
                )

                response_text = response.choices[0].message.content

                # Append and display assistant response
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                st.session_state.conversation_context += f"Assistant: {response_text}\n"
                with st.chat_message("assistant"):
                    st.markdown(response_text)

        except Exception as e:
            st.error(f"An error occurred: {e}")

    # Sidebar button to clear chat history
    if st.sidebar.button("Clear Chat History 🗑️"):
        st.session_state.messages = []
        st.session_state.conversation_context = ""

if __name__ == "__main__":
    main()
