// scripts.js

// Function to toggle the navigation menu in mobile view
function toggleMenu() {
    const navList = document.getElementById('nav-list');
    navList.classList.toggle('show-menu');
}

// Function to update Quick Actions dynamically based on user roles
function updateQuickActions() {
    // Placeholder: Fetch user roles from the backend and then update the UI accordingly
    // For demo purposes, let's assume the user role is "admin"
    const isAdmin = true; // This should be determined by actual user role data

    // Grab the Quick Actions container
    const quickActionsContainer = document.getElementById('quick-actions');

    if (isAdmin) {
        quickActionsContainer.innerHTML = `
            <button onclick="location.href='/add-country'">Add New Country</button>
            <button onclick="location.href='/manage-countries'">Manage Countries</button>
            <button onclick="location.href='/generate-invoice'">Generate Invoice</button>
        `;
    }
    // Add more conditions for different user roles if necessary
}

// Function to update the notification count dynamically
function updateNotificationCount() {
    // Placeholder: Fetch the count of new notifications from the backend
    const notificationCount = 3; // Replace with actual data fetched from the backend
    const notificationCountElement = document.getElementById('notification-count');

    notificationCountElement.textContent = notificationCount;
}

// Function to filter recent activity based on search input
function searchActivities() {
    let input = document.getElementById('search-activities').value.toLowerCase();
    let activityList = document.getElementById('activity-list');
    let activities = activityList.getElementsByTagName('li');

    for (let activity of activities) {
        let text = activity.textContent || activity.innerText;
        activity.style.display = text.toLowerCase().includes(input) ? '' : 'none';
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Update UI components on page load
    updateQuickActions();
    updateNotificationCount();

    // Event listener for the search box
    const searchBox = document.getElementById('search-activities');
    searchBox.addEventListener('input', searchActivities);

    // Event listener for the hamburger menu
    const hamburger = document.querySelector('.hamburger-menu');
    hamburger.addEventListener('click', toggleMenu);

    // Event listener for the Customize Dashboard button
    const customizeButton = document.getElementById('customize-button');
    customizeButton.addEventListener('click', function() {
        const widgetOptions = document.getElementById('widget-options');
        widgetOptions.style.display = widgetOptions.style.display === 'none' ? 'block' : 'none';
    });

    // Event listeners for widget toggle checkboxes
    document.querySelectorAll('.widget-toggle').forEach(checkbox => {
        checkbox.addEventListener('change', function(event) {
            const widget = document.getElementById(event.target.dataset.widgetId);
            widget.style.display = event.target.checked ? 'block' : 'none';
        });
    });
});
