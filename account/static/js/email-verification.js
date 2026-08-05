/**
 * ==========================================================================
 * E-POSTA DOĞRULAMA DİNAMİKLERİ - email-verification.js (Gelişmiş Frontend UI & Polling)
 * ==========================================================================
 */

// Konfigürasyon: Django URL'lerini veya statik test URL'lerini buraya tanımlayabilirsin
const VERIFY_CONFIG = {
    CHECK_URL: '/core/verify-email-looking/', // Test veya dinamik URL yapın
    REDIRECT_URL: '/account/user-account'
};

/**
 * Kartın Altına veya İçine Dinamik İnline Flash Mesaj Basar
 */
function showVerifyFlash(message, type = 'error') {
    const container = document.getElementById('verify-flash-container');
    if (!container) return;

    // Varsa eski mesajları temizle
    container.innerHTML = '';

    const flashCard = document.createElement('div');
    const normalizedType = type.includes('success') ? 'success' : 'error';
    flashCard.className = `inline-flash ${normalizedType}`;

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

document.addEventListener('DOMContentLoaded', function () {
    // ----------------------------------------------------------------------
    // 1. Yeniden Gönder Butonu Tetikleyicisi
    // ----------------------------------------------------------------------
    const resendBtn = document.getElementById('resend-verification-btn');

    if (resendBtn) {
        resendBtn.addEventListener('click', function (e) {
            e.preventDefault();

            // UI Loader Tetikleme Örneği
            if (typeof showLoader === 'function') {
                showLoader();
            }

            // UI Testleri İçin Manuel Tetikleme Örnekleri (Gerekirse açabilirsin):
            // showVerifyFlash('Doğrulama e-postası başarıyla tekrar gönderildi.', 'success');
        });
    }

    // ----------------------------------------------------------------------
    // 2. Otomatik E-posta Doğrulama Kontrolü (Polling)
    // ----------------------------------------------------------------------
    const checkVerification = setInterval(async () => {
        try {
            const response = await fetch(VERIFY_CONFIG.CHECK_URL, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest', // AJAX isteği olduğunu belirtmek için
                    'Content-Type': 'application/json'
                }
            });

            // Yanıt başarılı değilse (örn: 404, 500) işleme devam etme
            if (!response.ok) return;

            const data = await response.json();

            // Backend'den gelen doğrulandı bilgisinin kontrolü
            if (data.verify === 'ok' || data.verify === true) {
                clearInterval(checkVerification); // Döngüyü durdur
                window.location.href = VERIFY_CONFIG.REDIRECT_URL;
            }
        } catch (error) {
            // Konsolda kirlilik yaratmamak için bağlantı hatalarını sessizce logla
            console.warn("Doğrulama durumu kontrol ediliyor...", error);
        }
    }, 1000); // 1 saniyede bir çalışır

    // Sayfadan ayrılırken (örneğin sekme kapatılırsa) interval'ı temizle
    window.addEventListener('unload', () => {
        clearInterval(checkVerification);
    });
});