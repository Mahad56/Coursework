document.addEventListener('DOMContentLoaded', function () {
    const postButton = document.getElementById('post-button');
    if (postButton) {
        postButton.addEventListener('click', addPost);
    }

    const hamburger = document.querySelector('.sidebar-menu');
    if (hamburger) {
        hamburger.addEventListener('click', toggleMenu);
    }

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

    loadPosts();
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
    const sidebar = document.getElementById('sidebar-menu');
    sidebar.classList.toggle('active');
}

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
}

function showPage(pageId) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.remove('active'));

    const activePage = document.getElementById(pageId);
    if (activePage) {
        activePage.classList.add('active');
    }
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

        posts.posts.forEach(post => {
            addPostToDOM(post, true);
        });
    } catch (error) {
        console.error('Error fetching posts:', error);
    }
}

function addPostToDOM(post, preload = false) {
    const postsContainer = document.getElementById('posts-container');

    const postElement = document.createElement('div');
    postElement.classList.add('post-box');
    postElement.setAttribute('data-post-id', post.id);

    const commentSection = document.createElement('div');
    commentSection.classList.add('comment-section');
    commentSection.style.display = 'none';

    if (preload && post.comments) {
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
