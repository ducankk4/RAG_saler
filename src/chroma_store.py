import pandas as pd 
import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever


class ChromaEngine:
    load_dotenv()

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.data_path = os.getenv("DATA_PATH")
        self.search_kwargs = 5
    
    def load_data(self):
        try:
            df = pd.read_excel("data\data_final_NORMAL.xlsx")
            documents = []
            for i,row in df.iterrows():
                document = (
                    f"Tên sản phẩm: {row['productName']}"
                    f"Mô tả ngắn gọn: {row['shortDescription']}\n"
                    f"Mô tả chi tiết: {row['productDescription']}\n"
                    f"Giá: {row['price']}\n"
                    f"Thông số kĩ thuật: {row['specifications']}\n"
                    f"Số lượt bán: {row['soldQuantity']}\n"
                )
                metadata = {
                    "Nhóm sản phẩm": row['productGroupId'],
                    "Giá": row['price'],
                    "Số lượt bán": row['soldQuantity'],
                    "Công xuất": row['power'],
                    "Cân nặng": row['weight']
                }
                documents.append(Document(page_content=document, metadata=metadata))
            return documents
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def inges_data(self):
        try:
            embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            db_file = os.path.join(self.data_path, "chroma.sqlite3")
            if not os.path.exists(db_file):
                vector_store = Chroma.from_documents(
                    documents=self.load_data(),
                    embedding_function = embedding,
                    collection_name="economics",
                    persist_directory=self.data_path
                )
                print("_____data has been created successfully _____")
                return vector_store
            else:
                vector_store = Chroma(
                    collection_name="economics",
                    embedding_function=embedding,
                    # persist_directory=self.data_path
                )
                print("_____data has been loaded successfully _____")
                print(f"____Number of documents in vector store: {len(vector_store)}______")
                return vector_store
        except Exception as e:
            print(f"Error: {e}")
            return None
            
    def ensemble_retriever(self):
        vector_store = self.inges_data()
        retriever_vanilla = vector_store.as_retriever(search_type = "similarity", search_kwargs = {"k" :self.search_kwargs})
        retriever_bm25 = BM25Retriever.from_documents(self.load_data(), search_kwargs={"k": self.search_kwargs})
        ensemble_retriever = EnsembleRetriever(
            retrievers=[retriever_vanilla, retriever_bm25],
            weights=[0.3,0.7]
        )   
        return ensemble_retriever
    
    def get_retriever(self, query:str):
        ensemble_retriever = self.ensemble_retriever()
        try:
            retrieval_docs = ensemble_retriever.invoke(query)
            if retrieval_docs:
                print(f"Retrieved {len(retrieval_docs)} documents for the query: {query}")
                return retrieval_docs
            else :
                print("No documents found for the query.")
                return None
        except Exception as e:
            print(f"Error {e}")
            return None


