// Initial Page Loading

// Variables to store user and token in memory
let currentUser = null;
let authToken = null;
let conversationId = null;

// Initially, show only the login section
document.addEventListener('DOMContentLoaded', function () {
    showSection('login');  // Show login by default

    // Handle login form submission
    document.getElementById('login-form').addEventListener('submit', async function (event) {
        event.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        // Call the login function
        const token = await getAuth(username, password);

        if (token) {
            // Store the user and token in memory
            currentUser = username;
            authToken = token;

            // Fetch chat history and show the chat section
            updateChatHistoryBar();
        } else {
            alert("Login failed. Please try again.");
        }
    });

    // Handle sign-up form submission
    document.getElementById('signup-form').addEventListener('submit', async function (event) {
        event.preventDefault();
        const username = document.getElementById('signup-username').value;
        const password = document.getElementById('signup-password').value;

        // Call the registration function
        const token = await register(username, password);

        if (token) {
            // Store the user and token in memory
            currentUser = username;
            authToken = token;

            // Fetch chat history and show the chat section
            const chatHistory = await getChatHistory(currentUser, authToken);
            updateChatHistoryBar();
        } else {
            alert("Sign-Up failed. Please try again.");
        }
    });

    // Switch to sign-up section and clear inputs
    document.getElementById('show-signup-btn').addEventListener('click', function () {
        clearInputs(); // Clear all form inputs
        showSection('signup');  // Switch to Sign-Up form
    });

    // Switch to login section and clear inputs
    document.getElementById('show-login-btn').addEventListener('click', function () {
        clearInputs(); // Clear all form inputs
        showSection('login');  // Switch to Login form
    });
});

// Function to show specific section (login, signup, or chat)
function showSection(section) {
    const loginSection = document.getElementById('login-section');
    const signupSection = document.getElementById('signup-section');
    const chatSection = document.getElementById('chat-section');

    if (section === 'login') {
        loginSection.style.display = 'flex';  // Show login
        signupSection.style.display = 'none'; // Hide sign-up
        chatSection.style.display = 'none';   // Hide chat section
    } else if (section === 'signup') {
        signupSection.style.display = 'flex';  // Show sign-up
        loginSection.style.display = 'none';   // Hide login
        chatSection.style.display = 'none';    // Hide chat section
    } else if (section === 'chat') {
        chatSection.style.display = 'block';   // Show chat section
        loginSection.style.display = 'none';   // Hide login
        signupSection.style.display = 'none';  // Hide sign-up
    }
}

// Function to clear all input fields when switching between forms
function clearInputs() {
    document.querySelectorAll('input').forEach(input => input.value = '');
}

// Function to handle login (uses your existing getAuth function)
async function getAuth(user, password) {
    let endpoint = `/get-auth?user=${encodeURIComponent(user)}&password=${encodeURIComponent(password)}`;
    try {
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        return data.token;
    } catch (error) {
        console.error('Error fetching auth token:', error);
        return null;
    }
}

// Function to handle sign-up (similar to getAuth)
async function register(user, password) {
    let endpoint = `/register?user=${encodeURIComponent(user)}&password=${encodeURIComponent(password)}`;
    try {
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        return data.token;
    } catch (error) {
        console.error('Error registering user:', error);
        return null;
    }
}

// Function to render the chat list inside the scrollable div
function renderList(data) {
    const listContainer = document.getElementById('chat-history');
    listContainer.innerHTML = '';  // Clear any existing chat history

    // Iterate over the data and create list items
    // Most recent first
    data.reverse();
    data.forEach(([id, title, time]) => {
        const listItem = document.createElement('div');
        listItem.className = 'list-item';
        
        // Create a span for the title of the conversation
        const titleSpan = document.createElement('span');
        titleSpan.textContent = title;

        // Add a click event listener for the list item (excluding the delete button)
        listItem.addEventListener('click', () => handleItemClick(id, title, time));

        // Create a delete button
        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'X'; // Label the button with an "X"
        deleteButton.className = 'list-item-delete'; // Optional: add a class for styling

        // Add a click event listener for the delete button
        deleteButton.addEventListener('click', (event) => {
            event.stopPropagation(); // Prevent triggering the list item click event
            handleDeleteClick(id); // Call the delete function
        });

        // Append the title and delete button to the list item
        listItem.appendChild(titleSpan);
        listItem.appendChild(deleteButton);

        // Append the list item to the scrollable div
        listContainer.appendChild(listItem);
    });
}

