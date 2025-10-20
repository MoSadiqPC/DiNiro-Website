// === Theme Logic ===
function toggleTheme() {
    const body = document.body;
    body.classList.toggle('light-mode');
    
    // Save user preference in localStorage
    const currentTheme = body.classList.contains('light-mode') ? 'light' : 'dark';
    localStorage.setItem('theme', currentTheme);
    
    // Update theme icon
    const themeSwitch = document.getElementById('theme-toggle');
    if (themeSwitch) {
        themeSwitch.textContent = currentTheme === 'light' ? '🌙' : '☀️';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'dark'; // Default to dark
    const body = document.body;
    body.classList.toggle('light-mode', savedTheme === 'light');
    
    const themeSwitch = document.getElementById('theme-toggle');
    if (themeSwitch) {
        themeSwitch.textContent = savedTheme === 'light' ? '🌙' : '☀️';
        themeSwitch.addEventListener('click', toggleTheme); // Add listener here
    }
});
// === End Theme Logic ===


// === Dropdown Menu Logic ===
function toggleDropdown(button) {
    const dropdown = button.closest('.dropdown');
    // Close other dropdowns
    document.querySelectorAll('.dropdown.show').forEach(d => {
        if (d !== dropdown) d.classList.remove('show');
    });
    // Toggle current one
    dropdown.classList.toggle('show');
}

window.onclick = function(event) {
    // Make sure the click is not on the theme switcher
    if (!event.target.matches('.dropdown-toggle') && !event.target.matches('.theme-switch')) {
        const dropdowns = document.getElementsByClassName("dropdown");
        for (let i = 0; i < dropdowns.length; i++) {
            const openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}
// === End Dropdown Logic ===