/**
 * Marketin Burada - Kullanıcı Paneli Yönetim Scripti
 */
document.addEventListener("DOMContentLoaded", function () {
    
    // ==========================================================================
    // 1. Sekme Değiştirme ve F5 Koruma Mantığı (LocalStorage)
    // ==========================================================================
    const menuButtons = document.querySelectorAll(".sidebar-menu .menu-item[data-target], .sidebar-footer-menu .menu-item[data-target]");
    const contentPanels = document.querySelectorAll(".content-panel");

    function switchPanel(targetId) {
        if (!targetId) return;

        // Tüm aktiflik sınıflarını temizle
        menuButtons.forEach(btn => btn.classList.remove("active"));
        contentPanels.forEach(panel => panel.classList.remove("active"));

        const targetPanel = document.getElementById(targetId);
        const targetButton = document.querySelector(`[data-target="${targetId}"]`);

        if (targetPanel && targetButton) {
            targetPanel.classList.add("active");
            targetButton.classList.add("active");
            
            // Aktif sekmeyi hafızaya yaz
            localStorage.setItem("activeAccountTab", targetId);
        }
    }

    // Sayfa yenilendiğinde hafızadaki sekmeyi geri yükle
    const savedTab = localStorage.getItem("activeAccountTab");
    if (savedTab) {
        switchPanel(savedTab);
    } else {
        switchPanel("orders"); // Varsayılan sekme
    }

    // Menü tıklama dinleyicileri
    menuButtons.forEach(button => {
        button.addEventListener("click", function () {
            const target = this.getAttribute("data-target");
            switchPanel(target);
        });
    });

    // ==========================================================================
    // 2. Modal (Açılır Pencere) Yönetimi
    // ==========================================================================
    const addressModal = document.getElementById("address-modal");
    const paymentModal = document.getElementById("payment-modal");
    
    const btnOpenAddress = document.getElementById("btn-open-address-modal");
    const btnOpenPayment = document.getElementById("btn-open-payment-modal");
    const closeButtons = document.querySelectorAll(".modal-close");

    // Adres Modalı Aç
    if (btnOpenAddress && addressModal) {
        btnOpenAddress.addEventListener("click", function () {
            addressModal.classList.add("modal-active");
        });
    }

    // Kart Modalı Aç
    if (btnOpenPayment && paymentModal) {
        btnOpenPayment.addEventListener("click", function () {
            paymentModal.classList.add("modal-active");
        });
    }

    // Ortak Kapatma Buton Fonksiyonu (&times; - X butonu)
    closeButtons.forEach(btn => {
        btn.addEventListener("click", function () {
            const modalId = this.getAttribute("data-close");
            const targetModal = document.getElementById(modalId);
            if (targetModal) {
                targetModal.classList.remove("modal-active");
            }
        });
    });

    // Modallerin dışındaki gölgeye (Overlay) tıklandığında kapatma
    window.addEventListener("click", function (e) {
        if (e.target === addressModal) {
            addressModal.classList.remove("modal-active");
        }
        if (e.target === paymentModal) {
            paymentModal.classList.remove("modal-active");
        }
    });

    // ==========================================================================
    // 3. Giriş Maskeleri (Opsiyonel - Kart Bilgileri İçin Kolaylık)
    // ==========================================================================
    const cardNumberInput = document.getElementById("card-number");
    const cardExpiryInput = document.getElementById("card-expiry");

    // Kart numarasını her 4 basamakta bir otomatik boşluk bırakır
    if (cardNumberInput) {
        cardNumberInput.addEventListener("input", function (e) {
            let target = e.target;
            let position = target.selectionStart;
            let length = target.value.length;
            
            target.value = target.value.replace(/\s/g, '').replace(/(.{4})/g, '$1 ').trim();
            
            if(length !== target.value.length) {
                target.setSelectionRange(position + 1, position + 1);
            }
        });
    }

    // Son kullanma tarihine otomatik eğik çizgi ekler (AA/YY)
    if (cardExpiryInput) {
        cardExpiryInput.addEventListener("input", function (e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 2) {
                e.target.value = value.slice(0, 2) + '/' + value.slice(2, 4);
            } else {
                e.target.value = value;
            }
        });
    }
});