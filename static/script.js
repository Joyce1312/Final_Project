setTimeout(function() {
    let flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(function(message) {
        message.style.transition = 'opacity 1s ease-out'; // Optional: Add a fade-out effect
        message.style.opacity = 0; // Fade it out

        // Remove the element after the transition
        setTimeout(function() {
            message.remove(); // This will remove the message from the DOM
        }, 1000); // Ensure it happens after the opacity transition (1 second)
    });
}, 5000);  // Hide and remove flash messages after 5 seconds

function collapse(event){
    let button = event.target;
    let sidebar = document.getElementById('sidebar');
    // Toggle the 'collapsed' class on the sidebar
    sidebar.classList.toggle('collapsed');
}
