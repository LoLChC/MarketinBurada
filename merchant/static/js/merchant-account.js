/**
 * ==========================================================================
 * Marketin Burada - Merchant Paneli Merkez JavaScript Dosyası
 * ==========================================================================
 * * Modüller:
 * 1. Menü ve Sekme Yönetimi (Tab Navigation & LocalStorage)
 * 2. Dinamik Filtreleme ve Yönlendirmeler
 * 3. Modal (Pop-up) Yönetim Sistemi (Açma / Kapama Mekanizmaları)
 * 4. Kart Veri Bağlama (Data Binding for Modals)
 * 5. Dosya Yükleme Ekranı İsim Güncellemeleri
 * ==========================================================================
 */

document.addEventListener("DOMContentLoaded", function () {

    // ==========================================================================
    // MODÜL 1: MENÜ VE SEKME YÖNETİMİ
    // ==========================================================================
    const menuButtons = document.querySelectorAll(".sidebar-menu .menu-item[data-target]");
    const contentPanels = document.querySelectorAll(".content-panel");

    /**
     * İlgili sekmeyi görünür kılar ve LocalStorage üzerine kaydeder.
     * @param {string} targetId - Hedef sekmenin DOM ID'si.
     */
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

    // Sidebar butonları için Event Listener
    menuButtons.forEach(button => {
        button.addEventListener("click", function () {
            const target = this.getAttribute("data-target");
            switchPanel(target);
        });
    });

    // ==========================================================================
    // MODÜL 2: DİNAMİK FİLTRELEME VE YÖNLENDİRMELER
    // ==========================================================================

    /**
     * Reyonlar Panelindeki "Ürünleri Göster" butonu mantığı.
     * Tıklandığında ürünler sekmesine atar ve select kutusunda o reyonu seçili hale getirir.
     */
    const showProductBtns = document.querySelectorAll(".btn-show-products");
    showProductBtns.forEach(btn => {
        btn.addEventListener("click", function () {
            const targetAisle = this.getAttribute("data-target-aisle");

            // Ürünlerim paneline geç
            switchPanel("m-products");

            // Select kutusunu manipüle et ve filtrelemeyi tetikle
            const productFilter = document.getElementById("product-aisle-filter");
            if (productFilter && targetAisle) {
                productFilter.value = targetAisle;
                productFilter.dispatchEvent(new Event('change'));
            }
        });
    });

    /**
     * Kartları Arama ve Seçim kutusuna göre filtreler.
     * @param {NodeList} cards - Filtrelenecek kart öğeleri.
     * @param {string} searchInputId - Arama çubuğu ID'si.
     * @param {string} filterSelectId - Select dropdown ID'si.
     */
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

    // Ürün Arama ve Filtre Dinleyicileri
    const productCards = document.querySelectorAll(".product-item-card");
    const productSearchInput = document.getElementById("product-search-input");
    const productAisleFilter = document.getElementById("product-aisle-filter");
    if (productSearchInput) productSearchInput.addEventListener("input", () => filterCards(productCards, "product-search-input", "product-aisle-filter"));
    if (productAisleFilter) productAisleFilter.addEventListener("change", () => filterCards(productCards, "product-search-input", "product-aisle-filter"));


    // ==========================================================================
    // MODÜL 3: MODAL (POP-UP) YÖNETİM SİSTEMİ
    // ==========================================================================

    /**
     * İlgili ID'ye sahip Modalı açar.
     * @param {string} modalId - Açılacak modalın DOM ID'si.
     */
    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.add("modal-active");
    }

    // Manuel Modal Açıcıları
    const openCourierModalBtn = document.getElementById("btn-open-courier-modal");
    const openProductModalBtn = document.getElementById("btn-open-product-modal");
    const openAisleModalBtn = document.getElementById("btn-open-aisle-modal");

    if (openCourierModalBtn) openCourierModalBtn.addEventListener("click", () => openModal("courier-modal"));
    if (openProductModalBtn) openProductModalBtn.addEventListener("click", () => openModal("product-modal"));
    if (openAisleModalBtn) openAisleModalBtn.addEventListener("click", () => openModal("aisle-modal"));

    // Modal Kapatma Mekanizması (Dış karartı veya çarpı işareti ile)
    const closeModalsBtns = document.querySelectorAll(".modal-close, .modal-overlay");
    const modalBoxes = document.querySelectorAll(".modal-box");

    closeModalsBtns.forEach(btn => {
        btn.addEventListener("click", function (e) {
            // Eğer karartıya tıklandıysa ancak tıklanan yer modalın kendisiyse kapatma.
            if (this.classList.contains("modal-overlay") && e.target !== this) {
                return;
            }
            const activeModals = document.querySelectorAll(".modal-overlay.modal-active");
            activeModals.forEach(modal => modal.classList.remove("modal-active"));
        });
    });

    // İçeriğe tıklandığında olayın dışarıya taşmasını (bubbling) engelle
    modalBoxes.forEach(box => {
        box.addEventListener("click", e => e.stopPropagation());
    });


    // ==========================================================================
    // MODÜL 4: KART VERİ BAĞLAMA (DATA BINDING)
    // ==========================================================================

    // 4.1 Sipariş Kartı Verilerini Pop-up'a Aktarma
    const orderCards = document.querySelectorAll(".clickable-order-card");
    orderCards.forEach(card => {
        card.addEventListener("click", function () {
            const orderId = this.getAttribute("data-order-id");
            const orderDate = this.getAttribute("data-order-date");
            const orderTotal = this.getAttribute("data-order-total");
            const orderAddress = this.getAttribute("data-order-address");
            const orderStatus = this.getAttribute("data-order-status");

            // Null-check ile güvenli DOM ataması (Grid Tasarımı)
            const idEl = document.getElementById("popup-order-id");
            const dateEl = document.getElementById("popup-order-date");
            const totalEl = document.getElementById("popup-order-grand-total");
            const addressEl = document.getElementById("popup-order-address");
            const statusEl = document.getElementById("popup-order-status");

            if (idEl) idEl.textContent = "#" + orderId;
            if (dateEl) dateEl.textContent = orderDate;
            if (totalEl) totalEl.textContent = orderTotal + " TL";
            if (addressEl) addressEl.textContent = orderAddress;
            if (statusEl) statusEl.textContent = orderStatus;

            openModal("order-detail-modal");
        });
    });

    // 4.2 Stok Kartı Verilerini Pop-up'a Aktarma
    stockCards.forEach(card => {
        card.addEventListener("click", function () {
            const productName = this.getAttribute("data-product-name");
            const titleEl = document.getElementById("popup-stock-title");

            if (titleEl && productName) titleEl.textContent = productName;
            openModal("stock-detail-modal");
        });
    });

    // 4.3 Kampanya Kartı Verilerini Pop-up'a Aktarma
    const campaignCards = document.querySelectorAll(".clickable-campaign");
    campaignCards.forEach(card => {
        card.addEventListener("click", function () {
            const title = this.getAttribute("data-camp-title");
            const code = this.getAttribute("data-camp-code");
            const usage = this.getAttribute("data-camp-usage");

            const titleEl = document.getElementById("popup-camp-title");
            const codeEl = document.getElementById("popup-camp-code");
            const usageEl = document.getElementById("popup-camp-usage");

            if (titleEl) titleEl.textContent = title;
            if (codeEl) codeEl.textContent = code;
            if (usageEl) usageEl.textContent = usage;

            openModal("campaign-detail-modal");
        });
    });

    // Kampanyayı Durdur Butonu Engellemesi
    const pauseCampaignBtns = document.querySelectorAll(".btn-pause-campaign");
    pauseCampaignBtns.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.stopPropagation();
            alert("Kampanya başarıyla durduruldu!");
        });
    });

    // 4.4 Kurye Düzenleme Formuna Veri Aktarımı
    const courierEditButtons = document.querySelectorAll(".btn-open-courier-edit-modal");
    courierEditButtons.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.stopPropagation();
            const card = this.closest(".courier-card");
            if (card) {
                const idEl = document.getElementById("edit-courier-id");
                const nameEl = document.getElementById("edit-courier-name");
                const phoneEl = document.getElementById("edit-courier-phone");
                const vehicleEl = document.getElementById("edit-courier-vehicle");
                const branchEl = document.getElementById("edit-courier-branch");

                if (idEl) idEl.value = card.getAttribute("data-courier-id") || "";
                if (nameEl) nameEl.value = card.getAttribute("data-courier-name") || "";
                if (phoneEl) phoneEl.value = card.getAttribute("data-courier-phone") || "";
                if (vehicleEl) vehicleEl.value = card.getAttribute("data-courier-vehicle") || "";
                if (branchEl) branchEl.value = card.getAttribute("data-courier-branch") || "";

                openModal("courier-edit-modal");
            }
        });
    });

    // 4.5 Ürün Düzenleme Formuna Veri Aktarımı
    const productEditButtons = document.querySelectorAll(".btn-open-product-edit-modal");
    productEditButtons.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.stopPropagation();
            const card = this.closest(".product-item-card");
            if (card) {
                const idEl = document.getElementById("edit-product-id");
                const nameEl = document.getElementById("edit-product-name");
                const priceEl = document.getElementById("edit-product-price");
                const aisleEl = document.getElementById("edit-product-category");
                const fileNameDisplay = document.getElementById("edit-file-name-display");

                if (idEl) idEl.value = card.getAttribute("data-product-id") || "";
                if (nameEl) nameEl.value = card.getAttribute("data-product-name") || "";
                if (priceEl) priceEl.value = card.getAttribute("data-product-price") || "";
                if (aisleEl) aisleEl.value = card.getAttribute("data-product-aisle") || "";

                // Form açıldığında görsel bilgisini sıfırla
                if (fileNameDisplay) fileNameDisplay.textContent = "Yeni Görsel Seç";

                openModal("product-edit-modal");
            }
        });
    });

    // ==========================================================================
    // MODÜL 5: DOSYA YÜKLEME EKRANI (INPUT TYPE=FILE)
    // ==========================================================================

    // Ürün Ekleme (Yeni) Resim İsim Catcher
    const addProductImageInput = document.getElementById("modal-product-image");
    const addProductFileName = document.getElementById("file-name-display");

    if (addProductImageInput && addProductFileName) {
        addProductImageInput.addEventListener("change", function () {
            if (this.files && this.files.length > 0) {
                addProductFileName.textContent = this.files[0].name;
            } else {
                addProductFileName.textContent = "Görsel Seç veya Sürükle";
            }
        });
    }

    // Ürün Düzenleme (Varolan) Resim İsim Catcher
    const editProductImageInput = document.getElementById("edit-product-image");
    const editProductFileName = document.getElementById("edit-file-name-display");

    if (editProductImageInput && editProductFileName) {
        editProductImageInput.addEventListener("change", function () {
            if (this.files && this.files.length > 0) {
                editProductFileName.textContent = this.files[0].name;
            } else {
                editProductFileName.textContent = "Yeni Görsel Seç";
            }
        });
    }

});