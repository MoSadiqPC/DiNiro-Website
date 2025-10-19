document.addEventListener('DOMContentLoaded', () => {
    // Theme Toggle Logic
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        const body = document.body;
        function setTheme(theme) {
            body.classList.toggle('light-mode', theme === 'light');
            themeToggle.textContent = theme === 'light' ? '🌙' : '☀️';
            localStorage.setItem('theme', theme);
        }
        themeToggle.addEventListener('click', () => {
            setTheme(body.classList.contains('light-mode') ? 'dark' : 'light');
        });
        setTheme(localStorage.getItem('theme') || 'dark');
    }

    // Countdown Logic for Reveal Page
    const countdownTimer = document.getElementById('countdown-timer');
    if (countdownTimer) {
        const credentialsArea = document.getElementById('credentials-area');
        const countdownSection = document.querySelector('.credentials-countdown');
        let countdownValue = 10;

        const countdownInterval = setInterval(() => {
            countdownValue -= 1;
            countdownTimer.textContent = countdownValue;

            if (countdownValue <= 0) {
                clearInterval(countdownInterval);
                if (countdownSection) countdownSection.style.display = 'none';
                if (credentialsArea) credentialsArea.style.display = 'block';
            }
        }, 1000);
    }

    // Dropdown Menu Logic
    const dropdowns = document.querySelectorAll('.dropdown');

    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');

        if (toggle && menu) {
            toggle.addEventListener('click', (event) => {
                event.stopPropagation(); // Prevent closing immediately
                // Close other open dropdowns
                closeOtherDropdowns(dropdown);
                // Toggle the current dropdown
                dropdown.classList.toggle('show');
            });
        }
    });

    // Close dropdowns when clicking anywhere else
    window.addEventListener('click', (event) => {
        if (!event.target.closest('.dropdown-toggle')) {
            closeOtherDropdowns(null);
        }
    });

    function closeOtherDropdowns(currentDropdown) {
        dropdowns.forEach(dropdown => {
            if (dropdown !== currentDropdown) {
                dropdown.classList.remove('show');
            }
        });
    }
});