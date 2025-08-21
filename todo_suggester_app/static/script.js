// Fetches suggestions from the server based on user input
async function fetchSuggestions() {
  const habits = document.getElementById("habits").value.trim(); // Get user input
  const btn = document.getElementById("generateBtn");
  btn.disabled = true; // Disable button to prevent multiple clicks
  btn.innerText = "Thinking..."; // Show loading state
  try {
    // Send POST request to /suggest endpoint with habits as payload
    const res = await fetch("/suggest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ habits })
    });
    const data = await res.json(); // Parse response as JSON
    renderSuggestions(data.suggestions || [], habits); // Render suggestions
  } catch (e) {
    showToast("Something went wrong. Please try again."); // Show error message
    console.error(e);
  } finally {
    btn.disabled = false; // Re-enable button
    btn.innerText = "Generate 5 actions"; // Reset button text
  }
}

// Renders suggestion cards in the UI
function renderSuggestions(items, habits) {
  const container = document.getElementById("suggestions");
  container.innerHTML = ""; // Clear previous suggestions
  items.forEach((text, idx) => {
    const card = document.createElement("div");
    card.className = "suggestion";
    // Badge showing the suggestion number
    const badge = document.createElement("div");
    badge.className = "badge";
    badge.textContent = idx + 1;
    // Suggestion text
    const content = document.createElement("div");
    content.innerHTML = `<div>${text}</div>`;
    // Thumbs up/down feedback buttons
    const thumb = document.createElement("div");
    thumb.className = "thumb";
    const up = document.createElement("button");
    up.textContent = "👍";
    up.title = "Helpful";
    const down = document.createElement("button");
    down.textContent = "👎";
    down.title = "Not helpful";
    // Attach feedback handlers
    up.onclick = () => sendFeedback(habits, text, +1);
    down.onclick = () => sendFeedback(habits, text, -1);
    thumb.appendChild(up); 
    thumb.appendChild(down);
    // Assemble card
    card.appendChild(badge);
    card.appendChild(content);
    card.appendChild(thumb);
    container.appendChild(card);
  });
}

// Sends user feedback (thumbs up/down) to the server
async function sendFeedback(habits, task, rating) {
  try {
    // POST feedback to /feedback endpoint
    const res = await fetch("/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ habits, task, rating })
    });
    const data = await res.json();
    if (data.ok) {
      // Show thank you message based on feedback
      showToast(rating > 0 ? "Thanks! I'll suggest more like this." : "Got it. I'll suggest fewer like this.");
    }
  } catch (e) {
    console.error(e);
  }
}

// Shows a temporary toast notification
function showToast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 1800); // Hide after 1.8s
}

// Set up event listeners after DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  // Button click triggers suggestion fetch
  document.getElementById("generateBtn").addEventListener("click", fetchSuggestions);
  // Ctrl+Enter or Cmd+Enter in input also triggers fetch
  document.getElementById("habits").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      fetchSuggestions();
    }
  });
});
