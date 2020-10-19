var sentenceQueue = [];
var journalistQueue = [];
var original = true;
var totalWords = 0;
var misinfoWords = 0;
var politicalColors = {
    "left": "#1565c0",
    "left-center": "#42a5f5",
    "center": "#ba68c8",
    "right-center": "#e57373",
    "right": "#e53935",
}
var mouseOverMisinformation = false;
var mouseOverJournalist = false;

function highlightMisinfo(data) {
    var context = document.body; // requires an element with class "context" to exist
    var instance = new Mark(context);
    var i
    var options = {
        "accuracy": "exactly",
        "separateWordSearch": false,
        "className": "MarkUpMisinformation",
        "exclude": [".MarkUpMisinformation", ".misinfoBoxes", "#headingTab", ".blockTabs", ".blockTabInfo"],
        "each": function (node) {
            // node is the marked DOM element
            var box = document.createElement('div');
            let boxStyle = box.style;
            box.className = "misinfoBoxes";

            //boxStyle.top = coords.bottom + "px";
            createBoxHTML(box, data, i);

            document.body.appendChild(box);

            //show box
            node.onmouseover = function (event) {
                mouseOverMisinformation = true;

                if (mouseOverJournalist === false) {
                    //let box = node.firstElementChild.style;
                    let coords = getCoords(node);
                    boxStyle.width = node.offsetWidth + "px";
                    boxStyle.left = coords.left + "px";
                    boxStyle.top = coords.bottom + "px";
                    box.style.display = 'block'; //display box
                    box.style.position = "absolute"
                }
            };

            //hide box
            node.onmouseout = function (event) {
                mouseOverMisinformation = false;
                //let box = node.firstElementChild.style;
                box.style.display = 'none'; //hide box

            };

            box.onmouseenter = function (event) {
                mouseOverMisinformation = true;
                box.style.display = 'block'; //display box
            };

            box.onmouseleave = function (event) {
                mouseOverMisinformation = false;
                boxStyle.display = 'none'; //hide box

            };
        }
    };
    for (i = 0; i < data.length; i++) {
        misinfoWords = misinfoWords + data[i].sentence.length;
        instance.mark(data[i].sentence, options);
    }
}

function highlightJournalists() {
    var i
    var context = document.body // requires an element with class "context" to exist
    var instance = new Mark(context);
    var options = {
        "accuracy": {
            "value": "exactly",
            "limiters": [",", "."]
        },
        "exclude": [".MarkUpJournalists", ".misinfoBoxes", "#headingTab", ".blockTabs", ".blockTabInfo"],
        "separateWordSearch": false,
        "className": "MarkUpJournalists",
        "caseSensitive": false,
        "each": function (node) {
            // node is the marked DOM element
            node.style.zIndex = node.style.zIndex + 1;
            var box = document.createElement('div');
            let boxStyle = box.style;
            box.className = "misinfoBoxes";

            //boxStyle.top = coords.bottom + "px";
            createBoxJournalists(node, box, i);

            document.body.appendChild(box);

            //show box
            node.onmouseover = function (event) {
                mouseOverJournalist = true;

                if (mouseOverMisinformation === false) {
                    //let box = node.firstElementChild.style;
                    let coords = getCoords(node);
                    boxStyle.width = node.offsetWidth + "px";
                    boxStyle.left = coords.left + "px";
                    boxStyle.top = coords.bottom + "px";
                    box.style.display = 'block'; //display box
                    box.style.position = "absolute"
                }
            };

            //hide box
            node.onmouseout = function (event) {
                mouseOverJournalist = false;
                //let box = node.firstElementChild.style;
                box.style.display = 'none'; //hide box

            };

            box.onmouseenter = function (event) {
                mouseOverJournalist = true;
                box.style.display = 'block'; //display box
            };

            box.onmouseleave = function (event) {
                mouseOverJournalist = false;
                boxStyle.display = 'none'; //hide box

            };
        }
    };
    for (i = 0; i < journalistQueue.length; i++) {
        instance.mark(journalistQueue[i].Name, options);
    }
}

function getJournalists() {
    journalistQueue = [];
    for (var i = 0; i < journalists.length; i++) {
        if (document.body.innerText.toLowerCase().indexOf(journalists[i].Name.toLowerCase()) >= 0) {
            journalistQueue.push(journalists[i]);
        }
    }
}

