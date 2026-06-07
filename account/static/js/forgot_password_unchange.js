// Bu sayfa statik bir hata bilgilendirmesi sunduğu için şimdilik sadece back-forward cache koruması barındırıyor.
window.addEventListener("pageshow", function (event) {
    if (event.persisted) {
        window.location.reload();
    }
});

document.addEventListener('DOMContentLoaded', function () {
    console.log("Geçersiz link sayfasına yönlendirildi.");
});