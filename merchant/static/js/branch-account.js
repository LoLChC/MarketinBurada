/**
 * ==========================================================================
 * Marketin Burada - Şube Operasyonları ve Durum Yönetimi (State Control)
 * ==========================================================================
 * * İçerik (Modüller):
 * 1. Şube İçi Alt Sekme (Tab) Geçiş Mantığı
 * 2. Modal (Pop-up) Yönetim Sistemi
 * 3. Sipariş Durumu Veri Bağlama ve Şube Aksiyon Kontrolü
 * 4. Şube Stok Yönetimi ve Canlı Arama
 * ==========================================================================
 */

document.addEventListener("DOMContentLoaded", function () {

    // ==========================================================================
    // MODÜL 1: ŞUBE ALT SEKME GEÇİŞ KONTROLÜ
    // ==========================================================================
    const subMenuButtons = document.querySelectorAll(".account-sidebar .sidebar-menu .menu-item[data-target]");
    const subContentPanels = document.querySelectorAll(".account-content .content-panel");

    function switchSubPanel(targetId) {
        if (!targetId) return;

        subMenuButtons.forEach(btn => btn.classList.remove("active"));
        subContentPanels.forEach(panel => panel.classList.remove("active"));

        const targetPanel = document.getElementById(targetId);
        const targetButton = document.querySelector(`[data-target="${targetId}"]`);

        if (targetPanel && targetButton) {
            targetPanel.classList.add("active");
            targetButton.classList.add("active");
            sessionStorage.setItem("activeBranchSubTab", targetId);
        }
    }

    const savedSubTab = sessionStorage.getItem("activeBranchSubTab");
    if (savedSubTab) {
        switchSubPanel(savedSubTab);
    } else if (subContentPanels.length > 0) {
        switchSubPanel(subContentPanels[0].id);
    }

    subMenuButtons.forEach(btn => {
        btn.addEventListener("click", function () {
            const target = this.getAttribute("data-target");
            switchSubPanel(target);
        });
    });

    // ==========================================================================
    // MODÜL 2: MODAL (POP-UP) AÇMA VE KAPATMA SİSTEMİ
    // ==========================================================================
    const closeModalsBtns = document.querySelectorAll(".modal-close, .modal-overlay");
    const modalBoxes = document.querySelectorAll(".modal-box");

    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.add("modal-active");
    }

    closeModalsBtns.forEach(btn => {
        btn.addEventListener("click", function (e) {
            if (this.classList.contains("modal-overlay") && e.target !== this) {
                return;
            }
            const activeModals = document.querySelectorAll(".modal-overlay.modal-active");
            activeModals.forEach(modal => modal.classList.remove("modal-active"));
        });
    });

    modalBoxes.forEach(box => {
        box.addEventListener("click", e => e.stopPropagation());
    });

    // ==========================================================================
    // MODÜL 3: SİPARİŞ DURUM KONTROLÜ VE VERİ BAĞLAMA (STATE MACHINE)
    // Şube sadece "pending" -> "preparing" -> "ready" adımlarını yönetebilir.
    // ==========================================================================

    // 3.1 Kart Üzerindeki Doğrudan Aksiyon Butonları
    const directActionBtns = document.querySelectorAll(".btn-action-status");
    directActionBtns.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.stopPropagation(); // Modalin açılmasını engeller
            const orderId = this.getAttribute("data-id");

            // Backend'e fetch atılacak kısım simülasyonu
            if (this.classList.contains("btn-status-prepare")) {
                alert(`${orderId} numaralı sipariş onaylandı. Lütfen paketlemeye başlayın.`);
            } else if (this.classList.contains("btn-status-ready")) {
                alert(`${orderId} numaralı sipariş hazırlandı. Kurye atanması bekleniyor.`);
            }
        });
    });

    // 3.2 Sipariş Detay Modalının Verilerle Doldurulması ve Dinamik Butonlar
    const branchOrderCards = document.querySelectorAll(".clickable-branch-order");

    branchOrderCards.forEach(card => {
        card.addEventListener("click", function () {
            // Veri okuma
            const orderId = this.getAttribute("data-order-id");
            const orderDate = this.getAttribute("data-order-date");
            const orderTotal = this.getAttribute("data-order-total");
            const orderAddress = this.getAttribute("data-order-address");
            const orderStatus = this.getAttribute("data-order-status"); // backend keyword
            const orderStatusText = this.getAttribute("data-order-status-text");

            // Modal elemanları
            const idEl = document.getElementById("popup-branch-order-id");
            const dateEl = document.getElementById("popup-branch-order-date");
            const totalEl = document.getElementById("popup-branch-order-grand-total");
            const addressEl = document.getElementById("popup-branch-order-address");
            const statusEl = document.getElementById("popup-branch-order-status");
            const itemsBody = document.getElementById("popup-branch-order-items-body");

            // Dinamik aksiyon konteyneri
            const actionContainer = document.getElementById("popup-branch-action-container");
            const btnPrepare = document.getElementById("popup-btn-prepare");
            const btnReady = document.getElementById("popup-btn-ready");

            // Metin atamaları
            if (idEl) idEl.textContent = "#" + orderId;
            if (dateEl) dateEl.textContent = orderDate;
            if (totalEl) totalEl.textContent = orderTotal + " TL";
            if (addressEl) addressEl.textContent = orderAddress;
            if (statusEl) statusEl.textContent = orderStatusText;

            // Şube Yetki Denetimi: Sadece pending ve preparing durumlarında buton göster
            if (actionContainer && btnPrepare && btnReady) {
                if (orderStatus === "pending") {
                    actionContainer.style.display = "block";
                    btnPrepare.style.display = "block";
                    btnPrepare.setAttribute("data-id", orderId);
                    btnReady.style.display = "none";
                } else if (orderStatus === "preparing") {
                    actionContainer.style.display = "block";
                    btnPrepare.style.display = "none";
                    btnReady.style.display = "block";
                    btnReady.setAttribute("data-id", orderId);
                } else {
                    // ready, on_the_way, delivered, canceled durumlarında işlem yapılamaz
                    actionContainer.style.display = "none";
                }
            }

            // Simüle edilmiş ürün kalemleri
            if (itemsBody) {
                itemsBody.innerHTML = `
                    <tr>
                        <td>Sütaş Süt 1L</td>
                        <td class="text-center">2</td>
                        <td class="text-right">40.00 TL</td>
                        <td class="text-right">80.00 TL</td>
                    </tr>
                    <tr>
                        <td>Sütaş Ayran 290ml</td>
                        <td class="text-center">10</td>
                        <td class="text-right">15.00 TL</td>
                        <td class="text-right">150.00 TL</td>
                    </tr>
                `;
            }

            openModal("branch-order-detail-modal");
        });
    });

    // ==========================================================================
    // MODÜL 4: STOK POP-UP VE CANLI FİLTRELEME ENTEGRASYONU
    // ==========================================================================
    const openStockPopupBtns = document.querySelectorAll(".btn-open-stock-edit-popup");
    const stockModal = document.getElementById("branch-stock-edit-modal");
    const modalProdId = document.getElementById("modal-edit-stock-product-id");
    const modalProdName = document.getElementById("modal-edit-stock-product-name");
    const modalProdQty = document.getElementById("modal-edit-stock-qty");

    openStockPopupBtns.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.stopPropagation();

            const productId = this.getAttribute("data-product-id");
            const productName = this.getAttribute("data-product-name");
            const currentStock = this.getAttribute("data-current-stock");

            if (modalProdId) modalProdId.value = productId;
            if (modalProdName) modalProdName.value = productName;
            if (modalProdQty) modalProdQty.value = currentStock;

            if (stockModal) stockModal.classList.add("modal-active");
        });
    });

    const branchStockSearch = document.getElementById("branch-stock-search");
    const branchStockCards = document.querySelectorAll(".branch-stock-item-card");

    if (branchStockSearch) {
        branchStockSearch.addEventListener("input", function () {
            const query = this.value.toLowerCase().trim();

            branchStockCards.forEach(card => {
                const productName = card.getAttribute("data-product-name").toLowerCase();
                if (productName.includes(query)) {
                    card.style.display = "flex";
                } else {
                    card.style.display = "none";
                }
            });
        });
    }

});