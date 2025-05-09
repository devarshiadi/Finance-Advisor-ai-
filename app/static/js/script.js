// Global JavaScript functions can be added here.

document.addEventListener('DOMContentLoaded', function () {
    // Example: Add a class to the body to indicate JS is enabled
    document.body.classList.add('js-enabled');

    // You could centralize common functions here if needed,
    // for example, a function to make API calls with error handling.
    // const apiRequest = async (url, method, body = null, headers = {}) => { ... }

    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', function (event) {
            event.preventDefault(); // Prevent default anchor action
            
            localStorage.removeItem('accessToken');
            localStorage.removeItem('tokenType');
            
            // Redirect to the server's /logout endpoint, which then redirects to login page
            // This ensures any server-side session cleanup (if implemented later) could also occur.
            window.location.href = '/logout'; 
        });
    }

    // Client-side check to update navbar based on token presence
    // This runs on every page load to set the correct initial state for navbar items.
    const accessToken = localStorage.getItem('accessToken');
    const navWelcomeItem = document.getElementById('navWelcomeItem');
    const navLogoutItem = document.getElementById('navLogoutItem');
    const navLoginItem = document.getElementById('navLoginItem');
    const navSignupItem = document.getElementById('navSignupItem');

    if (accessToken) {
        // User is logged in (according to localStorage)
        if (navWelcomeItem) navWelcomeItem.style.display = 'block'; // Or 'list-item' if needed
        if (navLogoutItem) navLogoutItem.style.display = 'block';
        if (navLoginItem) navLoginItem.style.display = 'none';
        if (navSignupItem) navSignupItem.style.display = 'none';
        
        // Optional: Fetch user email to display in welcome message
        // Could be done here or within specific page scripts like homepage.html
        // fetch('/auth/users/me', { headers: {'Authorization': `Bearer ${accessToken}`} })
        //   .then(response => response.ok ? response.json() : Promise.reject('Failed'))
        //   .then(data => {
        //       const welcomeSpan = document.getElementById('navUserWelcome');
        //       if (welcomeSpan) welcomeSpan.textContent = `Welcome, ${data.email}`;
        //   })
        //   .catch(err => console.error("Error fetching user for navbar:", err));

    } else {
        // User is logged out
        if (navWelcomeItem) navWelcomeItem.style.display = 'none';
        if (navLogoutItem) navLogoutItem.style.display = 'none';
        if (navLoginItem) navLoginItem.style.display = 'block';
        if (navSignupItem) navSignupItem.style.display = 'block';
    }
});

// Function to get CSRF token if using CSRF protection with forms not handled by FastAPI's default
// function getCookie(name) { ... } 
// Not strictly needed for this JWT setup unless forms post directly without JS.
