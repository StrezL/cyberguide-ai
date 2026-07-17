const form = document.querySelector("#ask");
const question = document.querySelector("#question");
const level = document.querySelector("#level");
const mode = document.querySelector("#mode");
const askButton = document.querySelector("#ask-button");
const answerPanel = document.querySelector("#answer-panel");
const answerText = document.querySelector("#answer-text");
const selectedDomain = document.querySelector("#selected-domain");
let domain = "General Security";

const domainKeywords = {
  "Network Security": ["network", "firewall", "vpn", "ids", "ips", "segmentation", "router"],
  Cryptography: ["cryptography", "encryption", "decrypt", "hash", "cipher", "digital signature", "key"],
  "Cloud Security": ["cloud", "aws", "azure", "shared responsibility", "storage bucket"],
  "Information Security": ["information security", "cia triad", "confidentiality", "integrity", "access control", "data loss"],
  "Social Engineering": ["social engineering", "impersonation", "pretexting", "baiting"],
  Malware: ["malware", "virus", "worm", "trojan", "ransomware", "spyware"],
  "Internet Threats": ["phishing", "scam", "unsafe website", "internet threat"],
  "Defensive Measures": ["protect", "prevent", "defense", "defensive", "security checklist"],
};

function inferDomain(text) {
  const normalized = text.toLowerCase();
  for (const [candidate, keywords] of Object.entries(domainKeywords)) {
    if (keywords.some((keyword) => normalized.includes(keyword))) return candidate;
  }
  return "General Security";
}

function setPrompt(text, nextDomain) {
  question.value = text;
  if (nextDomain) {
    domain = nextDomain;
    selectedDomain.textContent = nextDomain;
  }
  question.focus();
  document.querySelector("#ask").scrollIntoView({ behavior: "smooth", block: "center" });
}

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => setPrompt(button.dataset.prompt, button.dataset.domain));
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const value = question.value.trim();
  if (!value) return;

  domain = inferDomain(value);
  selectedDomain.textContent = domain;

  askButton.disabled = true;
  askButton.textContent = "Thinking…";
  answerText.textContent = "";
  answerPanel.classList.remove("hidden");
  answerPanel.classList.add("loading");

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: value, domain, level: level.value, mode: mode.value }),
    });
    if (!response.ok || !response.body) throw new Error("Request failed");
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    while (true) {
      const { value: chunk, done } = await reader.read();
      if (done) break;
      answerText.textContent += decoder.decode(chunk, { stream: true });
    }
  } catch (error) {
    answerText.textContent = "The request could not be completed. Please check the connection and try again.";
  } finally {
    answerPanel.classList.remove("loading");
    askButton.disabled = false;
    askButton.textContent = "Ask AI";
  }
});

question.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

document.querySelector("#copy-answer").addEventListener("click", async (event) => {
  await navigator.clipboard.writeText(answerText.textContent);
  event.currentTarget.textContent = "Copied";
  window.setTimeout(() => (event.currentTarget.textContent = "Copy"), 1200);
});