async function updateChatHistoryBar(){
    const chatHistory = await getChatHistory(currentUser, authToken);
    if (chatHistory) {
        renderList(chatHistory);  // Populate chat history
        showSection('chat');      // Switch to chat section
    } else {
        renderList([]);
        showSection('chat');
    }

}

async function handleDeleteClick(id) {
    await deleteConversation(id);

    if (id == conversationId){
        conversationId = null;
        document.getElementById("messages").innerHTML = "";
    }
    await updateChatHistoryBar();
}

// Function to handle clicking on a list item
function handleItemClick(id, title, time) {
    displayConversation(id);
}

async function deleteConversation(conversationIdToDelete) {
    // Construct the delete URL, passing user, token, and conversation_id as query parameters
    let endpoint = `/delete-conversation?user=${encodeURIComponent(currentUser)}&token=${encodeURIComponent(authToken)}&conversation_id=${encodeURIComponent(conversationIdToDelete)}`;
    
    try {
        // Send a DELETE request to the server
        const response = await fetch(endpoint, { method: 'DELETE' });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        return data.message;  // Returning success message or other relevant data

    } catch (error) {
        console.error('Error deleting conversation:', error);
        return null;
    }
}


// Function to get chat history
async function getChatHistory(user, token) {
    let endpoint = `/get-chat-history?user=${encodeURIComponent(user)}&token=${encodeURIComponent(token)}`;
    try {
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        return data.chat_history;  // Assuming chat_history is returned in the response
    } catch (error) {
        console.error('Error fetching chat history:', error);
        return null;
    }
}


// Show modal when the user button is clicked
document.getElementById('user-btn').addEventListener('click', function() {
    const modal = document.getElementById('popup-modal');
    modal.style.display = 'flex'; // Show the popup
});

// Close modal when the close button is clicked
document.getElementById('close-modal').addEventListener('click', function() {
    const modal = document.getElementById('popup-modal');
    modal.style.display = 'none'; // Hide the popup
});

// Close the modal when clicking outside the modal content
window.addEventListener('click', function(event) {
    const modal = document.getElementById('popup-modal');
    if (event.target === modal) {
        modal.style.display = 'none'; // Hide the modal if clicking outside of it
    }
});


// Load conversation
async function loadConversation(newConversationId){
     // Construct the stream URL based on whether the conversationId exists
     let endpoint = `/get-conversation?user=${encodeURIComponent(currentUser)}&token=${encodeURIComponent(authToken)}&conversation_id=${encodeURIComponent(newConversationId)}`;
     try {
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        if (data.conversation_id == newConversationId){
            conversationId = newConversationId;
            return data.conversation

        }
    } catch (error) {
        console.error('Error fetching chat history:', error);
        return null;
    }
}

async function displayConversation(newConversationId){
    // Load converstion
    conversation = await loadConversation(newConversationId)

    if (conversation){
        // Clean actual converation
        document.getElementById("messages").innerHTML = "";
        for (const message of conversation){
            if (message.role == "user"){
                addOutgoingMessage(message.content)
            }
            else if (message.role == "assistant"){
                let incomingMessage;
                addIncomingMessage(message.content,incomingMessage,"")
            }
        }
    }
    else{
        alert("NO conversation Found")
    }
    
}





/**
 * Preprocess the server response for safe HTML display and format code snippets.
 * @param {string} rsp - The response from the server.
 * @returns {string} Safe and formatted HTML string.
 */
