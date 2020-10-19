var lastServerRequest = -1;
var COOLDOWN = 10;
var debounce = false;

function getCurrentTime() {
    return Math.floor(Date.now() / 1000);
}

function tryScan(tab) {
    if (debounce == false) {
        debounce = true;
        chrome.runtime.sendMessage({ type: "setStatus", status: "Check_Page"});
        chrome.tabs.sendMessage(tab, { type: "checkPage" });
    }
}

function setUp() {
    if (lastServerRequest == -1) {
        lastServerRequest = getCurrentTime() - COOLDOWN * 2;
    }

    if (getCurrentTime() - lastServerRequest < COOLDOWN) {
        chrome.runtime.sendMessage({ type: "setStatus", status: "startTimer", seconds: (COOLDOWN - (getCurrentTime() - lastServerRequest)) });
    }
}

chrome.runtime.onMessage.addListener(
    function (request) {
        if (request.type == "tryScan") {
            tryScan(request.tab);
        }
        else if (request.type == "setUp")
        {
            setUp();
        }
        else if (request.type == "pageUpdated")
        {
            debounce = false;
            lastServerRequest = getCurrentTime();
            chrome.runtime.sendMessage({ type: "setStatus", status: "startTimer", seconds: (COOLDOWN - (getCurrentTime() - lastServerRequest)) });
        }
    });