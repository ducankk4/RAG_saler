// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const typingIndicator = document.getElementById('typingIndicator');
const quickActions = document.getElementById('quickActions');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeChatbot();
    setupEventListeners();
    setWelcomeTime();
    checkApiConnection();
});

// Check API connection on startup
async function checkApiConnection() {
    try {
        const response = await fetch('/api/status');
        if (response.ok) {
            console.log('✅ API Connected Successfully');
        } else {
            console.warn('⚠️ API Connection Warning:', response.status);
        }
    } catch (error) {
        console.error('❌ API Connection Failed:', error);
        // Add notification to user
        setTimeout(() => {
            addBotMessage('⚠️ Kết nối API không ổn định. Một số tính năng có thể bị hạn chế.', true);
        }, 1000);
    }
}

function initializeChatbot() {
    // Auto-resize textarea
    autoResizeTextarea(messageInput);
    
    // Focus on input
    messageInput.focus();
    
    // Setup quick action buttons
    setupQuickActions();
}

function setupEventListeners() {
    // Send button click
    sendButton.addEventListener('click', handleSendMessage);
    
    // Enter key to send message
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    
    // Input change to toggle send button
    messageInput.addEventListener('input', function() {
        const isEmpty = this.value.trim() === '';
        sendButton.disabled = isEmpty;
        
        // Auto resize
        autoResizeTextarea(this);
    });
    
    // Hide quick actions when user starts typing
    messageInput.addEventListener('focus', function() {
        if (chatMessages.children.length === 1) { // Only welcome message
            quickActions.style.display = 'block';
        }
    });
}

function setupQuickActions() {
    const quickButtons = document.querySelectorAll('.quick-btn');
    quickButtons.forEach(button => {
        button.addEventListener('click', function() {
            const question = this.getAttribute('data-question');
            messageInput.value = question;
            messageInput.focus();
            sendButton.disabled = false;
            
            // Auto send the question
            setTimeout(() => {
                handleSendMessage();
            }, 300);
        });
    });
}

function setWelcomeTime() {
    const welcomeTimeElement = document.getElementById('welcomeTime');
    if (welcomeTimeElement) {
        welcomeTimeElement.textContent = formatTime(new Date());
    }
}

async function handleSendMessage() {
    const message = messageInput.value.trim();
    if (message === '') return;
    
    console.log('🔵 Sending message:', message);
    
    // Hide quick actions after first message
    if (chatMessages.children.length === 1) {
        quickActions.style.display = 'none';
    }
    
    // Add user message
    addUserMessage(message);
    
    // Clear input
    messageInput.value = '';
    sendButton.disabled = true;
    autoResizeTextarea(messageInput);
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Send message to backend
        console.log('📤 Calling sendMessageToBackend...');
        const response = await sendMessageToBackend(message);
        console.log('📥 Received response:', response);
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Add bot response
        addBotMessage(response);
        
    } catch (error) {
        console.error('❌ Error in handleSendMessage:', error);
        hideTypingIndicator();
        
        // More specific error message
        let errorMessage = 'Xin lỗi, đã có lỗi xảy ra. ';
        if (error.message.includes('Failed to fetch')) {
            errorMessage += 'Không thể kết nối với server. Vui lòng kiểm tra kết nối mạng.';
        } else if (error.message.includes('404')) {
            errorMessage += 'API endpoint không tồn tại.';
        } else if (error.message.includes('500')) {
            errorMessage += 'Lỗi server nội bộ.';
        } else {
            errorMessage += 'Vui lòng thử lại sau.';
        }
        
        addBotMessage(errorMessage, true);
    }
    
    // Focus back to input
    messageInput.focus();
}

function addUserMessage(message) {
    const messageDiv = createMessageElement(message, 'user');
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function addBotMessage(message, isError = false) {
    const messageDiv = createMessageElement(message, 'bot', isError);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function createMessageElement(message, sender, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const currentTime = formatTime(new Date());
    
    const avatarIcon = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
    const errorClass = isError ? ' error' : '';
    
    // Format message content to preserve line breaks
    const formattedMessage = formatMessageContent(message);
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="${avatarIcon}"></i>
        </div>
        <div class="message-content${errorClass}">
            <div class="message-text">${formattedMessage}</div>
        </div>
        <div class="message-time">
            <span>${currentTime}</span>
        </div>
    `;
    
    return messageDiv;
}

function showTypingIndicator() {
    typingIndicator.style.display = 'flex';
    scrollToBottom();
}

function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

function scrollToBottom() {
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
}

function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, 120);
    textarea.style.height = newHeight + 'px';
}

function formatTime(date) {
    return date.toLocaleTimeString('vi-VN', { 
        hour: '2-digit', 
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatMessageContent(text) {
    // Escape HTML first for security
    const escapedText = escapeHtml(text);
    // Replace line breaks with <br> tags to preserve formatting
    return escapedText.replace(/\n/g, '<br>');
}

// Backend API Communication
async function sendMessageToBackend(message) {
    console.log('🌐 Starting API call to /chat');
    
    try {
        const requestBody = {
            message: message,
            timestamp: new Date().toISOString()
        };
        
        console.log('📤 Request body:', requestBody);
        
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        console.log('📡 Response status:', response.status);
        console.log('📡 Response ok:', response.ok);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Response error text:', errorText);
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
        
        const data = await response.json();
        console.log('✅ Response data:', data);
        
        return data.reply || 'Tôi không thể trả lời câu hỏi này lúc này.';
        
    } catch (error) {
        console.error('❌ Backend communication error:', error);
        
        // Check if it's a network error
        if (error.message.includes('Failed to fetch') || error.name === 'TypeError') {
            console.log('🔄 Network error detected, using fallback response');
            return generateFallbackResponse(message);
        }
        
        // Re-throw the error to be handled by handleSendMessage
        throw error;
    }
}

// Fallback response for testing (remove when backend is connected)
function generateFallbackResponse(message) {
    const responses = [
        'Cảm ơn bạn đã hỏi! Đây là phản hồi mẫu từ chatbot.',
        'Tôi đã nhận được câu hỏi của bạn. Tính năng này đang được phát triển.',
        'Rất tiếc, tôi chưa thể kết nối với hệ thống backend. Vui lòng thử lại sau.',
        'Câu hỏi của bạn rất thú vị! Tôi sẽ cải thiện để trả lời tốt hơn.',
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
});

// Handle offline/online status
window.addEventListener('online', function() {
    console.log('Connection restored');
});

window.addEventListener('offline', function() {
    console.log('Connection lost');
    addBotMessage('Kết nối mạng bị gián đoạn. Vui lòng kiểm tra kết nối internet.', true);
});

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatTime,
        escapeHtml,
        createMessageElement
    };
}