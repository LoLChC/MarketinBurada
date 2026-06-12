document.addEventListener('DOMContentLoaded', function () {
    initMarketPageAnimations();
    initMarketFilters();
});

function initMarketPageAnimations() {
    const marketCards = document.querySelectorAll('.market-page-card');
    if (marketCards.length === 0) return;

    const cardObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target); 
            }
        });
    }, { threshold: 0.02 });

    marketCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(25px)';
        card.style.transition = 'opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
        cardObserver.observe(card);
    });
}

function initMarketFilters() {
    const searchInput = document.getElementById('marketSearch');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const marketCards = document.querySelectorAll('.market-page-card');
    const noResults = document.getElementById('noResults');

    if (!searchInput || marketCards.length === 0) return;

    let activeFilter = 'all';
    let searchQuery = '';

    function filterMarkets() {
        let visibleCount = 0;

        marketCards.forEach(card => {
            const cardStatus = card.getAttribute('data-status');
            const cardName = card.getAttribute('data-name') || '';
            
            const matchesFilter = (activeFilter === 'all' || cardStatus === activeFilter);
            const matchesSearch = cardName.includes(searchQuery);

            if (matchesFilter && matchesSearch) {
                card.style.display = 'flex';
                setTimeout(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, 10);
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        if (visibleCount === 0) {
            noResults.style.display = 'block';
        } else {
            noResults.style.display = 'none';
        }
    }

    searchInput.addEventListener('input', function (e) {
        searchQuery = e.target.value.toLowerCase().trim();
        filterMarkets();
    });

    filterButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            filterButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            activeFilter = this.getAttribute('data-filter');
            filterMarkets();
        });
    });
}