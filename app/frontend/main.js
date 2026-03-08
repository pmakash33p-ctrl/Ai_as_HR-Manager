const chatWindow = document.getElementById('chat-window');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const micBtn = document.getElementById('mic-btn');
const stopMicBtn = document.getElementById('stop-mic');
const voiceOverlay = document.getElementById('voice-overlay');
const sttPreview = document.getElementById('stt-preview');
const voiceToggle = document.getElementById('voice-toggle');

const API_URL = 'http://localhost:8000';
const urlParams = new URLSearchParams(window.location.search);
const EMPLOYEE_ID = parseInt(urlParams.get('employee_id')) || 1; // Default to John Doe (ID 1)

// --- Initialization ---

async function fetchStats() {
    try {
        const res = await fetch(`${API_URL}/api/employee/${EMPLOYEE_ID}`);
        if (!res.ok) throw new Error('Failed to fetch stats');
        const data = await res.json();

        document.getElementById('emp-name').innerText = data.profile.name;
        document.getElementById('emp-pos').innerText = data.profile.position;
        document.getElementById('leave-bal').innerText = `${data.leave_balance.annual} Days`;
        document.getElementById('salary-val').innerText = `$${data.latest_payroll.net_pay.toLocaleString()}`;
    } catch (err) {
        console.error('Stats Error:', err);
    }
}

fetchStats();

// --- Chat Functions ---

function addMessage(text, sender = 'ai') {
    const div = document.createElement('div');
    div.className = `flex gap-4 ${sender === 'user' ? 'flex-row-reverse' : ''}`;

    const avatarClass = sender === 'user' ? 'bg-slate-700' : 'bg-indigo-600';
    const bubbleClass = sender === 'user' ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-slate-800 text-slate-200 rounded-tl-none';

    div.innerHTML = `
        <div class="w-8 h-8 ${avatarClass} rounded-full flex items-center justify-center text-[10px] font-bold">${sender === 'user' ? 'JD' : 'AI'}</div>
        <div class="message-bubble ${bubbleClass} p-4 rounded-2xl text-sm leading-relaxed shadow-lg">
            ${text}
        </div>
    `;

    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function showTyping() {
    const div = document.createElement('div');
    div.id = 'typing-indicator';
    div.className = 'flex gap-4';
    div.innerHTML = `
        <div class="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center text-[10px]">AI</div>
        <div class="bg-slate-800 p-4 rounded-2xl rounded-tl-none flex gap-1">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        </div>
    `;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function removeTyping() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
}

async function sendMessage(text) {
    if (!text.trim()) return;

    addMessage(text, 'user');
    chatInput.value = '';

    // --- Fail-safe: Detect Direct Leave Requests ---
    if (text.toLowerCase().includes('apply') && text.match(/\d{4}-\d{2}-\d{2}/g)) {
        const dates = text.match(/\d{4}-\d{2}-\d{2}/g);
        if (dates.length >= 2) {
            showTyping();
            try {
                const res = await fetch(`${API_URL}/api/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: `Applying leave from ${dates[0]} to ${dates[1]} (Manual Trigger)`, employee_id: EMPLOYEE_ID })
                });
                const data = await res.json();
                removeTyping();
                addMessage(data.response, 'ai');
                fetchStats(); // Force refresh
                return;
            } catch (e) { }
        }
    }

    try {
        const res = await fetch(`${API_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, employee_id: EMPLOYEE_ID })
        });

        const data = await res.json();
        removeTyping();
        addMessage(data.response, 'ai');

        if (voiceToggle.checked) {
            speak(data.response);
        }

        if (data.action_taken) {
            fetchStats(); // Update dashboard if action was taken
        }
    } catch (err) {
        removeTyping();
        addMessage('Sorry, I am having trouble connecting to the server.', 'ai');
        console.error('Chat Error:', err);
    }
}

// --- Voice Functions (STT & TTS) ---

const recognition = 'webkitSpeechRecognition' in window ? new webkitSpeechRecognition() : null;

if (recognition) {
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        voiceOverlay.classList.remove('hidden');
        voiceOverlay.classList.add('flex');
        sttPreview.innerText = 'Listening...';
    };

    recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
            .map(result => result[0])
            .map(result => result.transcript)
            .join('');
        sttPreview.innerText = transcript;
    };

    recognition.onerror = () => {
        voiceOverlay.classList.add('hidden');
    };

    recognition.onend = () => {
        voiceOverlay.classList.add('hidden');
        if (sttPreview.innerText !== 'Listening...' && sttPreview.innerText.trim() !== '') {
            sendMessage(sttPreview.innerText);
        }
    };
}

function speak(text) {
    if (!('speechSynthesis' in window)) return;

    // Stop any current speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 0.8;

    window.speechSynthesis.speak(utterance);
}

// --- Event Listeners ---

sendBtn.addEventListener('click', () => sendMessage(chatInput.value));
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage(chatInput.value);
});

micBtn.addEventListener('click', () => {
    if (recognition) recognition.start();
    else alert('Speech recognition not supported in this browser.');
});

stopMicBtn.addEventListener('click', () => {
    if (recognition) recognition.stop();
});

document.getElementById('theme-toggle').addEventListener('click', () => {
    document.documentElement.classList.toggle('dark');
    const icon = document.querySelector('#theme-toggle i');
    if (document.documentElement.classList.contains('dark')) {
        icon.className = 'fas fa-moon';
        document.body.style.backgroundColor = '#0f172a';
    } else {
        icon.className = 'fas fa-sun';
        document.body.style.backgroundColor = '#f8fafc';
    }
});
