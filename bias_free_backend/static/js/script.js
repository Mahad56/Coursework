document.addEventListener('DOMContentLoaded', function () {
    // Register the post button click event
    const postButton = document.getElementById('post-button');
    if (postButton) {
        postButton.addEventListener('click', addPost);
    }

    // Hamburger menu toggle
    const hamburger = document.querySelector('.sidebar-menu');
    if (hamburger) {
        hamburger.addEventListener('click', toggleMenu);
    }

    // Dark mode toggle
    const darkModeToggle = document.querySelector('.dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
    }

    // Navigation page switching
    const navLinks = document.querySelectorAll('nav ul li a');
    navLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            const targetPage = event.target.getAttribute('onclick').replace("showPage('", "").replace("')", "");
            showPage(targetPage);
        });
    });

    // Event delegation for dynamically added posts
    const postsContainer = document.getElementById('posts-container');
    if (postsContainer) {
        postsContainer.addEventListener('click', function (event) {
            // Check if the clicked element is a comment button
            if (event.target && event.target.classList.contains('comment-btn')) {
                commentPost(event.target);
            }
        });
    }
});
// Function to handle "Post" creation
function addPost() {
    const postInput = document.getElementById('post-input');
    const postsContainer = document.getElementById('posts-container');

    if (!postInput || !postsContainer) {
        console.error('Required elements not found in the DOM.');
        return;
    }

    // Get the user's input
    const postContent = postInput.value.trim();

    // Get the username (you could also get this from a hidden input, data attribute, or other means)
    const username = currentUser; // Replace this with dynamic logic to fetch the username

    // Check if the input is not empty
    if (postContent) {
        // Generate a unique post ID (this could also come from the backend if necessary)
        const postId = Math.floor(Math.random() * 1000); // Replace with real post ID after creating post

        // Create a new post element
        const post = document.createElement('div');
        post.classList.add('post');
        post.innerHTML = `
            <div class="post-box">
            
                <div class="post-header">
                    <span class="username">${username}</span>  <!-- Display username -->
                    <span class="post-id">#${postId}</span>  <!-- Display post ID -->
                </div>
                <p>${postContent}</p>
                <div class="post-actions">
                    <button class="like-btn" onclick="likePost(this)">👍 Like (<span>0</span>)</button>
                    <button class="dislike-btn" onclick="dislikePost(this)">👎 Dislike (<span>0</span>)</button>
                    <button class="comment-btn">💬 Comment</button>
                </div>
            </div>
        `;
        // Add the new post to the top of the container
        postsContainer.insertBefore(post, postsContainer.firstChild);

        // Clear the input field
        postInput.value = '';
    } else {
        alert('Please enter some content to post.');
    }
}
// Function to handle "Like" button click
function likePost(button) {
    const postActions = button.closest('.post-actions');

    // Check if the user has already interacted with this post
    if (postActions.dataset.interacted === "true") {
        alert("You can only like or dislike this post once!");
        return;
    }

    // Mark as interacted
    postActions.dataset.interacted = "true";

    const likeCountElement = button.querySelector('span');
    let likeCount = parseInt(likeCountElement.textContent);
    likeCountElement.textContent = likeCount + 1;
}

// Function to handle "Dislike" button click
function dislikePost(button) {
    const postActions = button.closest('.post-actions');

    // Check if the user has already interacted with this post
    if (postActions.dataset.interacted === "true") {
        alert("You can only like or dislike this post once!");
        return;
    }

    // Mark as interacted
    postActions.dataset.interacted = "true";

    const dislikeCountElement = button.querySelector('span');
    let dislikeCount = parseInt(dislikeCountElement.textContent);
    dislikeCountElement.textContent = dislikeCount + 1;
}


// Function to handle "Comment" button click
function commentPost(button) {
    const postBox = button.closest('.post-box');
    let commentSection = postBox.querySelector('.comment-section');
    
    // Check if the comment section already exists
    if (!commentSection) {
        // Create a new comment section
        commentSection = document.createElement('div');
        commentSection.classList.add('comment-section');
        commentSection.style.display = 'none';  // Hide the comment section initially
        postBox.appendChild(commentSection);

        // Create "See Comments" button
        const seeCommentsButton = document.createElement('button');
        seeCommentsButton.textContent = "See Comments";
        seeCommentsButton.classList.add('see-comments-btn');
        seeCommentsButton.addEventListener('click', function () {
            // Toggle the visibility of the comment section
            commentSection.style.display = commentSection.style.display === 'none' ? 'block' : 'none';
        });

        // Append the "See Comments" button to the post box
        postBox.appendChild(seeCommentsButton);
    }

    // Prompt user for a new comment
    const commentText = prompt("Enter your comment:");
    if (commentText) {
        // Generate a unique comment ID (this can be changed to use a more sophisticated method)
        const commentId = Math.floor(Math.random() * 1000);

        // Get the username (using the currentUser variable passed from Django)
        const username = currentUser;

        // Create a new comment element
        const commentElement = document.createElement('div');
        commentElement.classList.add('comment');
        commentElement.innerHTML = `
            <div class="comment-header">
                <span class="comment-username">${username}</span>  <!-- Display username -->
                <span class="comment-id">#${commentId}</span>  <!-- Display comment ID -->
            </div>
            <p>${commentText}</p>
        `;

        // Append the new comment to the comment section
        commentSection.appendChild(commentElement);
    }
}

// Toggle the sidebar menu
function toggleMenu() {
    const sidebar = document.getElementById('sidebar-menu');
    sidebar.classList.toggle('active');
}
// Toggle dark mode
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
}
// Function to display the correct page
function showPage(pageId) {
    // Hide all pages
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.remove('active'));

    // Show the selected page
    const activePage = document.getElementById(pageId);
    if (activePage) {
        activePage.classList.add('active');
    }
}
