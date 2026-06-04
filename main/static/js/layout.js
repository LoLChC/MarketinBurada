document.addEventListener('DOMContentLoaded', function () {
    
    initHeaderDynamics();
    initMainAnimations();

});

let loaderStartTime = 0;

function showLoader() {
    const loader = document.getElementById('page-loader');
    if (loader) {
        loaderStartTime = Date.now(); // Loader'ın açıldığı anı milisaniye olarak kaydet
        loader.style.opacity = '0';
        loader.style.display = 'flex';
        setTimeout(() => { loader.style.opacity = '1'; }, 10);
    }
}

function hideLoader() {
    const loader = document.getElementById('page-loader');
    if (!loader) return;

    const currentTime = Date.now();
    const elapsedTime = currentTime - loaderStartTime; // Loader'ın açık kaldığı süre
    const targetTime = 1; // Hedeflenen minimum süre (10 saniye)

    if (elapsedTime < targetTime) {
        // Eğer 10 saniyeden önce kapanmak istendiyse, kalan süreyi hesapla ve bekle
        const remainingTime = targetTime - elapsedTime;
        setTimeout(() => {
            executeHide(loader);
        }, remainingTime);
    } else {
        // 10 saniye çoktan geçtiyse hemen kapat
        executeHide(loader);
    }
}

// Kapatma işlemini asıl yapan yardımcı fonksiyon
function executeHide(loader) {
    loader.style.opacity = '0';
    setTimeout(() => { loader.style.display = 'none'; }, 300);
}