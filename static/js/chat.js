function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function sendQuickReply(text) {
    const inputField = document.getElementById('userInput');
    inputField.value = text;
    sendMessage();
}

function sendMessage() {
    const inputField = document.getElementById('userInput');
    const sendBtn = inputField.parentElement.querySelector('button');
    const userText = inputField.value.trim();
    
    if (userText === '') return;

    const chatBox = document.getElementById('chatBox');
    const indicator = document.getElementById('typingIndicator');

    // Disable input and button while sending
    inputField.disabled = true;
    sendBtn.disabled = true;

    // Create Row wrapper for layout positioning
    const rowDiv = document.createElement('div');
    rowDiv.className = 'message-row user-row';

    const userDiv = document.createElement('div');
    userDiv.className = 'message user-message';
    userDiv.textContent = userText;
    
    rowDiv.appendChild(userDiv);
    chatBox.insertBefore(rowDiv, indicator);
    inputField.value = '';
    
    // Show indicator and push scroll viewport to bottom
    indicator.style.display = 'block';
    chatBox.scrollTop = chatBox.scrollHeight;

    // Send payload to Flask API Endpoint
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Natural micro-delay for realistic feel
        setTimeout(() => {
            indicator.style.display = 'none';
            
            const botRow = document.createElement('div');
            botRow.className = 'message-row bot-row';

            const botAvatar = document.createElement('div');
            botAvatar.className = 'bot-avatar';
            botAvatar.innerHTML = '<i class="fa-solid fa-user-tie"></i>';

            const botDiv = document.createElement('div');
            botDiv.className = 'message bot-message';
            botDiv.textContent = data.reply;

            botRow.appendChild(botAvatar);
            botRow.appendChild(botDiv);
            chatBox.insertBefore(botRow, indicator);
            chatBox.scrollTop = chatBox.scrollHeight;
            
            // Re-enable input and button
            inputField.disabled = false;
            sendBtn.disabled = false;
            inputField.focus();
        }, 650);
    })
    .catch(error => {
        indicator.style.display = 'none';
        console.error('System API Exception Error:', error);
        
        // Show error message to user
        const botRow = document.createElement('div');
        botRow.className = 'message-row bot-row';

        const botAvatar = document.createElement('div');
        botAvatar.className = 'bot-avatar';
        botAvatar.innerHTML = '<i class="fa-solid fa-user-tie"></i>';

        const botDiv = document.createElement('div');
        botDiv.className = 'message bot-message';
        botDiv.textContent = '⚠️ Sorry, I encountered an error. Please try again.';

        botRow.appendChild(botAvatar);
        botRow.appendChild(botDiv);
        chatBox.insertBefore(botRow, indicator);
        chatBox.scrollTop = chatBox.scrollHeight;
        
        // Re-enable input and button
        inputField.disabled = false;
        sendBtn.disabled = false;
        inputField.focus();
    });
}