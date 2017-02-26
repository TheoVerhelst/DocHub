(function() {

var dmp = new diff_match_patch();

// Returns which insertion and deletion has been made between two strings
function computeEdition(oldString, newString)
{
    // diff-match-patch configuration
    dmp.Diff_Timeout = 0.1; // Timeout for the diff computation
    dmp.Diff_EditCost = 10;

    // Magic values for diff results data structure
    var Diff_match = 0, Diff_deletion = -1, Diff_insertion = 1;
    var Diff_type = 0, Diff_string = 1;

    // Get an array of all insertion, deletions and matches
    var differenceArray = dmp.diff_main(oldString, newString);
    // Clean up the result
    dmp.diff_cleanupSemantic(differenceArray);
    dmp.diff_cleanupEfficiency(differenceArray);

    // We expect to get only one insertion and/or one deletion
    var deletion = differenceArray.find(function(element) {
        return element[Diff_type] == Diff_deletion;
    });
    var insertion = differenceArray.find(function(element) {
        return element[Diff_type] == Diff_insertion;
    });

    return {
        deletion: (deletion === undefined ? 0 : deletion[Diff_string].length),
        insertion: (insertion === undefined ? "" : insertion[Diff_string])
    }
}

// Compute the markdown preview of the pad
function makePreview(event) {
    var markdown_text = $("#id_text").val()
    $("#preview-text").html(markdown.Markdown.toHTML(markdown_text));
}

var socket = null;
var padTextArea = $("#id_text");

var previousTextContent = padTextArea.val()

function onInput(event) {
    var newTextContent = padTextArea.val()
    var message = computeEdition(previousTextContent, newTextContent);
    message.type = "edit";
    socket.send(JSON.stringify(message));

    userSelection = padTextArea.getSelection();
    // Put back the previous text in the textarea, only the server can change it
    padTextArea.val(previousTextContent);
    padTextArea.setSelection(userSelection.start, userSelection.end);
}

function sendCursorPosition() {
    // Timeout because event is fired before new cursor position being effective
    setTimeout(function()
    {
        socket.send(JSON.stringify({
            type: "seek",
            position: padTextArea.getSelection().end
        }));
    }, 50);
}

function focusOut(event) {
    socket.send(JSON.stringify({
        type: "focus-out"
    }));
}

function arrowPressed(event) {
    var moveKeys = [
      40,// down
      39,// right
      38,// up
      37,// left
      36,// home
      35,// end
      34,// pageDown
      33 // pageUp
    ]
    if(moveKeys.indexOf(event.which) > -1)
        sendCursorPosition();
}

function receiveMessage(message) {
    userSelection = padTextArea.getSelection();
    var data = JSON.parse(message.data);
    padTextArea.deleteText(data.position, data.deletion);
    padTextArea.insertText(data.insertion, data.position);
    padTextArea.setSelection(userSelection.start, userSelection.end);
}

function initPad() {
    // Socket connection
    socket = new WebSocket("ws://" + window.location.host + "/pad/" + $("#document-pk").val() + "/");
    socket.onmessage = receiveMessage;
    // Call onopen directly if socket is already open
    if(socket.readyState == WebSocket.OPEN)
        socket.onopen();

    //Event bindings
    $("#preview-tab-link").click(makePreview);
    padTextArea.on("input", onInput);
    padTextArea.click(sendCursorPosition);
    padTextArea.focusout(focusOut);
    padTextArea.keydown(arrowPressed);

    makePreview({});
}

$(document).ready(initPad);
})();
