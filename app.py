import streamlit as st
from main import agent, vectorstore

st.set_page_config(page_title="Conversational DB Agent", page_icon="🧠")
st.title("🧠 Conversational DB Agent")
st.markdown("Chat with your MongoDB database using natural language queries.")

# Initialize session state if not already present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages using st.chat_message
for msg in st.session_state.messages:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Ask a question about accounts, transactions, or customers")

if user_input:
    # Save and display user's message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Run similarity search for intent match
    try:
        similar_docs = vectorstore.similarity_search(user_input, k=1)
        if similar_docs:
            intent = similar_docs[0].page_content
            st.toast(f"🔍 Closest matched intent: {intent}")
        else:
            st.toast("🔍 No close match found. Attempting interpretation anyway...")
    except Exception as e:
        st.toast(f"⚠️ Could not determine closest intent: {e}")

    # Get response from agent
    try:
        response = agent.run(user_input)
    except Exception as e:
        response = (
            "❌ Agent error: " + str(e) +
            "\n🤖 Agent: Sorry, I couldn’t understand your query. Try rephrasing."
        )

    # Save and display assistant's message
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