function cleanOutput(rsp) {
    // Convert angle brackets to prevent HTML injection
    rsp = rsp.replace(/</g, "&lt;").replace(/>/g, "&gt;");

    // Handle code snippets by wrapping them in <pre> tags for proper formatting
    rsp = rsp.replace(/```[^\s]+/g, "<pre>"); // Start code block
    rsp = rsp.replace(/```/g, "</pre>"); // End code block
    
    // Convert markdown to HTML
    var converter = new showdown.Converter();
    var safeHtml = converter.makeHtml(rsp);
    return safeHtml;
}

/**
 * Sends a text message to the server and handles the streaming response.
 */
function sendMessage() {
    var input = document.getElementById("chat-input");
    var text = input.value.trim();
    if (text === "") return;

    addOutgoingMessage(text); // Add the outgoing message to the UI
    input.value = ""; // Clear the input field

    // Construct the stream URL based on whether the conversationId exists
    let streamUrl;
    if (conversationId == null) {
        streamUrl = `/stream-send?user=${encodeURIComponent(currentUser)}&token=${encodeURIComponent(authToken)}&message=${encodeURIComponent(text)}`;
    } else {
        streamUrl = `/stream-send?user=${encodeURIComponent(currentUser)}&token=${encodeURIComponent(authToken)}&message=${encodeURIComponent(text)}&conversation_id=${encodeURIComponent(conversationId)}`;
    }

    // Initialize EventSource with the stream URL
    var eventSource = new EventSource(streamUrl);

    let incomingMessage;
    var incomingText = "";

    // Handle the conversation ID event (for new conversations)
    eventSource.addEventListener("conversation_id", function(event) {
        if (conversationId == null || conversationId == ""){
            updateChatHistoryBar();
            conversationId = event.data; 
        }
        
    });

    // Handle chat events (streamed message chunks)
    eventSource.addEventListener("chat", function(event) {
        var data = JSON.parse(event.data);
        if (data.endOfMessage) {
            eventSource.close(); // Close the stream when the message ends
        } else {
            // Process and display the incoming message chunks
            [incomingMessage, incomingText] = addIncomingMessage(data.response, incomingMessage, incomingText);
        }
    });

    // Handle errors in the EventSource
    eventSource.onerror = function() {
        eventSource.close(); // Close the stream on error
        console.error('EventSource failed.');
    };
}


/**
 * Sends an audio message to the server and handles the streaming response.
 * @param {string} text - Transcribed audio text to send.
 */
function sendMessage_audio(text) {
    // Check if the input text is valid
    if (text === "") return;

    // Add the outgoing message to the chat UI
    addOutgoingMessage(text);

    // Construct the stream URL based on whether the conversationId exists
    let streamUrl;
    if (conversationId == null) {
        streamUrl = `/stream-send?user=${encodeURIComponent(currentUser)}&token=${encodeURIComponent(authToken)}&message=${encodeURIComponent(text)}`;
    } else {
        streamUrl = `/stream-send?user=${encodeURIComponent(currentUser)}&token=${encodeURIComponent(authToken)}&message=${encodeURIComponent(text)}&conversation_id=${encodeURIComponent(conversationId)}`;
    }

    // Initialize EventSource with the stream URL
    var eventSource = new EventSource(streamUrl);

    let incomingMessage;
    var incomingText = "";

    // Handle the conversation ID event (for new conversations)
    eventSource.addEventListener("conversation_id", function(event) {
        if (conversationId == null || conversationId == ""){
            updateChatHistoryBar();
            conversationId = event.data; 
        }
    });

    // Handle chat events (streamed message chunks)
    eventSource.addEventListener("chat", function(event) {
        var data = JSON.parse(event.data);
        if (data.endOfMessage) {
            eventSource.close(); // Close the stream when the message ends

            // After the stream ends, convert the text to speech
            const synth = window.speechSynthesis;
            const utterance = new SpeechSynthesisUtterance(incomingMessage.innerText); // Speak the entire message
            utterance.voice = synth.getVoices().find(voice => voice.lang.startsWith('en'));
            utterance.onend = function(event) {
                // Re-enable the startRecord button once the speech has finished
                document.getElementById("startRecord").disabled = false;
            }
            synth.speak(utterance);

        } else {
            // Process and display the incoming message chunks
            [incomingMessage, incomingText] = addIncomingMessage(data.response, incomingMessage, incomingText);
        }
    });

    // Handle errors in the EventSource
    eventSource.onerror = function() {
        eventSource.close(); // Close the stream on error
        console.error('EventSource failed.');
    };
}


