// ==========================================================================
// 3. MAIN KODLARI (Kart Giriş Efektleri)
// ==========================================================================
function initMainAnimations() {
    const marketCards = document.querySelectorAll('.market-card');
    
    if (marketCards.length === 0) return;

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

    marketCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
        cardObserver.observe(card);
    });
}