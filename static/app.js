const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message");
const clearButton = document.getElementById("clear-chat");
const providerBadge = document.getElementById("provider-badge");

const storageKey = "topic-rag-chat-history";
let history = loadHistory();

renderHistory();
scrollToBottom();

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) {
    return;
  }

  appendMessage("user", message);
  history.push({ role: "user", content: message });
  messageInput.value = "";
  setBusy(true);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, history }),
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const payload = await response.json();
    providerBadge.textContent = payload.provider;
    appendAssistantReply(payload.answer, payload.sources || []);
    history.push({ role: "assistant", content: payload.answer });
    saveHistory();
  } catch (error) {
    appendMessage("assistant", `I could not reach the server: ${error.message}`);
  } finally {
    setBusy(false);
    messageInput.focus();
  }
});

clearButton.addEventListener("click", () => {
  history = [];
  saveHistory();
  chatLog.innerHTML = "";
  providerBadge.textContent = "local";
  messageInput.focus();
});

function appendMessage(role, text) {
  const message = document.createElement("article");
  message.className = `message ${role}`;
  message.innerHTML = `<span class="label">${role}</span>${escapeHtml(text).replace(/\n/g, "<br />")}`;
  chatLog.appendChild(message);
  scrollToBottom();
}

function appendAssistantReply(answer, sources) {
  const message = document.createElement("article");
  message.className = "message assistant";

  const sourceList = sources.length
    ? `<ul>${sources
        .map(
          (source) =>
            `<li><strong>${escapeHtml(source.source)}</strong> <span>(${source.score.toFixed(4)})</span><br />${escapeHtml(source.snippet)}</li>`,
        )
        .join("")}</ul>`
    : "";

  message.innerHTML = `
    <span class="label">assistant</span>
    <div>${escapeHtml(answer).replace(/\n/g, "<br />")}</div>
    ${sourceList}
  `;
  chatLog.appendChild(message);
  scrollToBottom();
}

function renderHistory() {
  chatLog.innerHTML = "";
  history.forEach((item) => {
    appendMessage(item.role, item.content);
  });
}

function setBusy(isBusy) {
  chatForm.querySelectorAll("button, textarea").forEach((element) => {
    element.disabled = isBusy;
  });
}

function scrollToBottom() {
  chatLog.scrollTop = chatLog.scrollHeight;
}

function loadHistory() {
  try {
    const raw = localStorage.getItem(storageKey);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveHistory() {
  localStorage.setItem(storageKey, JSON.stringify(history));
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