/**
 * Adds a user's message to the chat interface.
 * @param {string} promptText - Text to be added as an outgoing message.
 */
function addOutgoingMessage(promptText){
    var messages = document.getElementById("messages");

    var outgoingMessage = document.createElement("div");
    outgoingMessage.classList.add("message", "outgoing");

    // Avantar and Label container
    var labelContainer = document.createElement("div");
    labelContainer.classList.add("labelContainer");

    // Label
    var userLabel = document.createElement("span");
    userLabel.classList.add("label");
    userLabel.textContent = "User";
    labelContainer.appendChild(userLabel);

    // Add avatar image for assistant
    var avatarImg = document.createElement("img");
    avatarImg.src = "images/user.webp"; // The path to your avatar image
    avatarImg.alt = "Assistant";
    avatarImg.classList.add("avatar");
    labelContainer.appendChild(avatarImg);

    outgoingMessage.appendChild(labelContainer);
    outgoingMessage.append(document.createTextNode(promptText));
    messages.appendChild(outgoingMessage);
    messages.scrollTop = messages.scrollHeight;
}


/**
 * Adds the server's response to the chat interface.
 * @param {string} responseText - Server's response text.
 * @param {Element} incomingMessage - HTML element containing the incoming message.
 * @param {string} incomingText - Accumulated response text.
 * @returns {[Element, string]} Updated HTML element and text.
 */
function addIncomingMessage(responseText,incomingMessage,incomingText) {
    var messages = document.getElementById("messages");
    incomingText+=responseText

    if (!incomingMessage) {
        incomingMessage = document.createElement("div");
        incomingMessage.classList.add("message", "incoming");

        // Avantar and Label container
        var labelContainer = document.createElement("div");
        labelContainer.classList.add("labelContainer");

        // Add avatar image for assistant
        var avatarImg = document.createElement("img");
        avatarImg.src = "images/assistant.webp"; // The path to your avatar image
        avatarImg.alt = "Assistant";
        avatarImg.classList.add("avatar");
        labelContainer.appendChild(avatarImg);

        // Add assistant label
        var assistantLabel = document.createElement("span");
        assistantLabel.classList.add("label");
        assistantLabel.textContent = "Assistant";
        labelContainer.appendChild(assistantLabel);

        incomingMessage.appendChild(labelContainer);

        // Create a new div to wrap the response text
        var responseContent = document.createElement("div");
        responseContent.classList.add("response-content");
        responseContent.innerHTML = cleanOutput(incomingText);
        incomingMessage.appendChild(responseContent);
        messages.appendChild(incomingMessage);

    } else {
        var responseContent = incomingMessage.querySelector(".response-content");
        responseContent.innerHTML = cleanOutput(incomingText);
    }

    messages.scrollTop = messages.scrollHeight;
    return [incomingMessage,incomingText];
}

/**
 * Initializes the recording process to capture user audio.
 */
