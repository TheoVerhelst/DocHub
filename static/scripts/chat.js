var socket = null;

function scrollDown(identifier) {
  $(identifier).animate({
      scrollTop: $(identifier)[0].scrollHeight - $(identifier)[0].clientHeight
  }, 300);
}

function receiveMessage(message) {
    // The message text is a json string containing data
    var data = JSON.parse(message.data);
    $("#chat-text").append("<li>"
        + "<span class='radius secondary label'>" + data['user'] + "</span> "
        + data['text'] + " "
        + "<small class='right'>" + data['created'] + "</small>"
        + "</li>");
    scrollDown("#chat-text");
}

function sendMessage(clickEvent) {
    var message = $("#chat-input").val();
    if(!(message === ""))
    {
        socket.send(message);
        $("#chat-input").val('');
    }
}

function initChat() {
    socket = new WebSocket("ws://" + window.location.host + "/chat/" + $("#chat-group").val() + "/");

    socket.onmessage = receiveMessage;

    // Call onopen directly if socket is already open
    if(socket.readyState == WebSocket.OPEN)
        socket.onopen();

    scrollDown("#chat-text");

    $("#chat-button").click(sendMessage);

    // Send a message when enter key is pressed in the chat input
    $("#chat-input").keypress(function(e) {
      var enterKeyCode = 13
      if (e.which == enterKeyCode)
          sendMessage(e);
    });

}

$(document).ready(initChat);
