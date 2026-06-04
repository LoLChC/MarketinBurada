// ==========================================================================
// 1. DOM HAZIR OLDUĞUNDA TETİKLENEN ANA TETİKLEYİCİ
// ==========================================================================
document.addEventListener('DOMContentLoaded', function () {
    
    initHeaderDynamics();
    initMainAnimations();

});

// ==========================================================================
// 2. HEADER DİNAMİKLERİ (Scroll Efekti)
// ==========================================================================
function initHeaderDynamics() {
    const header = document.getElementById('mainHeader');
    
    if (!header) return;

    window.addEventListener('scroll', function () {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
}

// ==========================================================================
// 3. MAIN KODLARI (Kart ve Bölüm Giriş Efektleri)
// ==========================================================================
function initMainAnimations() {
    // Hem anasayfa kartları hem de hakkımızda sayfasındaki yeni dikey kartlar dahil edildi
    const animElements = document.querySelectorAll('.market-card, .stat-card, .story-section, .value-card');
    
    if (animElements.length === 0) return;

    const cardObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target); 
            }
        });
    }, {
        threshold: 0.05
    });

    animElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
        cardObserver.observe(el);
    });
}