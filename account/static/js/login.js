function showFlash(message, type = 'error') {
    const container = document.getElementById('login-flash-container');
    if (!container) return;

    // Eski mesajı temizle ve yığılmayı önle
    container.innerHTML = '';

    // Yeni mesaj elementi oluştur
    const flashCard = document.createElement('div');
    flashCard.className = `inline-flash ${type}`;
    
    flashCard.innerHTML = `
        <span class="flash-text">${message}</span>
        <button type="button" class="flash-close" aria-label="Kapat">&times;</button>
    `;

    // Kapatma butonu aksiyonu
    flashCard.querySelector('.flash-close').addEventListener('click', () => {
        flashCard.style.opacity = '0';
        flashCard.style.transform = 'translateY(-10px)';
        setTimeout(() => flashCard.remove(), 200);
    });

    // Kapsayıcıya ekle
    container.appendChild(flashCard);
}

document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    const togglePasswordButtons = document.querySelectorAll('.toggle-password-btn');

    function showLoader() {
        const loader = document.getElementById('page-loader');
        if (!loader) return;
        location.reload();
        loader.style.display = 'flex';
        loader.style.opacity = '1';
    }

    function hideLoader() {
        const loader = document.getElementById('page-loader');
        if (!loader) return;
        loader.style.opacity = '0';
        setTimeout(() => {
            loader.style.display = 'none';
        }, 200);
    }

    // Password toggle
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            const input = document.getElementById(targetId);
            const icon = this.querySelector('.toggle-icon');

            if (!input || !icon) return;

            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });

    // Submit
    if (loginForm) {
        loginForm.addEventListener('submit', function () {
            showLoader();
        });
    }

    // Back/forward cache fix
    window.addEventListener('pageshow', function () {
        hideLoader();
    });
});