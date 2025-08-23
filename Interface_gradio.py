import gradio as gr
from main import PipeLine

pipeline = PipeLine()

def chat_fn(user_input):
    return pipeline.main(user_input)

demo = gr.Interface(
    fn=chat_fn,
    inputs=gr.Textbox(lines=2, placeholder="Nhập câu hỏi..."),
    outputs="text",
    title="Tư vẫn viên bán hàng ADUC",
    description="Hãy đặt câu hỏi về sản phẩm anh chị đang quan tâm."
)

if __name__ == "__main__":
    demo.launch()