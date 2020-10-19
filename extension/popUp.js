var countDown = 0;
var currentStatus;
var politicalBias;
var misinformationPercent;
var percentAddOn;
var setup = false;
var startTimer;
var button;
var politicalColors = {
    "Left": "#1565c0",
    "Left Center": "#42a5f5",
    "Center": "#ba68c8",
    "Right Center": "#e57373",
    "Right": "#e53935",
    "Fake News": "#ff5722",
    "Conspiracy": "#e91e63"
}

function onScanRequest() {
    let params = {
        active: true,
        currentWindow: true
    }

    chrome.tabs.query(params, gotTabs);

    function gotTabs(tabs) {
        if (countDown <= 0) {
            chrome.runtime.sendMessage({ type: "tryScan", tab: tabs[0].id });
        }
    }
}

function findPoliticalBias() {
    let params = {
        active: true,
        currentWindow: true
    }

    chrome.tabs.query(params, gotTabs);

    function gotTabs(tabs) {
        var tab = tabs[0];
        var url = new URL(tab.url)
        var domain = url.hostname;
        console.log(domain);
        if (sources[domain]) {
            politicalBias.innerText = sources[domain].bias;
            politicalBias.href = sources[domain].bias_website;
            politicalBias.onclick = function () {
                chrome.tabs.create({ active: true, url: sources[domain].bias_website });
            };
            if (politicalColors[sources[domain].bias]) {
                politicalBias.style.color = politicalColors[sources[domain].bias];
            }
        }
        else {
            politicalBias.innerText = "None Found";
        }
    }
}

function findPercentMisinfo() {
    let params = {
        active: true,
        currentWindow: true
    }

    chrome.tabs.query(params, gotTabs);

    function gotTabs(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, { type: "findMisinformationPercent" });
    }
}

function checkLength() {
    let params = {
        active: true,
        currentWindow: true
    }

    chrome.tabs.query(params, gotTabs);

    function gotTabs(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, { type: "checkLength" });
    }
}

function timer() {
   countDown--;
    currentStatus.innerText = "Please wait " + countDown + " seconds";

   if (countDown <= 0) {
       clearInterval(startTimer);
       currentStatus.innerText = "Ready to Scan";
       currentStatus.style.color = "#43a047";
   }
}

document.addEventListener('DOMContentLoaded', function () {
    button = document.getElementById('misinfoScanButton');
    currentStatus = document.getElementById("currentStatus");
    misinformationPercent = document.getElementById("pageData");
    percentAddOn = document.getElementById("limitWarning");
    politicalBias = document.getElementById("politicalBias");
    findPoliticalBias();
    checkLength();
});

chrome.runtime.onMessage.addListener(
    function (request) {
        console.log(request.type);
        if (request.type == "lengthChecked") {
            if (request.tooLong == true) {
                percentAddOn.innerText = "First 50,000 Characters";
            }
            if (setup == false) {
                setup = true;
                findPercentMisinfo();
                currentStatus.innerText = "Ready to Scan";
                currentStatus.style.color = "#43a047";
                chrome.runtime.sendMessage({ type: "setUp" });
                button.onclick = function start() {
                    onScanRequest();
                }
            }

        }
        else if (request.type == "sendPercent") {
            if (request.percent == -1) {
                misinformationPercent.innerText = "Must Scan";
            }
            else {
                misinformationPercent.innerText = request.percent + "%";
            }
        }
        else if (request.type == "setStatus") {
            if (request.status == "Check_Page") {
                currentStatus.innerText = "Scanning Page...";
                currentStatus.style.color = "black";
            }
            else if (request.status == "startTimer") {
                if (countDown <= 0) {
                    countDown = request.seconds;
                    currentStatus.innerText = "Please wait " + countDown + " seconds";
                    currentStatus.style.color = "#e53935";
                    startTimer = setInterval(timer, 1000);

                }
            }
        }    
    });