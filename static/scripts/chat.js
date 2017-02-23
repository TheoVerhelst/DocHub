var socket = null;

function receiveMessage(message)
{
    // The message text is a json string containing data
    var data = JSON.parse(message.data)
    $("#chat-text").append("<li>"
        + "<span class='radius secondary label'>" + data['user'] + "</span> "
        + data['text'] + " "
        + "<small class='right'>" + data['created'] + "</small>"
        + "</li>");
}

function sendMessage(clickEvent)
{
    socket.send($("#chat-input").val());
    $("#chat-input").val('');
}

function initChat()
{
    socket = new WebSocket("ws://" + window.location.host + "/chat/" + $("#chat-group").val() + "/");

    socket.onmessage = receiveMessage;

    // Call onopen directly if socket is already open
    if(socket.readyState == WebSocket.OPEN)
        socket.onopen();
}

$(document).ready(initChat);

$("#chat-button").click(sendMessage);
$("#chat-input").keypress(function(e)
{
  if (e.which == 13)
      sendMessage(e);
});
