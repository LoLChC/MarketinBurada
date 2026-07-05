/**
 * ==========================================================================
 * Marketin Burada - Kurye Paneli JavaScript İşlevleri
 * ==========================================================================
 */

document.addEventListener("DOMContentLoaded", function () {

    // 1. Sekme (Tab) Yönetimi
    const menuButtons = document.querySelectorAll(".sidebar-menu .menu-item[data-target]");
    const contentPanels = document.querySelectorAll(".content-panel");

    function switchPanel(targetId) {
        if (!targetId) return;

        menuButtons.forEach(btn => btn.classList.remove("active"));
        contentPanels.forEach(panel => panel.classList.remove("active"));

        const targetPanel = document.getElementById(targetId);
        const targetButton = document.querySelector(`[data-target="${targetId}"]`);

        if (targetPanel && targetButton) {
            targetPanel.classList.add("active");
            targetButton.classList.add("active");
            localStorage.setItem("activeCourierTab", targetId);
        }
    }

    const savedTab = localStorage.getItem("activeCourierTab");
    if (savedTab) {
        switchPanel(savedTab);
    } else {
        const firstPanel = contentPanels[0];
        if (firstPanel) switchPanel(firstPanel.id);
    }

    menuButtons.forEach(button => {
        button.addEventListener("click", function () {
            const target = this.getAttribute("data-target");
            switchPanel(target);
        });
    });

    // 2. Modalları Kapatma Mekanizması
    const closeModalBtns = document.querySelectorAll(".js-close-modal, .modal-overlay");
    closeModalBtns.forEach(btn => {
        btn.addEventListener("click", function (e) {
            if (this.classList.contains("modal-overlay") && e.target !== this) {
                return;
            }

            if (this.classList.contains("js-close-modal")) {
                const targetId = this.getAttribute("data-target");
                const modal = document.getElementById(targetId);
                if (modal) modal.classList.remove("modal-active");
                return;
            }

            const activeModals = document.querySelectorAll(".modal-overlay.modal-active");
            activeModals.forEach(modal => modal.classList.remove("modal-active"));
        });
    });

    const modalBoxes = document.querySelectorAll(".modal-box");
    modalBoxes.forEach(box => {
        box.addEventListener("click", e => e.stopPropagation());
    });

    // 3. Tıklanabilir Kartlar ve Dinamik Pop-up (Data Binding)
    const orderCards = document.querySelectorAll(".clickable-order-card");
    orderCards.forEach(card => {
        card.addEventListener("click", function (e) {
            // İçerideki butonlara (Görevi Üstlen vs) tıklandıysa modalı açma
            if (e.target.closest('button')) return;

            // Karttan verileri al
            const orderId = this.getAttribute("data-order-id");
            const orderStatus = this.getAttribute("data-order-status");
            const orderCustomer = this.getAttribute("data-order-customer");
            const orderPhone = this.getAttribute("data-order-phone");
            const orderAddress = this.getAttribute("data-order-address");

            // Modal elemanlarını yakala
            const idEl = document.getElementById("popup-order-id");
            const statusEl = document.getElementById("popup-order-status");
            const customerEl = document.getElementById("popup-order-customer");
            const phoneEl = document.getElementById("popup-order-phone");
            const addressEl = document.getElementById("popup-order-address");

            // Verileri modala yazdır
            if (idEl) idEl.textContent = orderId ? orderId : "";
            if (statusEl) statusEl.textContent = orderStatus ? orderStatus : "";
            if (customerEl) customerEl.textContent = orderCustomer ? orderCustomer : "";
            if (addressEl) addressEl.textContent = orderAddress ? orderAddress : "";

            // Koşul: Telefon Numarası Boş mu?
            if (phoneEl) {
                if (orderPhone && orderPhone.trim() !== "") {
                    phoneEl.textContent = orderPhone;
                    phoneEl.style.display = "block"; // Eğer numara varsa göster
                } else {
                    phoneEl.style.display = "none";  // Numarası (veya izni) yoksa gizle
                }
            }

            // Modalı aktif et
            const modal = document.getElementById("package-items-modal");
            if (modal) modal.classList.add("modal-active");
        });
    });

    // 4. Paketi Üstlenme (Claim) Butonu
    const claimPackageBtns = document.querySelectorAll(".js-claim-package");
    claimPackageBtns.forEach(btn => {
        btn.addEventListener("click", function () {
            if (confirm("Bu paketi dağıtmak üzere üzerinize almak istediğinize emin misiniz?")) {
                alert("Görev üstlenildi! Paket artık 'Üzerimdeki Paketler' sekmesinde görünecektir.");
                switchPanel("c-my-tasks");
            }
        });
    });

    // 5. Teslimatı Tamamlama Butonu
    const completeTaskBtns = document.querySelectorAll(".js-complete-task");
    completeTaskBtns.forEach(btn => {
        btn.addEventListener("click", function () {
            if (confirm("Siparişi müşteriye sorunsuz teslim ettiniz mi?")) {
                alert("Sipariş başarıyla teslim edildi olarak işaretlendi!");
                switchPanel("c-past-tasks");
            }
        });
    });

});