from sentence_transformers import CrossEncoder
from langchain_core.documents import Document
from dotenv import load_dotenv
import os

class Reranker:
    load_dotenv()

    def __init__(self):
        self.model = CrossEncoder(os.getenv("MODEL_RERANKER_NAME"))

    def reranking(self, query : str, documents : list[Document]) -> list[str]:
        page_contents = []
        for doc in documents:
            page_contents.append(doc.page_content)
        scores = self.model.predict([(query, page_content) for page_content in page_contents])
        
        top_k_documents = list(sorted(zip(page_contents, scores), key = lambda x: x[1], reverse=True))
        top_k_page_contents = [doc for doc, score in top_k_documents[:5]]
        print(f"Top 5 documents after reranking: {top_k_page_contents}")
        return top_k_page_contents
