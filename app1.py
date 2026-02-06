import streamlit as st
import os
import re
from dotenv import load_dotenv

from src.helper import get_huggingface_embeddings
from src.prompt import prompt

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.runnables import RunnablePassthrough


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Medical RAG Chatbot",
    page_icon="🩺",
    layout="centered"
)

st.title("🩺 Medical RAG Chatbot")
st.caption("Pinecone · HuggingFace · LangChain")

# --------------------------------------------------
# ENV
# --------------------------------------------------
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")


# --------------------------------------------------
# UTILITIES
# --------------------------------------------------
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def split_thinking(text: str):
    """
    Extract <think>...</think> block and final answer
    """
    match = re.search(r"<think>(.*?)</think>", text, re.DOTALL)

    thinking = ""
    if match:
        thinking = match.group(1).strip()
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    return thinking, text.strip()


# --------------------------------------------------
# RAG INITIALIZATION (CACHED)
# --------------------------------------------------
@st.cache_resource
def init_rag():
    embeddings = get_huggingface_embeddings()

    pc = Pinecone(api_key=PINECONE_API_KEY)

    vectorstore = PineconeVectorStore.from_existing_index(
        index_name="medicalbot",
        embedding=embeddings
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    llm = HuggingFaceEndpoint(
        repo_id="deepseek-ai/DeepSeek-R1-0528",
        task="text-generation",
        max_new_tokens=512,
        do_sample=False,
        repetition_penalty=1.03,
        provider="auto",
        huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN
    )

    chat_model = ChatHuggingFace(llm=llm)

    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | chat_model
    )

    return chain


chain = init_rag()


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# --------------------------------------------------
# USER INPUT
# --------------------------------------------------
user_input = st.chat_input("Ask a medical question...")

if user_input:
    # Store user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing medical knowledge base..."):
            response = chain.invoke(user_input)
            raw_output = response.content

        thinking, final_answer = split_thinking(raw_output)

        # Final answer (visible)
        st.markdown(final_answer)

        # Hidden reasoning (DeepSeek-style)
        if thinking:
            with st.expander("🤔 Show reasoning"):
                st.markdown(thinking)

    # Save assistant response (final only)
    st.session_state.messages.append({
        "role": "assistant",
        "content": final_answer
    })
