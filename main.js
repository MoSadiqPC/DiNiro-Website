// (الكود الكامل الذي أعطيتني إياه سابقاً، بدون تغيير)
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        const body = document.body;
        function setTheme(theme) {
            body.classList.toggle('light-mode', theme === 'light');
            themeToggle.textContent = theme === 'light' ? '🌙' : '☀️';
            localStorage.setItem('theme', theme);
        }
        themeToggle.addEventListener('click', () => { setTheme(body.classList.contains('light-mode') ? 'dark' : 'light'); });
        setTheme(localStorage.getItem('theme') || 'dark');
    }
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
});