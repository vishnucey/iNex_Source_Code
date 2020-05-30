// Initialize your app
var myApp = new Framework7();
// import React from 'react';
// Export selectors engine
var $$ = Dom7;


// Add view
var mainView = myApp.addView('.view-main', {
    // Because we use fixed-through navbar we can enable dynamic navbar
    dynamicNavbar: true
});

var conversationStarted = false;
var person = {
        name: 'iNex',
        avatar: '/static/img/bots/inex.png'
    }

var answerTimeout, isFocused;


// Initialize Messages
var myMessages = myApp.messages('.messages');
var myMessagebar = myApp.messagebar('.messagebar');




// Focus the textarea by default
myMessagebar.textarea[0].focus();

// Send if Enter is pressed
$$('.messagebar textarea').on("keydown", function(e) {
    if (!e) { var e = window.event; }

    if (e.keyCode == 13) {
            e.preventDefault();
            sendMessage($$('.messagebar textarea')[0].value, 1);
            document.getElementById("msg").placeholder="Processing in progress..."
            setTimeout(function() {document.getElementById("msg").placeholder="Message"},5000);
            }
            console.log("key pressed");

}, false);

// Send if 'Send' button is pressed
$$('.messagebar a.send-message').on('click touchstart mousedown', function() {
    sendMessage($$('.messagebar textarea')[0].value, 1);
    console.log('touchdown..')
    document.getElementById("msg").placeholder="Processing in progress..."
    setTimeout(function() {document.getElementById("msg").placeholder="Message"},5000);

});





//Toggling Tooltip when speech functionality is enabled
$("#speech").attr('title', 'Speech : Off');         //Default behavior on load
$$('#speech').on('click', function() {              //Tied to the click even of the speech button
    if(!$('#mic').hasClass('disabled')){            //If not disabled then show Speech : On
        $("#speech").attr('title', 'Speech : On');
    }else{                                          //If Disabled show Speech : Off
        $("#speech").attr('title', 'Speech : Off');
    }
})

function generate_interface(interface) {

            // console.log(interface)

            // Start building a response

            build = ''

            // Show the message if there is any

            if(interface['message']){
                build +=  interface['message']
            }

            // Generate buttons if there are action items

            if((typeof interface['actions'] != "undefined") && (interface['actions'].length)){
                build += "<div class='list-block inset'><ul>"

                for (var i = 0; i < interface.actions.length; i++) {
                    console.log(interface.actions[i].trigger)
                    build += "<li><a href='#' class='item-link list-button' data-trigger='" + interface.actions[i].trigger + "'>" + interface.actions[i].text + "</a></li>"
                }

                build += "</ul></div>"
            }

            return build
        }

// Initialize interaction handler

clickBomb = function(e){
            $$('.messagebar textarea')[0].value = $$(this).attr('data-trigger')
            var m = $$(this).attr('data-trigger')
            sendMessage(m, 1);
            console.log('.clickbomb...')
            document.getElementById("msg").placeholder="Processing in progress..."
            setTimeout(function() {document.getElementById("msg").placeholder="Message"},5000);

        }

function sendMessage(messageText, isVisible) {
    if (messageText.length === 0) {
        return;
    }
    // Clear messagebar
    myMessagebar.clear();

if(typeof(isVisible) == "undefined") { isVisible = 0;}

if(isVisible){

    // Add Message
    myMessages.addMessage({
        text: messageText,
        type: 'sent',
        day: !conversationStarted ? 'Today' : false,
        time: !conversationStarted ? (new Date()).getHours() + ':' + (new Date()).getMinutes() : false
    });
}
    conversationStarted = true;

    // Add answer after timeout
    if (answerTimeout) clearTimeout(answerTimeout);
    answerTimeout = setTimeout(function () {

        // var person = people[Math.floor(Math.random() * people.length)];
        var data = { userInput: messageText }

        answerText = $$.post( "/converse", data, function(response) {

                        console.log( "Data received from server." );

                        response = JSON.parse(response);
                        console.log(document.getElementById("msg"));
                        document.getElementById("msg").placeholder="Message";
                        console.log(response)


                                       if(!$('#mic').hasClass('disabled')){                //If microphone button is not disabled then perform TTS
                        ttsInput = response.speechOutput
                        console.log("input")
                        console.log(ttsInput)
                         //object to embed the blob and play
                        const audio = document.getElementById('audio')
                        var ttsRequest = {'text': ttsInput}
                        // XMLHttpRequest object to request data from a server

                        var xhr = new XMLHttpRequest();
                        xhr.open("post", "/text-to-speech", true);
                        xhr.setRequestHeader('Content-Type', 'application/json');
                        xhr.responseType = 'blob';
                        xhr.onload = function () {
//                        console.log("success");
                        console.log(this.response);
                        console.log(xhr.status);
                          if (xhr.status >= 200 && xhr.status < 400) {
                        console.log('success');
                        var blob = new Blob([this.response], {type: 'audio/wav'});

                        const url = window.URL.createObjectURL(blob);
                        console.log(url)
                        console.log("bla")
                        //this.setState({ loading: false, hasAudio: true });
                        audio.setAttribute('src', url);
                        audio.setAttribute('type', 'audio/wav');
                        audio.onload = function(evt) {
                                window.URL.revokeObjectURL(url);
                              };
                        audio.load();
                        audio.play();
                        console.log("end")


                          } else {
                            console.log('error');

                          }
                        }
                          xhr.send(JSON.stringify(ttsRequest));
                        };


                        myMessages.addMessage({
                            text: generate_interface(response),//['botMessage'],
                            type: 'received',
                            name: person.name,
                            avatar: person.avatar
                        });

                        // Scroll to the very bottom
                        myMessages.scrollMessages();

                        // Set button actions
                        $$('a.item-link.list-button').on('click', clickBomb)
                      })

    }, 2000);


}

// Restart button handler

$$('.restart-chat').on('click', function (e) {
        myMessages.clean()
        sendMessage('Reset', 0)
    });

// Bind actions to pre-populated messages (conversation starters)
$$('a.item-link.list-button').on('click', clickBomb)