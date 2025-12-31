import os
from langchain.document_loaders import PyPDFLoader, TextLoader

def load_documents(folder_path="knowledge_base/docs"):
    documents = []
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        if filename.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif filename.endswith('.txt'):
            loader = TextLoader(file_path)
        else:
            continue
            
        documents.extend(loader.load())
    
    return documents