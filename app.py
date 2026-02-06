from flask import Flask, render_template, jsonify, request
from src.helper import get_huggingface_embeddings
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
from src.prompt import *
import os

app = Flask(__name__)

load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
PINECONE_API_ENV = os.environ.get('PINECONE_API_ENV')
HUGGINGFACEHUB_API_TOKEN = os.environ.get('HUGGINGFACEHUB_API_TOKEN')

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def init_rag():
    embeddings = get_huggingface_embeddings()

    pc = Pinecone(api_key=PINECONE_API_KEY)
    docsearch = PineconeVectorStore.from_existing_index(
        index_name="medicalbot",
        embedding=embeddings
    )

    retriever = docsearch.as_retriever(search_kwargs={"k": 4})

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

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]   
    print("User:", msg)

    response = chain.invoke(msg)   
    print("Bot:", response.content)
        
        # Wrap response in expected JSON structure
    return jsonify({
            "thinking": "Analyzing medical knowledge base...",
            "response": str(response.content),
            "context_count": 4
        })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
