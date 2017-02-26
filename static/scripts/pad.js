(function() {

// Function to get the cursor position in an input element
(function ($, undefined) {
    $.fn.getCursorPosition = function() {
        var element = $(this).get(0);
        var position = 0;
        if('selectionStart' in element) {
            position = element.selectionStart;
        } else if('selection' in document) {
            element.focus();
            var Selection = document.selection.createRange();
            var SelectionLength = document.selection.createRange().text.length;
            Selection.moveStart('character', -element.value.length);
            pos = Selection.text.length - SelectionLength;
        }
        return position;
    }
})(jQuery);

var dmp = new diff_match_patch();

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

function makePreview(event) {
    var markdown_text = $("#id_text").val()
    $("#preview-text").html(markdown.Markdown.toHTML(markdown_text));
}

var socket = null;

var previousTextContent = $("#id_text").val()

function onInput(event) {
    var newTextContent = $("#id_text").val()
    var edition = computeEdition(previousTextContent, newTextContent);
    console.log(edition);
    previousTextContent = newTextContent;
    //socket.send(JSON.stringify(edition));
}

function receiveMessage(message) {
}

function initPad() {
    socket = new WebSocket("ws://" + window.location.host + "/pad/" + $("#document-pk").val() + "/");

    socket.onmessage = receiveMessage;

    // Call onopen directly if socket is already open
    if(socket.readyState == WebSocket.OPEN)
        socket.onopen();

    makePreview({});
    $("#preview-tab-link").click(makePreview);

    $("#id_text").on('input', onInput);

}

$(document).ready(initPad);
})();
