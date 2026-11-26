const API_URL = "http://localhost:8000";

const chatForm = document.getElementById("chatForm");
const questionInput = document.getElementById("questionInput");
const chatBox = document.getElementById("chatBox");
const sendButton = document.getElementById("sendButton");
const statusText = document.getElementById("status");


function addMessage(text, type) {
    const message = document.createElement("div");

    message.className = `message ${type}`;
    message.textContent = text;

    chatBox.appendChild(message);
    chatBox.scrollTop = chatBox.scrollHeight;
}


chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const question = questionInput.value.trim();

    if (!question) return;

    addMessage(question, "user");

    questionInput.value = "";
    sendButton.disabled = true;
    statusText.textContent = "Thinking...";

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Something went wrong.");
        }

        let answer = data.answer || "No answer was returned.";

        if (data.sources && data.sources.length > 0) {
            answer += "\n\nSources: " + data.sources.join(", ");
        }

        addMessage(answer, "assistant");
        statusText.textContent = "";

    } catch (error) {
        addMessage(
            "Error: " + error.message,
            "assistant"
        );

        statusText.textContent =
            "Could not connect to the backend. Check that the API is running.";

    } finally {
        sendButton.disabled = false;
        questionInput.focus();
    }
});
