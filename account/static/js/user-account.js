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

        menuButtons.forEach(btn => btn.classList.remove("active"));
        contentPanels.forEach(panel => panel.classList.remove("active"));

        const targetPanel = document.getElementById(targetId);
        const targetButton = document.querySelector(`[data-target="${targetId}"]`);

        if (targetPanel && targetButton) {
            targetPanel.classList.add("active");
            targetButton.classList.add("active");
            localStorage.setItem("activeAccountTab", targetId);
        }
    }

    const savedTab = localStorage.getItem("activeAccountTab");
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
    // 2. Profil Fotoğrafı / Avatar Önizleme ve Değiştirme
    // ==========================================================================
    const avatarInput = document.getElementById("avatar-upload-input");
    const avatarPreview = document.getElementById("avatar-preview-img");
    const avatarPlaceholder = document.getElementById("avatar-placeholder-icon");

    if (avatarInput) {
        avatarInput.addEventListener("change", function (e) {
            const file = e.target.files[0];
            if (file) {
                if (!file.type.startsWith("image/")) {
                    alert("Lütfen geçerli bir resim dosyası seçiniz.");
                    return;
                }

                const reader = new FileReader();
                reader.onload = function (event) {
                    if (avatarPreview) {
                        avatarPreview.src = event.target.result;
                        avatarPreview.style.display = "block";
                    }
                    if (avatarPlaceholder) {
                        avatarPlaceholder.style.display = "none";
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // ==========================================================================
    // 3. Adres ve Kart Ekleme Modalları (Popup) Yönetimi - GARANTİLİ KAPATMA
    // ==========================================================================
    const openAddressModalBtn = document.getElementById("btn-open-address-modal");
    const openPaymentModalBtn = document.getElementById("btn-open-payment-modal");
    
    // Projedeki olası tüm kapatma buton sınıflarını (.close-modal, .btn-modal-close, .modal-close) kapsıyoruz
    const closeModalsBtns = document.querySelectorAll(".btn-modal-close, .close-modal, .modal-close, .modal-overlay");
    const modalBoxes = document.querySelectorAll(".modal-box");

    // Adres Modalı Aç
    if (openAddressModalBtn) {
        openAddressModalBtn.addEventListener("click", function () {
            const modal = document.getElementById("address-modal");
            if (modal) modal.classList.add("modal-active");
        });
    }

    // Kart Modalı Aç
    if (openPaymentModalBtn) {
        openPaymentModalBtn.addEventListener("click", function () {
            const modal = document.getElementById("payment-modal");
            if (modal) modal.classList.add("modal-active");
        });
    }

    // Modalları Kapatma Tetikleyicisi
    closeModalsBtns.forEach(btn => {
        btn.addEventListener("click", function (e) {
            // Eğer karartıya (.modal-overlay) tıklandıysa ama tıklanan alt element modal-box ise kapatma
            if (this.classList.contains("modal-overlay") && e.target !== this) {
                return;
            }
            // Aktif olan tüm modalları bul ve kapat
            const activeModals = document.querySelectorAll(".modal-overlay.modal-active");
            activeModals.forEach(modal => {
                modal.classList.remove("modal-active");
            });
        });
    });

    // Modal içeriğine tıklandığında dış karartı eventinin tetiklenmesini engelle
    modalBoxes.forEach(box => {
        box.addEventListener("click", function (e) {
            e.stopPropagation();
        });
    });

    // ==========================================================================
    // 4. KART NUMARASI: Biçimlendirme, Canlı Logo ve Doğrulama Kontrolü
    // ==========================================================================
    const cardNumberInput = document.getElementById("card-number");
    const cardIcon = document.getElementById("card-icon");
    const validationText = document.getElementById("card-validation-text");

    if (cardNumberInput && cardIcon && validationText) {
        cardNumberInput.addEventListener("input", function (e) {
            let cursorPosition = e.target.selectionStart;
            let value = e.target.value.replace(/\D/g, ""); 
            let formattedValue = "";

            for (let i = 0; i < value.length; i++) {
                if (i > 0 && i % 4 === 0) {
                    formattedValue += " ";
                }
                formattedValue += value[i];
            }
            e.target.value = formattedValue;

            if (cursorPosition < e.target.value.length && (e.target.value[cursorPosition - 1] === " ")) {
                e.target.setSelectionRange(cursorPosition + 1, cursorPosition + 1);
            }

            let rawNumber = formattedValue.replace(/\s/g, '');
            
            if (rawNumber.length === 0) {
                cardIcon.className = "card-status-icon";
                validationText.textContent = "";
                validationText.className = "card-validation-hint";
                return;
            }

            let cardType = "Bilinmeyen Kart";
            let cardClass = "fa-solid fa-credit-card";

            if (/^4/.test(rawNumber)) {
                cardType = "Visa";
                cardClass = "fa-brands fa-cc-visa text-visa";
            } else if (/^(5[1-5]|222[1-9]|22[3-9]|2[3-6]|27[0-1]|2720)/.test(rawNumber)) {
                cardType = "Mastercard";
                cardClass = "fa-brands fa-cc-mastercard text-mastercard";
            } else if (/^3[47]/.test(rawNumber)) {
                cardType = "American Express (Amex)";
                cardClass = "fa-brands fa-cc-amex text-amex";
            } else if (/^(9792|65)/.test(rawNumber)) {
                cardType = "Troy";
                cardClass = "fa-solid fa-credit-card text-troy";
            }

            cardIcon.className = "card-status-icon " + cardClass;

            let isValid = checkLuhn(rawNumber);
            let totalLength = rawNumber.length;

            if (totalLength < 15) {
                validationText.textContent = `Kart Türü: ${cardType} (Yazılıyor...)`;
                validationText.className = "card-validation-hint text-muted";
            } else if (totalLength === 15 || totalLength === 16) {
                if (isValid) {
                    validationText.textContent = `✓ Geçerli ${cardType} Kartı`;
                    validationText.className = "card-validation-hint text-success";
                } else {
                    validationText.textContent = `✗ Geçersiz ${cardType} Numarası (Algoritma Hatası)`;
                    validationText.className = "card-validation-hint text-danger";
                    cardIcon.className = "card-status-icon fa-solid fa-circle-xmark text-danger";
                }
            } else {
                validationText.textContent = "✗ Hata: Çok fazla hane girdiniz!";
                validationText.className = "card-validation-hint text-danger";
                cardIcon.className = "card-status-icon fa-solid fa-circle-xmark text-danger";
            }
        });
    }

    function checkLuhn(cardNo) {
        let nDigits = cardNo.length;
        let nSum = 0;
        let isSecond = false;
        for (let i = nDigits - 1; i >= 0; i--) {
            let d = cardNo.charCodeAt(i) - '0'.charCodeAt(0);
            if (isSecond == true) d = d * 2;
            nSum += parseInt(d / 10, 10);
            nSum += d % 10;
            isSecond = !isSecond;
        }
        return (nSum % 10 == 0);
    }

    // ==========================================================================
    // 5. SON KULLANMA TARİHİ: Kesin Giriş Engelleme Kuralları (AA/YY)
    // ==========================================================================
    const cardExpiryInput = document.getElementById("card-expiry");
    const expiryValidationText = document.getElementById("expiry-validation-text");

    if (cardExpiryInput && expiryValidationText) {
        cardExpiryInput.addEventListener("input", function (e) {
            let value = e.target.value.replace(/\D/g, ""); // Sadece rakamları yakala
            
            // Ay Giriş Kontrolü
            if (value.length >= 1) {
                let firstDigit = parseInt(value.substring(0, 1), 10);
                if (firstDigit > 1 && value.length === 1) {
                    value = "0" + value;
                }
            }
            if (value.length >= 2) {
                let month = parseInt(value.substring(0, 2), 10);
                if (month < 1 || month > 12) {
                    e.target.value = "";
                    expiryValidationText.textContent = "✗ Geçersiz Ay (01-12 arası olmalı)";
                    expiryValidationText.className = "card-validation-hint text-danger";
                    return;
                }
            }

            // Yıl Kontrolü ve Geçmiş Yılı Engelleme
            let currentDate = new Date();
            let currentYearShort = parseInt(currentDate.getFullYear().toString().substring(2, 4), 10);
            let currentMonth = currentDate.getMonth() + 1;

            if (value.length >= 4) {
                let inputYearShort = parseInt(value.substring(2, 4), 10);
                let month = parseInt(value.substring(0, 2), 10);

                if (inputYearShort < currentYearShort) {
                    value = value.substring(0, 2);
                    e.target.value = value.substring(0, 2) + "/";
                    expiryValidationText.textContent = "✗ Geçmiş bir yıl girmeyi denediniz!";
                    expiryValidationText.className = "card-validation-hint text-danger";
                    return;
                }
                
                if (inputYearShort === currentYearShort && month < currentMonth) {
                    expiryValidationText.textContent = "✗ Kartın kullanım süresi dolmuş!";
                    expiryValidationText.className = "card-validation-hint text-danger";
                } else if (inputYearShort > currentYearShort + 20) {
                    e.target.value = value.substring(0, 2) + "/";
                    expiryValidationText.textContent = "✗ Geçersiz uzak yıl girdiniz!";
                    expiryValidationText.className = "card-validation-hint text-danger";
                    return;
                } else {
                    expiryValidationText.textContent = "✓ Geçerli Tarih";
                    expiryValidationText.className = "card-validation-hint text-success";
                }
            }

            let formattedValue = "";
            if (value.length > 2) {
                formattedValue = value.substring(0, 2) + "/" + value.substring(2, 4);
            } else {
                formattedValue = value;
            }
            e.target.value = formattedValue;

            if (value.length === 0) {
                expiryValidationText.textContent = "";
                expiryValidationText.className = "card-validation-hint";
            } else if (value.length < 4 && expiryValidationText.textContent.indexOf("Geçersiz") === -1) {
                expiryValidationText.textContent = "Tarih yazılıyor (AA/YY)...";
                expiryValidationText.className = "card-validation-hint text-muted";
            }
        });
    }

    // ==========================================================================
    // 6. CVC / CVV ALANI: Password İçerisinde Sadece Sayı Girişi ve 3 Hane Sınırı
    // ==========================================================================
    const cardCvvInput = document.getElementById("card-cvv");
    const cvvValidationText = document.getElementById("cvv-validation-text");

    if (cardCvvInput && cvvValidationText) {
        cardCvvInput.addEventListener("input", function (e) {
            let cleanValue = e.target.value.replace(/\D/g, ""); 
            
            if (cleanValue.length > 3) {
                cleanValue = cleanValue.substring(0, 3);
            }
            e.target.value = cleanValue;

            if (cleanValue.length === 0) {
                cvvValidationText.textContent = "";
                cvvValidationText.className = "card-validation-hint";
            } else if (cleanValue.length === 3) {
                cvvValidationText.textContent = "✓ Güvenlik kodu tamam.";
                cvvValidationText.className = "card-validation-hint text-success";
            } else {
                cvvValidationText.textContent = "CVC kodu 3 haneli olmalıdır.";
                cvvValidationText.className = "card-validation-hint text-muted";
            }
        });
    }
});