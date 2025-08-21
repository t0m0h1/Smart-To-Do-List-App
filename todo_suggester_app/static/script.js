async function fetchSuggestions() {
  const habits = document.getElementById("habits").value.trim();
  const btn = document.getElementById("generateBtn");
  btn.disabled = true;
  btn.innerText = "Thinking...";
  try {
    const res = await fetch("/suggest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ habits })
    });
    const data = await res.json();
    renderSuggestions(data.suggestions || [], habits);
  } catch (e) {
    showToast("Something went wrong. Please try again.");
    console.error(e);
  } finally {
    btn.disabled = false;
    btn.innerText = "Generate 5 actions";
  }
}

function renderSuggestions(items, habits) {
  const container = document.getElementById("suggestions");
  container.innerHTML = "";
  items.forEach((text, idx) => {
    const card = document.createElement("div");
    card.className = "suggestion";
    const badge = document.createElement("div");
    badge.className = "badge";
    badge.textContent = idx + 1;
    const content = document.createElement("div");
    content.innerHTML = `<div>${text}</div>`;
    const thumb = document.createElement("div");
    thumb.className = "thumb";
    const up = document.createElement("button");
    up.textContent = "👍";
    up.title = "Helpful";
    const down = document.createElement("button");
    down.textContent = "👎";
    down.title = "Not helpful";
    up.onclick = () => sendFeedback(habits, text, +1);
    down.onclick = () => sendFeedback(habits, text, -1);
    thumb.appendChild(up); thumb.appendChild(down);
    card.appendChild(badge);
    card.appendChild(content);
    card.appendChild(thumb);
    container.appendChild(card);
  });
}

async function sendFeedback(habits, task, rating) {
  try {
    const res = await fetch("/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ habits, task, rating })
    });
    const data = await res.json();
    if (data.ok) {
      showToast(rating > 0 ? "Thanks! I'll suggest more like this." : "Got it. I'll suggest fewer like this.");
    }
  } catch (e) {
    console.error(e);
  }
}

function showToast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 1800);
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("generateBtn").addEventListener("click", fetchSuggestions);
  document.getElementById("habits").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      fetchSuggestions();
    }
  });
});
