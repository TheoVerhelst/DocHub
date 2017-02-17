socket = null;

// We need this boolean to indicate wether initChat has already been called
// Because it is called every time the tab is clicked
chatInitialized = false;

function receiveMessage(message)
{
    $("#chat-text").append("<li><span class='radius secondary label'>User</span> " + message.data + "</li>");
}

function initChat()
{
    if(!chatInitialized)
    {
        socket = new WebSocket("ws://" + window.location.host + "/chat/");

        socket.onmessage = receiveMessage;

        // Call onopen directly if socket is already open
        if(socket.readyState == WebSocket.OPEN)
            socket.onopen();

        chatInitialized = true;
    }
}

function sendMessage(clickEvent)
{
    if(chatInitialized)
    {
        socket.send($("#chat-input").val());
        $("#chat-input").val('');
    }
}

// This function will be called when the chat tab is clicked
$("#chat").click(initChat);

$("#chat-button").click(sendMessage);
