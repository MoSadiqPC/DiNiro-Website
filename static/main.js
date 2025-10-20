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

// Close dropdowns if clicked outside
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


// === All logic to run when the page is loaded ===
document.addEventListener('DOMContentLoaded', () => {
    
    // --- Theme ---
    const savedTheme = localStorage.getItem('theme') || 'dark'; // Default to dark
    const body = document.body;
    body.classList.toggle('light-mode', savedTheme === 'light');
    
    const themeSwitch = document.getElementById('theme-toggle');
    if (themeSwitch) {
        themeSwitch.textContent = savedTheme === 'light' ? '🌙' : '☀️';
        themeSwitch.addEventListener('click', toggleTheme); // Add listener here
    }

    // --- Countdown Logic ---
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
    // --- End Countdown Logic ---

    // --- Update Modal & Bell Logic (REVISED) ---
    const CURRENT_UPDATE_VERSION = 'v.0.7'; // عرّف الإصدار الحالي
    const modal = document.getElementById('update-modal');
    const overlay = document.getElementById('modal-overlay');
    const closeBtn = document.getElementById('modal-close-btn');
    const okBtn = document.getElementById('modal-ok-btn');
    const updateBell = document.getElementById('user-update-bell'); // جلب الجرس الجديد

    const lastSeenVersion = localStorage.getItem('seen_update_version');

    // 1. التحقق إذا كان المستخدم بحاجة لرؤية التحديث
    if (lastSeenVersion !== CURRENT_UPDATE_VERSION) {
        if (updateBell) {
            // استخدام 'inline-flex' لإظهار الجرس كعنصر flex
            updateBell.style.display = 'inline-flex';
            updateBell.style.alignItems = 'center'; // للتأكد من توسيط الأيقونة
        }
    }

    // 2. دالة لفتح النافذة
    function openModal() {
        if (modal) modal.classList.add('show');
        if (overlay) overlay.classList.add('show');
    }

    // 3. دالة لإغلاق النافذة
    function closeModal() {
        if (modal) modal.classList.remove('show');
        if (overlay) overlay.classList.remove('show');
        // عند الإغلاق، إخفاء الجرس وحفظ الإصدار
        if (updateBell) {
            updateBell.style.display = 'none';
        }
        localStorage.setItem('seen_update_version', CURRENT_UPDATE_VERSION);
    }

    // 4. إضافة أوامر النقر
    if (updateBell) updateBell.addEventListener('click', (e) => {
        e.preventDefault(); // منع الرابط من الانتقال
        openModal(); // فتح النافذة
    });
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (okBtn) okBtn.addEventListener('click', closeModal);
    if (overlay) overlay.addEventListener('click', closeModal);
    
    // --- End Update Modal Logic ---

});
// === End DOMContentLoaded ===