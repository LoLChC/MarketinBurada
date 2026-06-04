/**
 * ==========================================================================
 * KAYIT SAYFASI DİNAMİKLERİ - register.js
 * ==========================================================================
 */

/**
 * Register Kartı İçine Dinamik İnline Flash Mesaj Basar
 */
function showRegisterFlash(message, type = 'error') {
    const container = document.getElementById('register-flash-container');
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

/**
 * Şifre Gücünü Karakter ve Çeşitliliğe Göre Kontrol Eden Fonksiyon
 */
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

// DOM Yüklendiğinde Tetiklenecek Olaylar
document.addEventListener('DOMContentLoaded', function () {
    const registerForm = document.getElementById('registerForm');
    const passwordInput = document.getElementById('password');
    const strengthBar = document.getElementById('strength-bar');
    const strengthText = document.getElementById('strength-text');
    const togglePasswordButtons = document.querySelectorAll('.toggle-password-btn');

    // 1. Şifre Görünürlüğü (Göz Butonu) Yönetimi
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            const inputField = document.getElementById(targetId);
            const icon = this.querySelector('.toggle-icon');

            if (inputField && icon) {
                if (inputField.type === 'password') {
                    inputField.type = 'text';
                    // İkonu "gözü kapat" durumuna getir
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                    this.setAttribute('aria-label', 'Şifreyi Gizle');
                } else {
                    inputField.type = 'password';
                    // İkonu "gözü aç" durumuna getir
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                    this.setAttribute('aria-label', 'Şifreyi Göster');
                }
            }
        });
    });

    // 2. Kullanıcı şifre girdikçe barı ve metni gerçek zamanlı güncelle
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
    
    // 3. Form Gönderim Denetimi
    if (registerForm) {
        registerForm.addEventListener('submit', function (event) {
            const password = document.getElementById('password').value;
            const passwordConfirm = document.getElementById('password_confirm').value;
            const strength = checkPasswordStrength(password);

            if (strength.score > 0 && strength.score <= 40) {
                event.preventDefault();
                showRegisterFlash('Lütfen hesabınızın güvenliği için daha güçlü bir şifre seçin.', 'error');
                return false;
            }

            if (password !== passwordConfirm) {
                event.preventDefault();
                showRegisterFlash('Girdiğiniz şifreler birbiriyle uyuşmuyor.', 'error');
                return false;
            }

            showLoader();
        });
    }
});