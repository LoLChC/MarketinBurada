document.addEventListener('DOMContentLoaded', function () {
    
    // 1. KULLANICI AŞAĞI KAYDIRDIĞINDA header'I ŞIKLAŞTIR
    const header = document.getElementById('mainHeader');
    
    window.addEventListener('scroll', function () {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // 2. SAYFA İÇİ BAĞLANTILAR İÇİN AKICI KAYDIRMA (SMOOTH SCROLL)
    const localLinks = document.querySelectorAll('a[href^="#"]');
    
    localLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // 3. MARKET KARTLARI İÇİN LAZY LOADING SİMÜLASYONU
    // Kartlar ekrana yaklaştıkça görünürlük efektini tetikler (Performans dostu)
    const marketCards = document.querySelectorAll('.market-card');
    
    const cardObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });

    marketCards.forEach(card => {
        // İlk yüklemede kartları hafif aşağıda ve şeffaf yapıyoruz (Efekt için)
        card.style.opacity = '0';
        card.style.transform = 'translateY(15px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        cardObserver.observe(card);
    });
});