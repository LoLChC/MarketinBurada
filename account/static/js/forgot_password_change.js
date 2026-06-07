window.addEventListener("pageshow", function (event) {
    if (event.persisted) {
        window.location.reload();
    }
});

function showChangeFlash(message, type = 'error') {
    const container = document.getElementById('change-flash-container');
    if (!container) return;

    container.innerHTML = '';
    const flashCard = document.createElement('div');
    flashCard.className = `inline-flash ${type}`;
    
    flashCard.innerHTML = `
        <span class="flash-text">${message}</span>
        <button type="button" class="flash-close" aria-label="Kapat">&times;</button>
    `;

    flashCard.querySelector('.flash-close').addEventListener('click', () => {
        flashCard.style.opacity = '0';
        flashCard.style.transform = 'translateY(-10px)';
        setTimeout(() => flashCard.remove(), 200);
    });

    container.appendChild(flashCard);
}

function checkPasswordStrength(password) {
    let score = 0;
    if (!password) return { score: 0, text: '', class: '' };

    if (password.length >= 6) score++; 
    if (password.length >= 10) score++; 
    if (/[A-Z]/.test(password) && /[a-z]/.test(password)) score++; 
    if (/[0-9]/.test(password)) score++; 
    if (/[^A-Za-z0-9]/.test(password)) score++; 

    if (score <= 1) return { score: 20, text: 'Çok Zayıf', class: 'very-weak' };
    if (score === 2) return { score: 40, text: 'Zayıf', class: 'weak' };
    if (score === 3) return { score: 65, text: 'Orta', class: 'medium' };
    if (score === 4) return { score: 85, text: 'Güçlü', class: 'strong' };
    return { score: 100, text: 'Çok Güçlü 🎉', class: 'very-strong' };
}

document.addEventListener('DOMContentLoaded', function () {
    const changeForm = document.getElementById('passwordChangeForm');
    const passwordInput = document.getElementById('password');
    const strengthBar = document.getElementById('strength-bar');
    const strengthText = document.getElementById('strength-text');
    const togglePasswordButtons = document.querySelectorAll('.toggle-password-btn');

    // Göz Butonları
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            const inputField = document.getElementById(targetId);
            const icon = this.querySelector('.toggle-icon');

            if (inputField && icon) {
                if (inputField.type === 'password') {
                    inputField.type = 'text';
                    icon.classList.replace('fa-eye', 'fa-eye-slash');
                } else {
                    inputField.type = 'password';
                    icon.classList.replace('fa-eye-slash', 'fa-eye');
                }
            }
        });
    });

    // Realtime Güç Kontrolü
    if (passwordInput && strengthBar && strengthText) {
        passwordInput.addEventListener('input', function () {
            const password = passwordInput.value;
            const result = checkPasswordStrength(password);

            strengthBar.style.width = result.score + '%';
            strengthBar.className = 'strength-bar ' + result.class;
            
            strengthText.textContent = result.text;
            strengthText.className = 'strength-text ' + result.class;
        });
    }

    // Submit Validations & Loader
    if (changeForm) {
        changeForm.addEventListener('submit', function (event) {
            const password = passwordInput.value;
            const passwordConfirm = document.getElementById('password_confirm').value;
            const strength = checkPasswordStrength(password);

            if (strength.score > 0 && strength.score <= 40) {
                event.preventDefault();
                showChangeFlash('Hesap güvenliğiniz için lütfen daha güçlü bir şifre seçin.', 'error');
                return false;
            }

            if (password !== passwordConfirm) {
                event.preventDefault();
                showChangeFlash('Girdiğiniz şifreler birbiriyle uyuşmuyor.', 'error');
                return false;
            }

            // Loader'ı Aç
            const loader = document.getElementById('page-loader');
            if (loader) {
                loader.style.display = 'flex';
                loader.style.opacity = '1';
            }
        });
    }
});