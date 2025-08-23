// Theme
const html = document.documentElement;
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');
function setTheme(mode){
    html.setAttribute('data-theme', mode);
    themeIcon.textContent = mode === 'dark' ? '☀️' : '🌙';
    themeToggle.querySelector('.btn-text').textContent = mode === 'dark' ? 'Light' : 'Dark';
    localStorage.setItem('theme', mode);
}
setTheme(localStorage.getItem('theme') || 'dark');
themeToggle.addEventListener('click', ()=>{
    setTheme(html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
});

// Elements
const messagesEl = document.getElementById('messages');
const inputEl = document.getElementById('input');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearChat');
const endEl = document.getElementById('end');
const spinner = document.getElementById('spinner');
const hintText = document.getElementById('hintText');

// Templates
const tplAssistant = document.getElementById('tpl-assistant');
const tplUser = document.getElementById('tpl-user');

// State
const messages = [];

// Utilities
function scrollToBottom(){ endEl.scrollIntoView({ behavior: 'smooth', block: 'end' }); }
function elFromTemplate(tpl){ return tpl.content.firstElementChild.cloneNode(true); }
function addMessage(role, content){
    const tpl = role === 'assistant' ? tplAssistant : tplUser;
    const node = elFromTemplate(tpl);
    node.querySelector('.content').innerHTML = renderMarkdownLite(content);
    messagesEl.appendChild(node);
    messages.push({ role, content });
    scrollToBottom();
}
function setLoading(loading){
    if(loading){ spinner.classList.remove('hidden'); hintText.textContent = 'Đang tạo câu trả lời...'; }
    else { spinner.classList.add('hidden'); hintText.textContent = 'Tip: Hỏi về sản phẩm, so sánh, hoặc tiếp nối cuộc hội thoại.'; }
}
function renderMarkdownLite(text){
    // very light markdown support: **bold**, *italic*, `code`
    return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br/>');
}

// Fake backend (replace with your API)
async function sendMessageToBackend(prompt){
    // Gửi câu hỏi tới backend FastAPI và nhận phản hồi thực
    try {
        const response = await fetch("http://localhost:8000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: prompt })
        });
        if (!response.ok) {
            throw new Error("Backend error");
        }
        const data = await response.json();
        return data.response;
    } catch (err) {
        return "⚠️ Không thể kết nối tới máy chủ. Vui lòng thử lại hoặc kiểm tra backend.";
    }
}

function streamText(text, onChunk){
    let i = 0;
    const step = Math.max(1, Math.floor(text.length/80));
    const id = setInterval(()=>{
    i += step;
    onChunk(text.slice(0, i));
    if(i >= text.length){ clearInterval(id); onChunk(text); }
    }, 16);
    return ()=> clearInterval(id);
}

async function handleSend(){
    const val = inputEl.value.trim();
    if(!val) return;
    addMessage('user', val);
    inputEl.value = '';
    setLoading(true);

    // Placeholder assistant bubble to stream into
    const node = elFromTemplate(tplAssistant);
    const contentEl = node.querySelector('.content');
    contentEl.textContent = '';
    messagesEl.appendChild(node);
    scrollToBottom();

    try {
        const full = await sendMessageToBackend(val, messages);
        contentEl.innerHTML = renderMarkdownLite(full);
        scrollToBottom();
        setLoading(false);
        messages.push({ role: 'assistant', content: full });
    } catch (err) {
        contentEl.textContent = '⚠️ Đã có lỗi khi gọi API. Vui lòng thử lại.';
        setLoading(false);
    }
}

// Events
sendBtn.addEventListener('click', handleSend);
inputEl.addEventListener('keydown', (e)=>{
    if(e.key === 'Enter' && !e.shiftKey){ e.preventDefault(); handleSend(); }
});
clearBtn.addEventListener('click', ()=>{
    messagesEl.innerHTML = '';
    messages.length = 0;
    addMessage('assistant', 'Đã tạo hội thoại mới. Hãy cho mình biết bạn quan tâm sản phẩm nào ✨');
});

// Init
addMessage('assistant', 'Chào bạn 👋 Mình là trợ lý tư vấn sản phẩm. Hãy đặt câu hỏi về các thiết bị điện tử/đồ thông minh nhé!');




