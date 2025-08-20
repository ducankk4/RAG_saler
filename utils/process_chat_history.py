class ChatHistory:
    def __init__(self):
        self.messages = []
        self.len_message = 5

    def add_message(self, query: str, response: str):
        self.messages.append({"query": query, "response": response})

    def get_history(self):
        if len(self.messages) > self.len_message:
            self.messages = self.messages[-self.len_message:]
        else:
            chat_history = ""
            if len(self.messages) !=0:
                for message in self.messages:
                    chat_history += f"Câu hỏi: {message['query']}\n Phản hồi: {message['response']}\n\n"
                return chat_history.strip()
        return chat_history
    
    