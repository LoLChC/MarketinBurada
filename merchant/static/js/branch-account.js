/**
 * ==========================================================================
 * Marketin Burada - Branch Paneli Merkez JavaScript Dosyası
 * ==========================================================================
 * * Modüller:
 * 1. Menü ve Sekme Yönetimi
 * 2. Dinamik Filtreleme ve Arama
 * 3. Modal (Pop-up) Yönetim Sistemi ve Kart Veri Bağlama
 * 4. Form Gönderim Yakalayıcılar
 * ==========================================================================
 */

document.addEventListener("DOMContentLoaded", function () {

    // ==========================================================================
    // MODÜL 1: MENÜ VE SEKME YÖNETİMİ
    // ==========================================================================
    const menuButtons = document.querySelectorAll(".sidebar-menu .menu-item[data-target]");
    const contentPanels = document.querySelectorAll(".content-panel");

    function switchPanel(targetId) {
        if (!targetId) return;

        // Tüm aktif sınıfları temizle
        menuButtons.forEach(btn => btn.classList.remove("active"));
        contentPanels.forEach(panel => panel.classList.remove("active"));

        const targetPanel = document.getElementById(targetId);
        const targetButton = document.querySelector(`[data-target="${targetId}"]`);

        // Hedeflenen sekmeye aktif sınıflarını ekle ve durumu sakla
        if (targetPanel && targetButton) {
            targetPanel.classList.add("active");
            targetButton.classList.add("active");
            localStorage.setItem("activeMerchantTab", targetId);
        }
    }

    // Sayfa yüklendiğinde hafızadaki sekmeyi yükle, yoksa ilk sekmeyi aç
    const savedTab = localStorage.getItem("activeMerchantTab");
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

    // ==========================================================================
    // MODÜL 2: DİNAMİK FİLTRELEME VE YÖNLENDİRMELER
    // ==========================================================================
    function filterCards(cards, searchInputId, filterSelectId) {
        const searchInput = document.getElementById(searchInputId);
        const filterSelect = document.getElementById(filterSelectId);

        if (!searchInput || !filterSelect) return;

        const searchText = searchInput.value.toLowerCase().trim();
        const selectedAisle = filterSelect.value;

        cards.forEach(card => {
            const nameAttr = card.getAttribute("data-product-name");
            const aisleAttr = card.getAttribute("data-aisle") || card.getAttribute("data-product-aisle");

            const productName = nameAttr ? nameAttr.toLowerCase() : "";
            const productAisle = aisleAttr ? aisleAttr : "";

            const matchesSearch = productName.includes(searchText);
            const matchesFilter = (selectedAisle === "all" || productAisle === selectedAisle);

            if (matchesSearch && matchesFilter) {
                card.style.display = "flex";
            } else {
                card.style.display = "none";
            }
        });
    }

    // Stok Arama ve Filtre Dinleyicileri
    const stockCards = document.querySelectorAll(".clickable-stock-card");
    const stockSearchInput = document.getElementById("stock-search-input");
    const stockAisleFilter = document.getElementById("stock-aisle-filter");
    if (stockSearchInput) stockSearchInput.addEventListener("input", () => filterCards(stockCards, "stock-search-input", "stock-aisle-filter"));
    if (stockAisleFilter) stockAisleFilter.addEventListener("change", () => filterCards(stockCards, "stock-search-input", "stock-aisle-filter"));

    // ==========================================================================
    // MODÜL 3: MODAL (POP-UP) YÖNETİM SİSTEMİ VE KART VERİ BAĞLAMA
    // ==========================================================================
    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.add("modal-active");
    }

    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.remove("modal-active");
    }

    // HTML içerisine eklediğimiz sınıfları dinleyerek Modalları doğrudan aç (Butonlar üzerinden)
    const openModalBtns = document.querySelectorAll(".js-open-modal");
    openModalBtns.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.stopPropagation();
            const target = this.getAttribute("data-modal");
            openModal(target);
        });
    });

    // Kapatma butonlarını dinle
    const closeModalsBtns = document.querySelectorAll(".js-close-modal, .modal-overlay");
    closeModalsBtns.forEach(btn => {
        btn.addEventListener("click", function (e) {
            // Overlay (arkaplan) için tıklandıysa ve kutu değilse kapat
            if (this.classList.contains("modal-overlay") && e.target !== this) {
                return;
            }

            // X (çarpı) butonu için kapatma
            if (this.classList.contains("js-close-modal")) {
                const target = this.getAttribute("data-target");
                closeModal(target);
                return;
            }

            // Overlay kapanışı
            const activeModals = document.querySelectorAll(".modal-overlay.modal-active");
            activeModals.forEach(modal => modal.classList.remove("modal-active"));
        });
    });

    const modalBoxes = document.querySelectorAll(".modal-box");
    modalBoxes.forEach(box => {
        box.addEventListener("click", e => e.stopPropagation());
    });

    // Özel İşlem: Kuryeye Git ve Modalı Aç
    const goToCourierBtns = document.querySelectorAll(".js-go-to-courier");
    goToCourierBtns.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.stopPropagation();
            switchPanel("m-couriers");
            openModal("courier-package-modal");
        });
    });

    // *YENİ*: Sipariş Kartı Verilerini Pop-up'a Aktarma ve Kartı Tıklanabilir Yapma
    const orderCards = document.querySelectorAll(".clickable-order-card");
    orderCards.forEach(card => {
        card.addEventListener("click", function (e) {
            // Eğer kartın içerisindeki bir butona tıklandıysa kartın kendi fonksiyonunu tetikleme
            if (e.target.closest('button')) {
                return;
            }

            // Kart üzerinden veri özniteliklerini (Data Attributes) topla
            const orderId = this.getAttribute("data-order-id");
            const orderDate = this.getAttribute("data-order-date");
            const orderTotal = this.getAttribute("data-order-total");
            const orderAddress = this.getAttribute("data-order-address");
            const orderStatus = this.getAttribute("data-order-status");
            const orderCustomer = this.getAttribute("data-order-customer");
            const orderPhone = this.getAttribute("data-order-phone");

            // Modal içerisindeki hedeflenen DOM elemanlarını seç
            const idEl = document.getElementById("popup-order-id");
            const dateEl = document.getElementById("popup-order-date");
            const totalEl = document.getElementById("popup-order-grand-total");
            const addressEl = document.getElementById("popup-order-address");
            const statusEl = document.getElementById("popup-order-status");
            const customerEl = document.getElementById("popup-order-customer");
            const phoneEl = document.getElementById("popup-order-phone");

            // Verileri DOM elemanlarına güvenli biçimde aktar
            if (idEl) idEl.textContent = "#" + orderId;
            if (dateEl) dateEl.textContent = orderDate;
            if (totalEl) totalEl.textContent = orderTotal + " TL";
            if (addressEl) addressEl.textContent = orderAddress;
            if (statusEl) statusEl.textContent = orderStatus;
            if (customerEl) customerEl.textContent = orderCustomer;
            if (phoneEl) phoneEl.textContent = orderPhone;

            // Modalı aç
            openModal("order-detail-modal");
        });
    });

    // ==========================================================================
    // MODÜL 4: FORM GÖNDERİM YAKALAYICILAR
    // ==========================================================================
    const stockForms = document.querySelectorAll(".js-stock-update-form");
    stockForms.forEach(form => {
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            // Burada backend API fetch işlemi yapılabilir.
            alert("Stok güncellendi!");
        });
    });

});