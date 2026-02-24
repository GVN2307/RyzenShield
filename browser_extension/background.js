chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "PRE_CHECK") {
        // Communicate with native host
        chrome.runtime.sendNativeMessage('com.ryzenshield.firewall', { prompt: request.prompt }, (response) => {
            if (chrome.runtime.lastError) {
                console.error("Native Messaging Error:", chrome.runtime.lastError);
                sendResponse({ action: "pass", score: 0 }); // Fallback
            } else {
                sendResponse(response);
            }
        });
        return true; // Keep message channel open for async response
    }
});

console.log("RyzenShield Background Worker Active");
