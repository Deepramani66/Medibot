$(document).ready(function() {
    const chatMessages = $('#chatMessages');
    const messageForm = $('#messageForm');
    const messageInput = $('#messageInput');
    const sendButton = $('#sendButton');
    
    // Scroll to bottom of chat
    function scrollToBottom() {
        chatMessages.scrollTop(chatMessages[0].scrollHeight);
    }
    
    // Get current time in HH:MM format
    function getCurrentTime() {
        const now = new Date();
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    }
    
    // Parse <think></think> from AI response
function parseAIResponse(text) {
    let thinking = '';
    let response = text;

    const thinkRegex = /<think>([\s\S]*?)<\/think>/i;
    const match = text.match(thinkRegex);

    if (match) {
        thinking = match[1].trim();
        response = text.replace(match[0], '').trim();
    }

    return {
        thinking: thinking || null,
        response: response
    };
}


    // Add message to chat
    function addMessage(content, isUser = false, isTyping = false) {
        const time = getCurrentTime();
        let messageHtml;
        
        if (isTyping) {
            messageHtml = `
                <div class="message bot-message typing-message">
                    <div class="message-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <div class="message-bubble">
                            <div class="typing-indicator">
                                <div class="typing-dot"></div>
                                <div class="typing-dot"></div>
                                <div class="typing-dot"></div>
                            </div>
                        </div>
                        <div class="message-time">${time}</div>
                    </div>
                </div>
            `;
        } else if (isUser) {
            messageHtml = `
                <div class="message user-message">
                    <div class="message-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="message-content">
                        <div class="message-bubble">${content}</div>
                        <div class="message-time">${time}</div>
                    </div>
                </div>
            `;
        } else {
            // For bot messages with thinking process
            if (content.thinking && content.response) {
                messageHtml = `
                    <div class="message bot-message">
                        <div class="message-avatar">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="message-content">
                            <div class="message-bubble">
                                <!-- Thinking Box -->
                                <div class="thinking-container">
                                    <div class="thinking-header" onclick="toggleThinking(this)">
                                        <div class="thinking-title">
                                            <i class="fas fa-brain"></i>
                                            AI Thinking Process
                                        </div>
                                        <button class="thinking-toggle">
                                            <i class="fas fa-chevron-down"></i>
                                            <span>Show Details</span>
                                        </button>
                                    </div>
                                    <div class="thinking-content">
                                        ${content.thinking}
                                    </div>
                                </div>
                                
                                <!-- Final Response -->
                                <div class="final-response">
                                    <h5><i class="fas fa-stethoscope"></i> Medical Assessment</h5>
                                    <div>${content.response}</div>
                                    ${content.context_count ? 
                                        `<div style="margin-top: 10px; font-size: 0.85rem; color: #6c757d; font-style: italic;">
                                            <i class="fas fa-database"></i> Analyzed ${content.context_count} medical sources
                                        </div>` 
                                        : ''
                                    }
                                </div>
                            </div>
                            <div class="message-time">${time}</div>
                        </div>
                    </div>
                `;
            } else {
                // Simple bot message
                messageHtml = `
                    <div class="message bot-message">
                        <div class="message-avatar">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="message-content">
                            <div class="message-bubble">${content}</div>
                            <div class="message-time">${time}</div>
                        </div>
                    </div>
                `;
            }
        }
        
        chatMessages.append(messageHtml);
        scrollToBottom();
        
        // Return the message element
        return chatMessages.children().last();
    }
    
    // Toggle thinking content visibility
    window.toggleThinking = function(headerElement) {
        const container = headerElement.closest('.thinking-container');
        const content = container.querySelector('.thinking-content');
        const toggleBtn = headerElement.querySelector('.thinking-toggle');
        const icon = toggleBtn.querySelector('i');
        const textSpan = toggleBtn.querySelector('span');
        
        content.classList.toggle('expanded');
        headerElement.classList.toggle('expanded');
        
        if (content.classList.contains('expanded')) {
            icon.className = 'fas fa-chevron-up';
            textSpan.textContent = 'Hide Details';
        } else {
            icon.className = 'fas fa-chevron-down';
            textSpan.textContent = 'Show Details';
        }
    };
    
    // Handle form submission
    messageForm.on('submit', function(e) {
        e.preventDefault();
        
        const message = messageInput.val().trim();
        if (!message) return;
        
        // Clear input
        messageInput.val('');
        
        // Add user message
        addMessage(message, true);
        
        // Add typing indicator
        const typingMessage = addMessage('', false, true);
        
        // Disable send button during processing
        sendButton.prop('disabled', true);
        
        // Send request to server
        $.ajax({
            url: '/get',
            type: 'POST',
            data: { msg: message },
            dataType: 'json',
            success: function(response) {
    typingMessage.remove();

    // response is JSON OR string
    let parsed;

    if (typeof response === 'string') {
        parsed = parseAIResponse(response);
    } else if (response.response) {
        parsed = parseAIResponse(response.response);
    } else {
        parsed = response;
    }

    addMessage(parsed, false);
},

            error: function(xhr, status, error) {
                // Remove typing indicator
                typingMessage.remove();
                
                // Add error message
                const errorMessage = {
                    thinking: "An error occurred while processing your request.",
                    response: "Please try again or rephrase your question. If the problem persists, contact support."
                };
                addMessage(errorMessage, false);
            },
            complete: function() {
                // Re-enable send button
                sendButton.prop('disabled', false);
                messageInput.focus();
            }
        });
    });
    
    // Handle Enter key (but allow Shift+Enter for new line)
    messageInput.on('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            messageForm.submit();
        }
    });
    
    // Auto-focus on input
    messageInput.focus();
    
    // Initial scroll to bottom
    scrollToBottom();
});