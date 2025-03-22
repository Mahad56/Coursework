document.addEventListener('DOMContentLoaded', function () {
        
    // Get the "Post" button and add a click event listener to it
    const postButton = document.getElementById('post-button');
    if (postButton) {
        postButton.addEventListener('click', addPost);
    }
    // Get the hamburger menu and add a click event listener to toggle the menu
    const hamburger = document.querySelector('.sidebar-menu');
    if (hamburger) {
        hamburger.addEventListener('click', toggleMenu);
    }
    // Get the dark mode toggle button and add a click event listener to enable/disable dark mode
    const darkModeToggle = document.querySelector('.dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
    }

    const navLinks = document.querySelectorAll('nav ul li a');
    navLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            const targetPage = event.target.getAttribute('onclick').replace("showPage('", "").replace("')", "");
            showPage(targetPage);
        });
    });
    

    const postsContainer = document.getElementById('posts-container');
    if (postsContainer) {
        postsContainer.addEventListener('click', function (event) {
            if (event.target.classList.contains('like-btn')) {
                likePost(event.target);
            } else if (event.target.classList.contains('dislike-btn')) {
                dislikePost(event.target);
            } else if (event.target.classList.contains('comment-btn')) {
                commentPost(event.target);
            }
        });
    }

    renderSentimentBar();

    // Load general posts
    loadPosts();

    // Load opposing views posts
    loadOpposingViewsPosts(); // Ensures the posts are added to the specific container
});
function getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('csrftoken=')) {
            return cookie.substring('csrftoken='.length, cookie.length);
        }
    }
    return '';
}
function toggleMenu() {
    const body = document.body;
    const sidebar = document.getElementById('sidebar-menu');
    
    // show/hide the sidebar and shift dashboard content to avoid overlap
    body.classList.toggle('sidebar-active');
    sidebar.classList.toggle('active');
}
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
}
async function addPost(event) {
    event.preventDefault();
    const postInput = document.getElementById('post-input');
    const postsContainer = document.getElementById('posts-container');

    if (!postInput || !postsContainer) {
        console.error('Required elements not found in the DOM.');
        return;
    }

    const postContent = postInput.value.trim();
    if (!postContent) {
        alert('Please enter some content to post.');
        return;
    }

    try {
        const response = await fetch('/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ content: postContent }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Error:', errorData.error);
            alert('Error: ' + errorData.error);
            return;
        }

        const data = await response.json();
        addPostToDOM(data);
        postInput.value = '';
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again later.');
    }
}
async function loadPosts() {
    try {
        const response = await fetch('/posts/get-posts/');
        if (!response.ok) {
            throw new Error('Failed to fetch posts');
        }

        const posts = await response.json();
        const postsContainer = document.getElementById('posts-container');

        // Loop through each post and add to the DOM
        posts.posts.forEach(post => {
            addPostToDOM(post);  // Add comments directly if they are included
        });
    } catch (error) {
        console.error('Error fetching posts:', error);
    }
}
function addPostToDOM(post, preload = false, containerId = 'posts-container') {
    const postsContainer = document.getElementById(containerId);
    if (!postsContainer) {
        console.error(`Container with ID '${containerId}' not found.`);
        return;
    }

    const postElement = document.createElement('div');
    postElement.classList.add('post-box');
    postElement.setAttribute('data-post-id', post.id);

    const commentSection = document.createElement('div');
    commentSection.classList.add('comment-section');
    commentSection.style.display = 'none';

    // Preload comments if available
    if (post.comments && post.comments.length > 0) {
        post.comments.forEach(comment => {
            const commentElement = document.createElement('div');
            commentElement.classList.add('comment');
            commentElement.innerHTML = `
                <div class="comment-header">
                    <span class="comment-username">${comment.user}</span>
                    <span class="comment-id">#${comment.id}</span>
                </div>
                <p>${comment.content}</p>
            `;
            commentSection.appendChild(commentElement);
        });
    }

    postElement.innerHTML = `
        <div class="post-header">
            <span class="username">${post.user}</span>
            <span class="post-id">#${post.id}</span>
        </div>
        <p>${post.content}</p>
        <div class="post-actions">
            <button class="like-btn" data-post-id="${post.id}">
                👍 Like (<span>${post.likes}</span>)
            </button>
            <button class="dislike-btn" data-post-id="${post.id}">
                👎 Dislike (<span>${post.dislikes}</span>)
            </button>
            <button class="comment-btn" data-post-id="${post.id}">
                💬 Comment
            </button>
        </div>
    `;

    postElement.appendChild(commentSection);

    const seeCommentsButton = document.createElement('button');
    seeCommentsButton.textContent = "See Comments";
    seeCommentsButton.classList.add('see-comments-btn');
    seeCommentsButton.addEventListener('click', function () {
        commentSection.style.display = commentSection.style.display === 'none' ? 'block' : 'none';
    });
    postElement.appendChild(seeCommentsButton);

    postsContainer.appendChild(postElement);
}

