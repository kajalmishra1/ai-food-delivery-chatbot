// ============================================================
// ROBOT GREETING FUNCTIONALITY
// ============================================================

const robotOverlay = document.getElementById('robotOverlay');
const mainPage = document.getElementById('mainPage');
const enterBtn = document.getElementById('enterBtn');

// Show main chat and hide robot overlay
function enterChat() {
    robotOverlay.classList.add('hidden');
    mainPage.classList.add('visible');
    
    // Focus input after transition
    setTimeout(() => {
        document.getElementById('user-input').focus();
    }, 400);
}

// Enter button click
enterBtn.addEventListener('click', enterChat);

// Also allow pressing Enter key on the button
enterBtn.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        enterChat();
    }
});

// ============================================================
// ORIGINAL CHAT FUNCTIONALITY (unchanged)
// ============================================================

function sendMessage(prefilled) {
    const inputEl = document.getElementById("user-input");
    const input = (prefilled !== undefined ? prefilled : inputEl.value);

    if (input.trim() === "") return;

    addMessage(input, "user");
    inputEl.value = "";
    inputEl.focus();

    showTyping();

    fetch("/get", {
        method: "POST",
        body: JSON.stringify({ message: input }),
        headers: {
            "Content-Type": "application/json"
        }
    })
        .then(res => res.json())
        .then(data => {
            removeTyping();
            addMessage(data.reply, "bot", data.tag === "fallback");
        })
        .catch(() => {
            removeTyping();
            addMessage("Sorry, I'm having trouble connecting right now. Please try again in a moment.", "bot", true);
        });
}

function addMessage(text, sender, isFallback) {
    const chatbox = document.getElementById("chatbox");
    const msg = document.createElement("div");
    msg.classList.add(sender);

    if (isFallback) {
        msg.classList.add("fallback");
    }

    if (sender === "bot") {
        msg.innerHTML = `
            <div class="bot__avatar">OB</div>
            <span>${escapeHtml(text)}</span>
        `;
    } else {
        msg.textContent = text;
    }

    chatbox.appendChild(msg);
    chatbox.scrollTop = chatbox.scrollHeight;
}

function showTyping() {
    const chatbox = document.getElementById("chatbox");

    const typingDiv = document.createElement("div");
    typingDiv.classList.add("bot");
    typingDiv.id = "typing";

    typingDiv.innerHTML = `
        <div class="bot__avatar">OB</div>
        <span class="typing-dots"><span></span><span></span><span></span></span>
    `;

    chatbox.appendChild(typingDiv);
    chatbox.scrollTop = chatbox.scrollHeight;
}

function removeTyping() {
    const typing = document.getElementById("typing");
    if (typing) typing.remove();
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

// Enter key sends the message
document.getElementById("user-input").addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});

// Quick-reply chips send their preset message
document.getElementById("quickReplies").addEventListener("click", function (e) {
    const btn = e.target.closest("button");
    if (btn) {
        sendMessage(btn.dataset.msg);
    }
});

// Add greeting message when main page becomes visible
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.attributeName === 'class') {
            if (mainPage.classList.contains('visible')) {
                // Add greeting message only once
                const chatbox = document.getElementById('chatbox');
                if (chatbox.children.length === 0) {
                    addMessage("Good day! I'm OrderBuddy. Ask me about your order, delivery, refunds, or payments.", "bot");
                }
                observer.disconnect();
            }
        }
    });
});

observer.observe(mainPage, { attributes: true });
