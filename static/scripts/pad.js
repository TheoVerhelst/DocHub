(function() {

var dmp = new diff_match_patch();

// Returns which insertion and deletion has been made between two strings
function computeEdition(oldString, newString) {
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

// Configuration variables
var debugLog = false;

// Global variables
var socket = null;
var padTextArea = $("#id_text");
var serverTextContent = padTextArea.val();
var previousTextContent = serverTextContent;
var lastPosition = 0;
var lastFocusState = false;
// This is a queue of edits requested to the server
// We need a queue because we may send more than one edit before the server
// respond, so we need to buffer them all and hope the responses will come in
// the same order.
var requestedEdits = [];

function log(arg1, arg2) {
    if(debugLog) {
        console.log(arg1, arg2);
    }
}

function editsAreEqual(lhs, rhs) {
    return lhs.position === rhs.position
        && lhs.deletion === rhs.deletion
        && lhs.insertion === rhs.insertion;
}

function resetFocus() {
    // We have to unbind handlers, because handlers should be fired by user
    // input only, not programmatically (and resetFocus are called
    // on server response, not on user input).
    unbindEventHandlers();
    if(lastFocusState)
        padTextArea.focus();
    else
        padTextArea.blur();
    bindEventHandlers();
}

function resetSelection() {
    unbindEventHandlers();
    padTextArea.setSelection(lastPosition, lastPosition);
    bindEventHandlers();
}

function onInput(event) {
    var newTextContent = padTextArea.val();
    var message = computeEdition(previousTextContent, newTextContent);
    message.type = "edit";
    // It is possible to have empty edit, do not send message in that case
    if(message.insertion.length > 0 || message.deletion > 0) {
        socket.send(JSON.stringify(message));
        message.position = lastPosition;
        log("SEND", message);
        requestedEdits.push(message);
        lastPosition = padTextArea.getSelection().end;
        previousTextContent = padTextArea.val();
    }
}

function seek() {
    newPosition = padTextArea.getSelection().end;
    // This check avoids asking two times for the same cursor position
    if(!lastFocusState || newPosition != lastPosition) {
        lastPosition = newPosition;
        lastFocusState = true;
        var contextWidth = 10;
        var context = padTextArea.val().substring(lastPosition - contextWidth, lastPosition + contextWidth),
            context_position = Math.min(lastPosition, contextWidth);
        var message = {
            type: "seek",
            position: lastPosition,
            context: context,
            context_position: context_position
        }
        socket.send(JSON.stringify(message));
        log("SEND", message);
    }
}

function focusOut(event) {
    if(lastFocusState) {
        message = {
            type: "focus_out"
        }
        socket.send(JSON.stringify(message));
        log("SEND", message);
        lastFocusState = false;
    }
}

function arrowPressed(event) {
    var moveKeys = [
      40 /* down */, 39 /* right */, 38 /* up */,  37 /* left */,
      36 /* home */, 35 /* end */, 34 /* pageDown */, 33 /* pageUp */
    ]
    if(moveKeys.indexOf(event.which) > -1)
        seek();
}

function applyEdit(edit) {
    if(edit.deletion > 0)
        padTextArea.deleteText(edit.position - edit.deletion, edit.position);
    if(edit.insertion.length > 0)
        padTextArea.insertText(edit.insertion, edit.position);
}

function receiveMessage(message) {
    var data = JSON.parse(message.data)
    log("RECEIVE", data);

    switch(data.type) {
        case "sync":
            padTextArea.val(data.content);
            serverTextContent = data.content;
            previousTextContent = serverTextContent;
            lastPosition = 0;
            lastFocusState = false;
            resetSelection();
            resetFocus();
            break;

        case "seek":
            lastPosition = data.position;
            lastFocusState = true;
            resetSelection();
            break;

        case "edit":
            var oldestEdit = requestedEdits.shift();
            if(oldestEdit === undefined)
                oldestEdit = {};

            // If the oldest edit is different from the one we just received
            if(!editsAreEqual(data, oldestEdit)) {
                // Revert the oldest edit if it was not empty
                if(Object.keys(oldestEdit).length !== 0) {
                    // TODO in this case, we should handle the cursor in order to not focusing out
                    padTextArea.val(serverTextContent);
                    resetSelection();
                }
                // Apply the received server edit
                applyEdit(data);
                // Clear all requested edits
                requestedEdits = [];
            }
            serverTextContent = padTextArea.val();
            previousTextContent = serverTextContent;
            break;

        case "error":
            // Selection refused by server
            if(data.cause == "seek") {
                // Use the selection given by the server
                lastPosition = data.position;
                lastFocusState = true;
                resetSelection();
                resetFocus();
            }
            break;
    }
}

function bindEventHandlers() {
    padTextArea.on("textentered", onInput);
    padTextArea.on("focus", seek);
    padTextArea.on("click", seek);
    padTextArea.on("blur", focusOut);
    padTextArea.on("keydown", arrowPressed);
}

function unbindEventHandlers() {
    padTextArea.off("textentered", onInput);
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
