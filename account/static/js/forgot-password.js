window.addEventListener("pageshow", function (event) {
    if (event.persisted) {
        window.location.reload();
    }
});

document.addEventListener("DOMContentLoaded", function () {

    const forgotForm = document.getElementById("forgotForm");
    const loader = document.getElementById("page-loader");

    function showLoader() {
        if (!loader) return;

        loader.style.display = "flex";

        requestAnimationFrame(() => {
            loader.style.opacity = "1";
        });
    }

    function hideLoader() {
        if (!loader) return;

        loader.style.opacity = "0";

        setTimeout(() => {
            loader.style.display = "none";
        }, 200);
    }

    if (forgotForm) {
        forgotForm.addEventListener("submit", function () {
            showLoader();
        });
    }

    window.addEventListener("pageshow", function () {
        hideLoader();
    });
});