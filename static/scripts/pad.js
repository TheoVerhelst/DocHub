var socket = null;

function receiveMessage(message)
{
}

function sendMessage(clickEvent)
{
}

function initPad()
{
    makePreview({})
}

function makePreview(event)
{
    var markdown_text = $("#id_text").val()
    $("#preview-text").html(markdown.Markdown.toHTML(markdown_text))
}

$(document).ready(initPad);

$("#preview-tab-link").click(makePreview);
