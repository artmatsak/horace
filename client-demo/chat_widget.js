const socket = new WebSocket("ws://localhost:8001");

const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");

socket.addEventListener("open", (event) => {
  console.log("WebSocket connection opened:", event);
});

socket.addEventListener("message", (event) => {
  const data = JSON.parse(event.data);
  handleMessage(data);
});

socket.addEventListener("error", (event) => {
  console.error("WebSocket error:", event);
  displayError("An error has occurred");
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
      // Handle state changes if needed
      break;
    case "error":
      displayError(data.message);
      break;
    default:
      console.warn("Unhandled message type:", data.type);
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
  chatBubble.classList.add(source === "ai" ? "ai-message" : "user-message");
  chatBubble.innerHTML = text.replace(/\n/g, "<br>"); // Replace new lines with <br> tags
  chatMessages.appendChild(chatBubble);
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
