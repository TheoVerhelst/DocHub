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

var serverTextContent = padTextArea.val();
var serverPosition = 0;
var requestedPosition = 0;
var serverFocusState = false;

function resetFocus() {
    // We have to unbind handlers, because handlers should be fired by user
    // input only, not programmatically (and resetFocus are called
    // on server response, not on user input).
    unbindEventHandlers();
    if(serverFocusState)
        padTextArea.focus();
    else
        padTextArea.blur();
    bindEventHandlers();
}

function resetSelection() {
    unbindEventHandlers();
    padTextArea.setSelection(serverPosition, serverPosition);
    bindEventHandlers();
}

function onInput(event) {
    var newTextContent = padTextArea.val()
    var message = computeEdition(serverTextContent, newTextContent);
    message.type = "edit";
    // It is possible to have empty edit, do not send message in that case
    if(message.insertion.length > 0 || message.deletion > 0)
    {
        socket.send(JSON.stringify(message));

        // We put back the server text in the textarea, only the server can change the textarea
        padTextArea.val(serverTextContent);
        // Bu we let the cursor move as the user type
        serverPosition = padTextArea.getSelection().end;
    }
}

function seek() {
    // Timeout because event is fired before new cursor position being effective
    setTimeout(function() {
        newPosition = padTextArea.getSelection().end;
        // This checks avoid asking two times for the same cursor position
        if(newPosition != requestedPosition)
        {
            requestedPosition = newPosition;
            if(!serverFocusState || requestedPosition != serverPosition) {
                var contextWidth = 10;
                var context = padTextArea.val().substring(requestedPosition - contextWidth, requestedPosition + contextWidth),
                    context_position = Math.min(requestedPosition, contextWidth);

                socket.send(JSON.stringify({
                    type: "seek",
                    position: requestedPosition,
                    context: context,
                    context_position: context_position
                }));
            }
        }
    }, 50);
}

function focusOut(event) {
    if(serverFocusState) {
        socket.send(JSON.stringify({
            type: "focus_out"
        }));
    }
    serverFocusState = false;
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
        seek();
}

function receiveMessage(message) {
    var data = JSON.parse(message.data)

    switch(data["type"]) {
        case "sync":
            padTextArea.val(data["content"]);
            serverTextContent = data["content"];
            serverPosition = 0;
            serverFocusState = false;
            break;

        case "seek":
            serverPosition = data["position"];
            serverFocusState = true;
            break;

        case "edit":
            if(data["deletion"] > 0)
                padTextArea.deleteText(data["position"] - data["deletion"], data["position"]);
            if(data["insertion"].length > 0)
                padTextArea.insertText(data["insertion"], data["position"]);
            serverTextContent = padTextArea.val();
            break;

        case "error":
            // Selection refused by server
            if(data["cause"] == "seek") {
                // Put back original selection
                serverPosition = data["position"];
                serverFocusState = true;
            }
            break;
    }
    resetSelection();
    resetFocus();
}

function bindEventHandlers() {
    padTextArea.on("input", onInput);
    padTextArea.on("focus", seek);
    padTextArea.on("click", seek);
    padTextArea.on("blur", focusOut);
    padTextArea.on("keydown", arrowPressed);
}

function unbindEventHandlers() {
    padTextArea.off("input", onInput);
    padTextArea.off("focus", seek);
    padTextArea.off("click", seek);
    padTextArea.off("blur", focusOut);
    padTextArea.off("keydown", arrowPressed);
}

function initPad() {

    // Socket connection
    socket = new WebSocket("ws://" + window.location.host + "/pad/" + $("#document-pk").val() + "/");
    socket.onmessage = receiveMessage;
    // Call onopen directly if socket is already open
    if(socket.readyState == WebSocket.OPEN)
        socket.onopen();

    //Event bindings
    bindEventHandlers();

    $("#preview-tab-link").click(makePreview);
    makePreview({});
}

$(document).ready(initPad);

})();