function startRecording() {
    document.getElementById("startRecord").style.display = "none";
    document.getElementById("startRecord").disabled = true;
    document.getElementById("stopRecord").style.display = "inline-block";

    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            const options = { mimeType: 'audio/wav' };
            if (MediaRecorder.isTypeSupported(options.mimeType)) {
                mediaRecorder = new MediaRecorder(stream, options);
            } else {
                console.log('WAV format not supported, falling back to default MIME type.');
                mediaRecorder = new MediaRecorder(stream);
            }
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            mediaRecorder.start();
            document.getElementById("stopRecord").disabled = false;
            audioChunks = [];
        });
}

/**
 * Stops the recording process and sends the captured audio to the server.
 */
function stopRecording() {
    document.getElementById("startRecord").style.display = "inline-block";
    document.getElementById("stopRecord").style.display = "none";

    mediaRecorder.stop();
    document.getElementById("stopRecord").disabled = true;
    
    mediaRecorder.onstop = () => {
        const mimeType = mediaRecorder.mimeType;
        const audioBlob = new Blob(audioChunks, { type: mimeType });
        const formData = new FormData();

        // Append audio file
        formData.append("audioFile", audioBlob);
        
        // Append user and token (assuming these variables are available globally or passed in)
        formData.append("user", currentUser);  // Replace with actual user variable
        formData.append("token", authToken);   // Replace with actual token variable

        fetch('/upload-audio', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            // Handle successful transcription
            if (data.transcription) {
                sendMessage_audio(data.transcription); 
            } else if (data.error) {
                console.error('Server Error:', data.error);
                alert('Error processing audio. Please try again.');
            }
            
        })
        .catch(error => {
            console.error("Error:", error);
            alert('Error uploading audio. Please try again.');
            document.getElementById("startRecord").disabled = false;
        });
    };
}
 

// Function to handle keyboard events
function handleKeyDown(event) {
    // Check if the key pressed is the space key
    if (event.key === ' ' || event.code === 'Space') {
        // Stop the reading action
        stopReading();
        document.getElementById("startRecord").disabled = false;
    }
}

// Function to stop reading the content
function stopReading() {
    // Stop any ongoing speech synthesis
    window.speechSynthesis.cancel();
}


// Add an event listener for the Enter key
document.getElementById("chat-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault(); // Prevent the default action to stop form submission
        sendMessage();
    }
});

function newConversation(){
    conversationId = null;
    document.getElementById("messages").innerHTML = "";
}


async function logoutUser() {
    const endpoint = `/logout?user=${encodeURIComponent(currentUser)}&token=${encodeURIComponent(authToken)}`;

    try {
        const response = await fetch(endpoint, { method: 'DELETE' });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        alert(data.message);  // Alert the user about the logout success

        // Reload the page after logout to reset the state
        location.reload();
    } catch (error) {
        console.error('Error logging out:', error);
        alert('Failed to logout. Please try again.');
    }
}


async function deleteUser() {
    const password = prompt('Please enter your password to delete your account:'); // Ask for password
    if (!password) {
        alert('Password is required to delete your account.');
        return;
    }

    const endpoint = `/delete-user?user=${encodeURIComponent(currentUser)}&token=${encodeURIComponent(authToken)}&password=${encodeURIComponent(password)}`;

    try {
        const response = await fetch(endpoint, { method: 'DELETE' });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        alert(data.message);  // Alert the user about the successful deletion

        // Reload the page or redirect to a different page after account deletion
        location.reload();
    } catch (error) {
        console.error('Error deleting user:', error);
        alert('Failed to delete user. Please try again.');
    }
}

// Recoding Widgets
document.getElementById("startRecord").style.display = "inline-block";
document.getElementById("stopRecord").style.display = "none";
document.getElementById("startRecord").onclick = startRecording;
document.getElementById("stopRecord").onclick = stopRecording;
document.getElementById("new-conversation-button").onclick = newConversation;
document.getElementById("send-button").onclick = sendMessage;
document.getElementById("logout-btn").onclick = logoutUser;
document.getElementById("delete-btn").onclick = deleteUser;
document.addEventListener("keydown", handleKeyDown);


let mediaRecorder;
let audioChunks = [];







 





