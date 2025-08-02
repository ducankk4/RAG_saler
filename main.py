from src.chroma_store import ChromaEngine
from utils.reranker import Reranker
from langchain_groq import ChatGroq
from utils.prompt_template import PROMPT_LLM_RESPONSE, PROMPT_QUERY_ROUTER, PROMPT_REWRITE_QUERY
from dotenv import load_dotenv
import os
class PipeLine:
    load_dotenv()

    def __init__(self):
        self.chroma_engine = ChromaEngine()
        self.reranker = Reranker()
        self.query_router_prompt = PROMPT_QUERY_ROUTER
        self.llm_response_prompt = PROMPT_LLM_RESPONSE
        self.rewrite_query_prompt = PROMPT_REWRITE_QUERY
    
    def call_llm(self, query: str, prompt: str) -> str:
        llm = ChatGroq(
            model=os.getenv("MODEL_LLM_NAME"),
            temperature=0.2,
            max_tokens=None,
            reasoning_format="parsed",
            timeout=None,
            max_retries=2,
            api_key=os.getenv("GROQ_API_KEY"),
        )
        message = [
            ("system", prompt ),
            ("human", query)
        ]
        return (llm.invoke(message)).content
    
    def query_router(self, query: str) -> str:
        type_of_query = self.call_llm(query, self.query_router_prompt)
        print(f"Query type: {type_of_query}")
        return type_of_query
    
    def solve_sale_query(self, query: str, text: list[str]) -> str:
        context = "\n".join(text)
        response = self.call_llm(query, self.llm_response_prompt.format(context=context))
        return response
    
    def solve_other_query(self, query: str) -> str:
        response = self.call_llm(query, self.llm_response_prompt.format(context=""))
        return response
    
    def main(self, query: str) -> str:
        query_type = self.query_router(query)
        if query_type == "mua bán":
            documents = self.chroma_engine.get_retriever(query)
            texts= self.reranker.reranking(query, documents)
            response = self.solve_sale_query(query, texts)
        else:
            response = self.solve_other_query(query)
        return response

if __name__ == "__main__":
    pipeline = PipeLine()
    query = "bên em có bán đèn ngủ tiết kiệm điện không nhỉ"
    response = pipeline.main(query)
    print(f"Response: {response}")
          