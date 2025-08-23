from src.chroma_store import ChromaEngine
from utils.reranker import Reranker
from langchain_groq import ChatGroq
from utils.process_chat_history import ChatHistory
from utils.prompt_template import PROMPT_LLM_RESPONSE, PROMPT_QUERY_ROUTER, PROMPT_REWRITE_QUERY, PROMPT_OTHER_QUERY_RESPONSE
from dotenv import load_dotenv
import os
class PipeLine:
    load_dotenv()

    def __init__(self):
        self.chroma_engine = ChromaEngine()
        self.reranker = Reranker()
        self.chat_history = ChatHistory()
        self.query_router_prompt = PROMPT_QUERY_ROUTER
        self.llm_response_prompt = PROMPT_LLM_RESPONSE
        self.rewrite_query_prompt = PROMPT_REWRITE_QUERY
        self.other_query_response_prompt = PROMPT_OTHER_QUERY_RESPONSE
    
    def call_llm(self, query: str, prompt: str) -> str:
        llm = ChatGroq(
            model=os.getenv("MODEL_LLM_NAME"),
            temperature=0,
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
        return type_of_query
    
    def handle_retrieval_query(self, query: str, text: list[str], chat_history : str) -> str:
        context = "\n".join(text)
        response = self.call_llm(query, self.llm_response_prompt.format(context=context, chat_history = chat_history))
        return response
    
    def handle_flowup_query(self, query: str, chat_history: str):
        context = ""
        prompt = self.llm_response_prompt.format(context=context, chat_history=chat_history)
        response = self.call_llm(query, prompt)
        return response
    
    def hanfle_other_query(self, query: str, chat_history: str) -> str:
        prompt = self.other_query_response_prompt.format(chat_history=chat_history)
        response = self.call_llm(query, prompt)
        return response
    
    def main(self, query: str) -> str:
        query_type = self.query_router(query)
        print(f"_____Type_query______ : {query_type}" )
        chat_history = self.chat_history.get_history()
        print(f"_____Chat history______ : {chat_history}" )
        if "tìm kiếm" in query_type:
            rewrited_query_prompt = self.rewrite_query_prompt.format(chat_history=chat_history)
            rewrited_query = self.call_llm(query, rewrited_query_prompt)
            print(f"________Rewrited query_______: {rewrited_query}")
            documents = self.chroma_engine.get_retriever(rewrited_query)
            texts= self.reranker.reranking(rewrited_query, documents)
            response = self.handle_retrieval_query(query, texts, chat_history)
        elif "tiếp tục" in query_type:
            response = self.handle_flowup_query(query, self.chat_history.get_history())
        else:
            response = self.hanfle_other_query(query, self.chat_history.get_history())
        
        self.chat_history.add_message(query, response)
        return response

# if __name__ == "__main__":
#     pipeline = PipeLine()
#     query = "đèn led NLMT giá tốt"
#     response = pipeline.main(query)
#     print(f"Response: {response}")
          