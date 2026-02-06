# Extracting Data From Pdfs and splitting into chunks
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
def load_pdf(data):
    loader = DirectoryLoader(
        data,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )

    documents = loader.load()
    return documents

# text split
from langchain_text_splitters import RecursiveCharacterTextSplitter

def text_split(extracted_data):
  text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", " ", ""]
)
  text_chunks = text_splitter.split_documents(extracted_data)
  return text_chunks

#Downloading Embedding model from huggingface
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

def get_huggingface_embeddings():

    embeddings = HuggingFaceEmbeddings(
        model_name = 'sentence-transformers/all-mpnet-base-v2'
    )

    return embeddings


