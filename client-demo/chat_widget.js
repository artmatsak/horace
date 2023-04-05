const socket = new WebSocket("ws://localhost:8001");

const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatSend = document.getElementById("chat-send");

let typingBubble = null;

socket.addEventListener("open", (event) => {
  console.log("WebSocket connection opened:", event);
});

socket.addEventListener("message", (event) => {
  const data = JSON.parse(event.data);
  handleMessage(data);
});

socket.addEventListener("error", (event) => {
  console.error("WebSocket error:", event);
  displayError("Error connecting to chat server");
});

socket.addEventListener("close", (event) => {
  console.log("WebSocket connection closed:", event);
});

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage(chatInput.value);
  chatInput.value = "";
});

function handleMessage(data) {
  switch (data.type) {
    case "utterance":
      displayMessage(data.source, data.text);
      break;
    case "state":
      handleState(data.state);
      break;
    case "error":
      displayError(data.message);
      break;
    default:
      console.warn("Unhandled message type:", data.type);
  }
}

function handleState(state) {
  switch (state) {
    case "replying":
      chatInput.disabled = true;
      chatSend.disabled = true;
      showTypingAnimation();
      break;
    case "listening":
      chatInput.disabled = false;
      chatSend.disabled = false;
      hideTypingAnimation();
      break;
    case "ended":
      chatInput.disabled = true;
      chatSend.disabled = true;
      socket.close();
      break;
    default:
      console.warn("Unhandled state:", state);
  }
}

function sendMessage(text) {
  const message = {
    type: "utterance",
    text: text,
  };
  socket.send(JSON.stringify(message));
  displayMessage("user", text);
}

function displayMessage(source, text) {
  const chatBubble = document.createElement("div");
  chatBubble.classList.add("chat-bubble");
  chatBubble.classList.add(
    source === "ai"
      ? "ai-message"
      : source === "user"
      ? "user-message"
      : "system-message"
  );
  chatBubble.innerHTML = text.replace(/\n/g, "<br>"); // Replace new lines with <br> tags

  if (typingBubble) {
    chatMessages.insertBefore(chatBubble, typingBubble);
  } else {
    chatMessages.appendChild(chatBubble);
  }

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function displayError(message) {
  const chatBubble = document.createElement("div");
  chatBubble.classList.add("chat-bubble");
  chatBubble.classList.add("error-message");
  chatBubble.textContent = message;
  chatMessages.appendChild(chatBubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingAnimation() {
  if (!typingBubble) {
    typingBubble = document.createElement("div");
    typingBubble.classList.add("chat-bubble");
    typingBubble.classList.add("ai-message");

    const typingIndicator = document.createElement("div");
    typingIndicator.classList.add("typing-indicator");

    for (let i = 0; i < 3; i++) {
      const dot = document.createElement("span");
      typingIndicator.appendChild(dot);
    }

    typingBubble.appendChild(typingIndicator);
    chatMessages.appendChild(typingBubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
}

function hideTypingAnimation() {
  if (typingBubble) {
    chatMessages.removeChild(typingBubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    typingBubble = null;
  }
}
