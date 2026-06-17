/**
 * Marketin Burada - Merchant Paneli Yönetim Scripti
 */
document.addEventListener("DOMContentLoaded", function () {
    
    // Sekme Değiştirme ve F5 Koruma Mantığı (LocalStorage)
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
            localStorage.setItem("activeMerchantTab", targetId);
        }
    }

    // Kaldığı sekmeyi hatırla veya ilk sekmeyi aç
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
});