function commentPost(button) {
    const postBox = button.closest('.post-box');
    const postId = postBox.dataset.postId;

    if (!postId) {
        console.error('Post ID not found');
        return;
    }

    const commentSection = postBox.querySelector('.comment-section');

    let commentInputField = postBox.querySelector('.comment-input-field');
    if (!commentInputField) {
        const inputContainer = document.createElement('div');
        inputContainer.classList.add('comment-input-container');

        commentInputField = document.createElement('input');
        commentInputField.type = 'text';
        commentInputField.placeholder = 'Write a comment...';
        commentInputField.classList.add('comment-input-field');

        const submitButton = document.createElement('button');
        submitButton.textContent = 'Submit';
        submitButton.classList.add('comment-submit-btn');
        submitButton.addEventListener('click', function () {
            const commentText = commentInputField.value.trim();
            if (commentText) {
                addComment(commentSection, commentText, postId);
                commentInputField.value = '';
            }
        });

        inputContainer.appendChild(commentInputField);
        inputContainer.appendChild(submitButton);

        postBox.appendChild(inputContainer);
    }
}
async function addComment(commentSection, commentText, postId) {
    try {
        const response = await fetch(`/posts/comment/${postId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ content: commentText }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Error:', errorData.error);
            alert('Error: ' + errorData.error);
        } else {
            const data = await response.json();
            const commentElement = document.createElement('div');
            commentElement.classList.add('comment');
            commentElement.innerHTML = `
                <div class="comment-header">
                    <span class="comment-username">${data.user}</span>
                    <span class="comment-id">#${data.comment_id}</span>
                </div>
                <p>${data.content}</p>
            `;
            commentSection.appendChild(commentElement);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again later.');
    }
}
function likePost(button) {
    const postActions = button.closest('.post-actions');
    const dislikeButton = postActions.querySelector('.dislike-btn');
    const postId = button.dataset.postId;

    // Check if the button was already liked
    if (button.classList.contains('active')) {
        // Remove like
        button.classList.remove('active');
        const likeCountElement = button.querySelector('span');
        let likeCount = parseInt(likeCountElement.textContent);
        likeCountElement.textContent = likeCount - 1;

        // Send remove-like request to the backend
        updateLikeStatus(postId, 'remove-like');
        return;
    }

    // If the dislike button was active, remove dislike
    if (dislikeButton.classList.contains('active')) {
        dislikeButton.classList.remove('active');
        const dislikeCountElement = dislikeButton.querySelector('span');
        let dislikeCount = parseInt(dislikeCountElement.textContent);
        dislikeCountElement.textContent = dislikeCount - 1;

        // Send remove-dislike request to the backend
        updateLikeStatus(postId, 'remove-dislike');
    }

    // Add like
    button.classList.add('active');
    const likeCountElement = button.querySelector('span');
    let likeCount = parseInt(likeCountElement.textContent);
    likeCountElement.textContent = likeCount + 1;

    // Send like request to the backend
    updateLikeStatus(postId, 'like');
}
// Function to handle "Dislike" button click
function dislikePost(button) {
    const postActions = button.closest('.post-actions');
    const likeButton = postActions.querySelector('.like-btn');
    const postId = button.dataset.postId;

    // Check if the button was already disliked
    if (button.classList.contains('active')) {
        // Remove dislike
        button.classList.remove('active');
        const dislikeCountElement = button.querySelector('span');
        let dislikeCount = parseInt(dislikeCountElement.textContent);
        dislikeCountElement.textContent = dislikeCount - 1;

        // Send remove-dislike request to the backend
        updateLikeStatus(postId, 'remove-dislike');
        return;
    }

    // If the like button was active, remove like
    if (likeButton.classList.contains('active')) {
        likeButton.classList.remove('active');
        const likeCountElement = likeButton.querySelector('span');
        let likeCount = parseInt(likeCountElement.textContent);
        likeCountElement.textContent = likeCount - 1;

        // Send remove-like request to the backend
        updateLikeStatus(postId, 'remove-like');
    }

    // Add dislike
    button.classList.add('active');
    const dislikeCountElement = button.querySelector('span');
    let dislikeCount = parseInt(dislikeCountElement.textContent);
    dislikeCountElement.textContent = dislikeCount + 1;

    // Send dislike request to the backend
    updateLikeStatus(postId, 'dislike');
}
// Function to send like/dislike updates to the backend
async function updateLikeStatus(postId, action) {
    const csrfToken = getCsrfToken();

    let url = '';
    if (action === 'like') {
        url = `/posts/like/${postId}/`;
    } else if (action === 'remove-like') {
        url = `/posts/remove-like/${postId}/`;
    } else if (action === 'dislike') {
        url = `/posts/dislike/${postId}/`;
    } else if (action === 'remove-dislike') {
        url = `/posts/remove-dislike/${postId}/`;
    }

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Error:', errorData.error);
            alert('Error: ' + errorData.error);
        } else {
            const data = await response.json();
            console.log('Post updated:', data.message);

            const postBox = document.querySelector(`[data-post-id="${postId}"]`);
            if (postBox) {
                const likeCount = postBox.querySelector('.like-btn span');
                const dislikeCount = postBox.querySelector('.dislike-btn span');

                if (likeCount) likeCount.textContent = data.likes;
                if (dislikeCount) dislikeCount.textContent = data.dislikes;
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again later.');
    }
}
//initialise before use
var currentUser = currentUser;

async function renderSentimentBar() {
    try {
        const response = await fetch('/posts/get-sentiment-data/');
        if (!response.ok) {
            throw new Error('Failed to fetch sentiment data');
        }

        const data = await response.json();

        // Find the current user's sentiment data
        const userSentiment = data.users_data.find(user => user.user === currentUser);

        if (!userSentiment) {
            console.error('Current user sentiment data was not found.');
            return;
        }
        //default 0
        const positive = userSentiment.positive_percentage || 0;
        const neutral = userSentiment.neutral_percentage || 0;
        const negative = userSentiment.negative_percentage || 0;

        // Calculate total width of each colour in the sentiment bar. the width will equal the total percentage of each sentiment
        const totalSentiment = positive + neutral + negative;
        const positiveWidth = (positive / totalSentiment) * 100;
        const neutralWidth = (neutral / totalSentiment) * 100;
        const negativeWidth = (negative / totalSentiment) * 100;

        // Set up the sentiment bar and clear any existing content
        const sentimentBar = document.getElementById('sentiment-bar');
        sentimentBar.innerHTML = '';

        // Create divs for each sentiment section
        const positiveSection = document.createElement('div');
        positiveSection.style.width = positiveWidth + '%';
        positiveSection.classList.add('sentiment-section', 'positive');
        positiveSection.textContent = `Positive`;

        const neutralSection = document.createElement('div');
        neutralSection.style.width = neutralWidth + '%';
        neutralSection.classList.add('sentiment-section', 'neutral');
        neutralSection.textContent = `Neutral`;

        const negativeSection = document.createElement('div');
        negativeSection.style.width = negativeWidth + '%';
        negativeSection.classList.add('sentiment-section', 'negative');
        negativeSection.textContent = `Negative`;

        // Append the sections to the sentiment bar
        sentimentBar.appendChild(positiveSection);
        sentimentBar.appendChild(neutralSection);
        sentimentBar.appendChild(negativeSection);

    } catch (error) {
        console.error('Could not fetching sentiment data:', error);
        alert('Failed to load sentiment data.');
    }
}
async function loadOpposingViewsPosts() {
    try {
        // Fetch sentiment data for the current user
        const sentimentResponse = await fetch('/posts/get-sentiment-data/');
        if (!sentimentResponse.ok) {
            throw new Error('Failed to fetch sentiment data');
        }
        const sentimentData = await sentimentResponse.json();

        // Determine user's sentiment and find opposing sentiment
        const userSentiment = sentimentData.users_data.find(user => user.user === currentUser);
        if (!userSentiment) {
            console.error('Current user sentiment data not found.');
            return;
        }
        let opposingSentiment;
        if (userSentiment.positive_percentage > userSentiment.negative_percentage) {
            opposingSentiment = 'positive';
        } else if (userSentiment.negative_percentage > userSentiment.positive_percentage) {
            opposingSentiment = 'negative';
        } else {
            opposingSentiment = 'neutral';
        }

        // Fetch posts with the opposing sentiment
        const postsResponse = await fetch(`/posts/get-opposing-posts/${opposingSentiment}/`);
        if (!postsResponse.ok) {
            throw new Error('Failed to fetch opposing posts');
        }
        const posts = await postsResponse.json();

        const opposingPostsContainer = document.getElementById('opposing-posts-container');
        if (!opposingPostsContainer) {
            console.error('Opposing posts container not found.');
            return;
        }

        // Clear the container and add new posts
        opposingPostsContainer.innerHTML = '';
        posts.posts.forEach(post => {
            addPostToDOM(post, true, 'opposing-posts-container'); // Ensure correct container
        });

        // Handle cases where no opposing poss are found
        if (posts.posts.length === 0) {
            opposingPostsContainer.innerHTML = '<p>No opposing views posts available at the moment.</p>';
        }
    } catch (error) {
        console.error('Error fetching opposing posts:', error);
        alert('Failed to load opposing posts.');
    }
}
function showPage(pageId) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.remove('active'));

    const activePage = document.getElementById(pageId);
    if (activePage) {
        activePage.classList.add('active');
    } else {
        console.error('Page not found:', pageId);
    }
}
function showOrderedPosts(orderType) {
 
    // Clear the posts container
    const postsContainer = document.getElementById('posts-container');
    postsContainer.innerHTML = '';

    // Fetch ordered posts from the backend
    fetch(`/posts/get-ordered-posts/${orderType.toLowerCase()}/`)
        .then(response => {
            if (!response.ok) throw new Error('Failed to fetch posts.');
            return response.json();
        })
        .then(data => {
            data.posts.forEach(post => {
                addPostToDOM(post); 
            });

            if (data.posts.length === 0) {
                postsContainer.innerHTML = '<p>No posts available for this order.</p>';
            }
        })
        .catch(error => console.error('Error fetching posts:', error));
}

