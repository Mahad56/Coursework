function showPage(pageId) {
    let pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.remove('active'));

    document.getElementById(pageId).classList.add('active');
}

function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");
}

// Function to toggle the sidebar menu
function toggleMenu() {
    let menu = document.getElementById('sidebar-menu');
    menu.classList.toggle('active');
    console.log("Menu toggled"); // Debugging
}

// Function to Like a post
function likePost(btn) {
    let countSpan = btn.querySelector("span");
    let count = parseInt(countSpan.innerText);
    count++;
    countSpan.innerText = count;
}

// Function to Dislike a post
function dislikePost(btn) {
    let countSpan = btn.querySelector("span");
    let count = parseInt(countSpan.innerText);
    count++;
    countSpan.innerText = count;
}

// Function to add a comment
function addComment() {
    let input = document.getElementById("comment-input");
    let commentText = input.value.trim();
    
    if (commentText !== "") {
        let commentsDiv = document.querySelector(".comments");
        let newComment = document.createElement("p");
        newComment.textContent = commentText;
        commentsDiv.appendChild(newComment);
        input.value = "";
    }
}
