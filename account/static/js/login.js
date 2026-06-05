/**
 * ==========================================================================
 * GİRİŞ SAYFASI DİNAMİKLERİ - login.js
 * ==========================================================================
 */

/**
 * Login Kartı İçine Dinamik Flash Mesaj Basar
 * @param {string} message - Gösterilecek metin
 * @param {string} type - 'success' veya 'error'
 */
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

// DOM Yüklendiğinde Tetiklenecek Olaylar
document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
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

    // 2. Form gönderildiğinde bekleme ekranını tetikle
    if (loginForm) {
        loginForm.addEventListener('submit', function () {
            showLoader(); // layout.js içindeki global fonksiyonu çağırır
        });
    }
});