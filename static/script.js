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