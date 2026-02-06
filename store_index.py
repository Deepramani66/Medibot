from src.helper import load_pdf, text_split, get_huggingface_embeddings
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os

load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
PINECONE_API_ENV = os.environ.get('PINECONE_API_ENV')
HUGGINGFACEHUB_API_TOKEN = os.environ.get('HUGGINGFACEHUB_API_TOKEN')

extracted_data = load_pdf('data/')

text_chunks = text_split(extracted_data)
print(len(text_chunks))

embeddings = get_huggingface_embeddings()

texts = [doc.page_content for doc in text_chunks]

pc = Pinecone(
        api_key= PINECONE_API_KEY
    )

index_name = "medicalbot"
dense_index = pc.Index(index_name)
vectorstore = PineconeVectorStore.from_texts(
    texts=texts,
    embedding=embeddings,
    index_name=index_name
)

docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

query = 'What are allergies'

docs = docsearch.similarity_search(query, k=2)
print(docs)