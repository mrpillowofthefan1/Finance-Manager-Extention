// popup.js
chrome.runtime.onMessage.addListener((message) => {
  document.getElementById('recommendation').innerText = message.recommendation || "No recommendation available.";
});
