// Intercept 'Enter' key in textareas and contenteditable divs to pre-check prompts
document.addEventListener('keydown', (e) => {
    const target = e.target;
    const isTextarea = target.tagName === 'TEXTAREA';
    const isContentEditable = target.getAttribute('contenteditable') === 'true' || target.isContentEditable;

    if ((isTextarea || isContentEditable) && e.key === 'Enter' && !e.shiftKey) {
        const prompt = (isTextarea ? target.value : target.innerText).trim();
        if (prompt) {
            // Send to background script for analysis
            chrome.runtime.sendMessage({ type: "PRE_CHECK", prompt }, (response) => {
                if (response && response.action === "block") {
                    e.preventDefault();
                    e.stopImmediatePropagation();
                    alert(`Blocked by RyzenShield: ${response.explanation} (Score: ${response.score.toFixed(2)})`);
                }
            });
        }
    }
}, true); // Use capture phase to intercept before site's own listeners

console.log("RyzenShield Content Script Active");
