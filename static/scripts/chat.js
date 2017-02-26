var socket = null;

function scrollDown(identifier)
{
  $(identifier).animate({ scrollTop: $(identifier).prop("scrollHeight")}, 1000);
}

function receiveMessage(message)
{
    // The message text is a json string containing data
    var data = JSON.parse(message.data);
    $("#chat-text").append("<li>"
        + "<span class='radius secondary label'>" + data['user'] + "</span> "
        + data['text'] + " "
        + "<small class='right'>" + data['created'] + "</small>"
        + "</li>");
    scrollDown("#chat-text");
}

function sendMessage(clickEvent)
{
    var message = $("#chat-input").val();
    if(!(message === ""))
    {
        socket.send(message);
        $("#chat-input").val('');
    }
}

function initChat()
{
    socket = new WebSocket("ws://" + window.location.host + "/chat/" + $("#chat-group").val() + "/");

    socket.onmessage = receiveMessage;

    // Call onopen directly if socket is already open
    if(socket.readyState == WebSocket.OPEN)
        socket.onopen();
    scrollDown("#chat-text");
}

$(document).ready(initChat);

$("#chat-button").click(sendMessage);
$("#chat-input").keypress(function(e)
{
  if (e.which == 13)
      sendMessage(e);
});
