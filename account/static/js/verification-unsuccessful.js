/**
 * ==========================================================================
 * E-POSTA DOĞRULAMA BAŞARISIZ DİNAMİKLERİ - verification-unsuccessful.js
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('verify-flash-container');
    
    if (container) {
        // Ekrana doğrudan basılmasını istediğin yönlendirme uyarısı
        container.innerHTML = `
            <div class="inline-flash-info">
                Hesabım sayfasına gidip oradan tekrar e-posta doğrulaması yapın lütfen.
            </div>
        `;
    }
});