function updatePage() {

    if (original == true) {
        if (document.body.innerText.length > 50000) {
            sentenceQueue.push(document.body.innerText.substring(0, 50000));
            totalWords = 50000;
        }
        else {
            sentenceQueue.push(document.body.innerText);
            totalWords = document.body.innerText.length;
        }
    }

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("POST", "http://localhost:8080/api", true);
    xmlHttp.setRequestHeader("Content-Type", "application/json");
    xmlHttp.onload = function(e) {
        var misinformationData = JSON.parse(xmlHttp.responseText);
        highlightMisinfo(misinformationData);
        highlightJournalists();
        sentenceQueue = [];
        if (original == true) {
            initiateAddedNodes();
        }
        original = false;
        chrome.runtime.sendMessage({
            type: "pageUpdated"
        });
        chrome.runtime.sendMessage({
            type: "sendPercent",
            percent: parseInt(100 * (misinfoWords / totalWords), 10)
        });
    };
    xmlHttp.send(JSON.stringify(sentenceQueue));
    getJournalists();
}

function getCoords(node) {
    let box = node.getBoundingClientRect();

    return {
        top: box.top + window.pageYOffset,
        right: box.right + window.pageXOffset,
        bottom: box.bottom + window.pageYOffset,
        left: box.left + window.pageXOffset
    };
}

function createBoxHTML(box, data, index) {

    var header = document.createElement('center');
    header.id = "headingTab";
    header.innerText = "Situation Consensus";
    box.appendChild(header);

    for (var i = 0; i < data[index].results.length; i++) {
        var button = document.createElement('a');
        button.href = data[index].results[i].source;
        button.target = "_blank";
        button.className = "blockTabs";
        button.innerText = data[index].results[i].correct;
        box.appendChild(button);
    }
}

function createBoxJournalists(node, box, index) {
    node.style.backgroundColor = politicalColors[journalistQueue[index].Rating];
    var header = document.createElement('center');
    header.id = "headingTab";
    header.innerText = journalistQueue[index].Name;
    box.appendChild(header);

    var tab = document.createElement('div');
    tab.className = "blockTabInfo";
    var span1 = document.createElement('span');
    span1.innerText = "This person is considered to have a ";
    tab.appendChild(span1);
    var link = document.createElement('a');
    link.innerText = journalistQueue[index].Rating;
    link.style.color = politicalColors[journalistQueue[index].Rating];
    link.style.fontWeight = "bold";
    link.href = journalistQueue[index].URL;
    link.target = "_blank";
    tab.appendChild(link);
    var span2 = document.createElement('span');
    span2.innerText = " leaning. " + parseInt(parseFloat(journalistQueue[index].Percent) * 100, 10) + "% of people agree with this rating.";
    tab.appendChild(span2);
    box.appendChild(tab);
}

function initiateAddedNodes() {
    let observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (!mutation.addedNodes)
                return

            for (let i = 0; i < mutation.addedNodes.length; i++) {
                let node = mutation.addedNodes[i]
                if (node.innerText && node.className != "misinfoBoxes" && node.className != "markUpMisinformation" && node.className != "markUpJournalists") {
                    if (node.innerText.split(" ").length > 7) {
                        sentenceQueue.push(node.innerText);
                        totalWords = totalWords + node.innerText.length;
                    }
                }
            }
        })
    })

    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: false,
        characterData: false
    })
}

chrome.runtime.onMessage.addListener(
    function (request) {
        if (request.type == "checkPage")
            updatePage();
        else if (request.type == "findMisinformationPercent") {
            if (totalWords == 0) {
                chrome.runtime.sendMessage({
                    type: "sendPercent",
                    percent: -1
                });
            } else {
                chrome.runtime.sendMessage({
                    type: "sendPercent",
                    percent: parseInt(100 * (misinfoWords / totalWords), 10)
                });
            }
        }
        else if (request.type == "checkLength") {
            if (document.body.innerText.length > 50000) {
                chrome.runtime.sendMessage({
                    type: "lengthChecked",
                    tooLong: true
                });
            } else {
                chrome.runtime.sendMessage({
                    type: "lengthChecked",
                    tooLong: false
                });
            }
        }
    });
