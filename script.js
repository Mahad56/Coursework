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
}
