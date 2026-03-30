document.addEventListener('DOMContentLoaded', () => {
    const micBtn = document.getElementById('mic-btn');
    const statusText = document.getElementById('status-text');
    const chatContainer = document.getElementById('chat-container');
    
    // Check browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        statusText.textContent = "Speech Recognition not supported in this browser. Try Chrome.";
        micBtn.disabled = true;
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    let isListening = false;

    const textInput = document.getElementById('text-input');
    const sendBtn = document.getElementById('send-btn');

    // Give a cool boot-up delay before typing
    setTimeout(() => {
        const initMsg = "COMMANDER BOOT SEQUENCE INITIATED... ONLINE. AWAITING INPUT.";
        typeMessage(initMsg, 'ai');
        speak("Commander boot sequence initiated. Online. Awaiting input.");
    }, 500);

    async function submitText(transcript) {
        if (!transcript.trim()) return;
        
        addMessage(transcript, 'user');
        textInput.value = '';
        
        statusText.textContent = 'ANALYZING...';
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: transcript })
            });
            const data = await response.json();
            
            typeMessage(data.response, 'ai');
            speak(data.response);
            statusText.textContent = 'SYSTEM STANDBY';
        } catch (error) {
            console.error('Error:', error);
            typeMessage('SYSTEM FAULT DETECTED.', 'ai');
            statusText.textContent = 'SYSTEM FAULT';
        }
    }

    sendBtn.addEventListener('click', () => {
        submitText(textInput.value);
    });

    textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            submitText(textInput.value);
        }
    });

    micBtn.addEventListener('click', () => {
        if (isListening) {
            recognition.stop();
        } else {
            recognition.start();
        }
    });

    recognition.onstart = () => {
        isListening = true;
        micBtn.classList.add('listening');
        statusText.textContent = 'RECORDING...';
        // Interupt any ongoing AI speech
        window.speechSynthesis.cancel();
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        
        micBtn.classList.remove('listening');
        isListening = false;
        
        // Auto submit the recognized speech
        submitText(transcript);
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        statusText.textContent = 'FAULT: ' + event.error;
        micBtn.classList.remove('listening');
        isListening = false;
    };

    recognition.onend = () => {
        if(isListening){
            micBtn.classList.remove('listening');
            isListening = false;
            statusText.textContent = 'SYSTEM STANDBY';
        }
    };

    function addMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'bubble';
        bubbleDiv.textContent = text;
        
        msgDiv.appendChild(bubbleDiv);
        chatContainer.appendChild(msgDiv);
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // High Tech Typing Animation for AI responses
    function typeMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'bubble typing-cursor';
        msgDiv.appendChild(bubbleDiv);
        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        let index = 0;
        // Typing speed: faster if text is long
        const speed = Math.max(15, 30 - (text.length / 10)); 
        
        function typeWriter() {
            if (index < text.length) {
                bubbleDiv.textContent += text.charAt(index);
                index++;
                chatContainer.scrollTop = chatContainer.scrollHeight;
                setTimeout(typeWriter, speed);
            } else {
                bubbleDiv.classList.remove('typing-cursor');
            }
        }
        typeWriter();
    }

    function speak(text) {
        if (!('speechSynthesis' in window)) return;
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
    }
});
