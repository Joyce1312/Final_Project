function init() {
    console.log("Product page has loaded!");
    let op = document.getElementById("output");
    build = '';
    for(let i = 0; i < 10; i++){
        for(let j = 0; j < 3; j++){
            build += `<div class="card" id="card${j}_${i}">`;
            build +=    `<p>img</p>`;
            build +=    `<h3>Name</h3>`;
            build +=    `<p>price</p>`;
            build +=    `<button type="submit">Add to Cart</button>`;
            build += `</div>`;
            
        }
    }
    op.innerHTML = build;

}

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