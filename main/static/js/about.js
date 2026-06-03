function initMainAnimations() {
    // Seçicilere .stat-card ve .story-section yapılarını da ekledik
    const animElements = document.querySelectorAll('.market-card, .stat-card, .story-section');
    
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