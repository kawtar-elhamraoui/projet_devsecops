from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import os

def create_vector_store(documents, persist_directory="chroma_db"):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    vectordb.persist()
    
    return vectordb