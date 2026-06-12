document.addEventListener('DOMContentLoaded', function () {
    // DOM Elemanlarının Seçimi
    const categoryButtons = document.querySelectorAll('.category-list .category-item');
    const productCards = document.querySelectorAll('.products-grid .product-card');
    const productsGrid = document.getElementById('productsGrid');
    const searchInput = document.getElementById('productSearch');
    const sortSelect = document.getElementById('productSort');
    const noProductsMatch = document.getElementById('noProductsMatch');

    let currentCategory = 'all';
    let searchQuery = '';
    let cart = [];

    // ==========================================
    // 1. DİNAMİK FİLTRELEME VE SIRALAMA LOJİĞİ
    // ==========================================
    function filterAndSortProducts() {
        let visibleCards = [];

        productCards.forEach(card => {
            const cardCategory = card.getAttribute('data-category');
            const cardName = card.getAttribute('data-name').toLowerCase();
            
            const matchesCategory = (currentCategory === 'all' || cardCategory === currentCategory);
            const matchesSearch = cardName.includes(searchQuery);

            if (matchesCategory && matchesSearch) {
                card.style.display = 'flex';
                visibleCards.push(card);
            } else {
                card.style.display = 'none';
            }
        });

        if (visibleCards.length === 0) {
            noProductsMatch.style.display = 'flex';
            productsGrid.style.display = 'none';
        } else {
            noProductsMatch.style.display = 'none';
            productsGrid.style.display = 'grid';
            
            const sortValue = sortSelect.value;
            if (sortValue === 'price-asc') {
                visibleCards.sort((a, b) => parseFloat(a.getAttribute('data-price')) - parseFloat(b.getAttribute('data-price')));
            } else if (sortValue === 'price-desc') {
                visibleCards.sort((a, b) => parseFloat(b.getAttribute('data-price')) - parseFloat(a.getAttribute('data-price')));
            }
            visibleCards.forEach(card => productsGrid.appendChild(card));
        }
    }

    categoryButtons.forEach(button => {
        button.addEventListener('click', function () {
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            currentCategory = this.getAttribute('data-category');
            filterAndSortProducts();
        });
    });

    searchInput.addEventListener('input', function () {
        searchQuery = this.value.toLowerCase().trim();
        filterAndSortProducts();
    });

    sortSelect.addEventListener('change', filterAndSortProducts);


    // ==========================================
    // 2. MODERN SÜREÇLİ SEPET SİSTEMİ
    // ==========================================
    const cartCard = document.querySelector('.modern-cart');
    const minPrice = parseFloat(cartCard.getAttribute('data-min-price')) || 0;

    const emptyCartState = document.getElementById('emptyCartState');
    const cartItemsWrapper = document.getElementById('cartItemsWrapper');
    const cartSummary = document.getElementById('cartSummary');
    const cartTotalPrice = document.getElementById('cartTotalPrice');
    const cartBadgeCount = document.getElementById('cartBadgeCount');
    
    const progressBarFill = document.getElementById('progressBarFill');
    const progressStatusText = document.getElementById('progressStatusText');
    const checkoutBtn = document.getElementById('checkoutBtn');

    function updateCartUI() {
        const totalQty = cart.reduce((acc, item) => acc + item.qty, 0);
        cartBadgeCount.textContent = totalQty;

        if (cart.length === 0) {
            emptyCartState.style.display = 'flex';
            cartItemsWrapper.style.display = 'none';
            cartSummary.style.display = 'none';
            progressBarFill.style.width = '0%';
            progressStatusText.innerHTML = 'Minimum sipariş tutarına ulaşın!';
            checkoutBtn.disabled = true;
            return;
        }

        emptyCartState.style.display = 'none';
        cartItemsWrapper.style.display = 'flex';
        cartSummary.style.display = 'block';

        cartItemsWrapper.innerHTML = '';
        let total = 0;

        cart.forEach(item => {
            const itemTotal = item.price * item.qty;
            total += itemTotal;

            const row = document.createElement('div');
            row.className = 'cart-item-row';
            
            const imgContent = item.image 
                ? `<img src="${item.image}" alt="${item.name}">` 
                : `<i class="fa-solid fa-box"></i>`;

            row.innerHTML = `
                <div class="cart-item-img-slot">${imgContent}</div>
                <div class="cart-item-info">
                    <span class="cart-item-name">${item.name}</span>
                    <span class="cart-item-price-meta">${itemTotal.toFixed(2)} TL</span>
                </div>
                <div class="cart-item-actions">
                    <button type="button" class="cart-qty-btn minus-btn" data-id="${item.id}">-</button>
                    <span class="cart-item-qty">${item.qty}</span>
                    <button type="button" class="cart-qty-btn plus-btn" data-id="${item.id}">+</button>
                </div>
                <button type="button" class="cart-item-remove-btn" data-id="${item.id}">
                    <i class="fa-regular fa-trash-can"></i>
                </button>
            `;
            cartItemsWrapper.appendChild(row);
        });

        cartTotalPrice.textContent = `${total.toFixed(2)} TL`;

        // Progress Bar & Minimum Sipariş Kilidi Kontrolü
        if (minPrice > 0) {
            const percentage = Math.min((total / minPrice) * 100, 100);
            progressBarFill.style.width = `${percentage}%`;

            if (total >= minPrice) {
                progressStatusText.innerHTML = `<span style="color: #7A8450; font-weight: 600;"><i class="fa-solid fa-circle-check"></i> Minimum tutara ulaşıldı!</span>`;
                checkoutBtn.disabled = false;
            } else {
                const remaining = minPrice - total;
                progressStatusText.innerHTML = `Sepete <strong>${remaining.toFixed(2)} TL</strong> değerinde ürün daha ekleyin.`;
                checkoutBtn.disabled = true;
            }
        } else {
            progressBarFill.style.width = '100%';
            checkoutBtn.disabled = false;
        }
    }

    // Tıklama Olayları Yakalama (Event Delegation)
    document.addEventListener('click', function (e) {
        // Grid İçinden Ürün Ekleme
        if (e.target.classList.contains('add-to-cart-btn') || e.target.closest('.add-to-cart-btn')) {
            const btn = e.target.classList.contains('add-to-cart-btn') ? e.target : e.target.closest('.add-to-cart-btn');
            const id = btn.getAttribute('data-id');
            const name = btn.getAttribute('data-name');
            const price = parseFloat(btn.getAttribute('data-price'));
            const image = btn.getAttribute('data-image');

            const existingItem = cart.find(item => item.id === id);

            if (existingItem) {
                existingItem.qty++;
            } else {
                cart.push({ id, name, price, image, qty: 1 });
            }
            updateCartUI();
        }

        // Sepette Miktar Artırma (+)
        if (e.target.classList.contains('plus-btn')) {
            const id = e.target.getAttribute('data-id');
            const item = cart.find(item => item.id === id);
            if (item) item.qty++;
            updateCartUI();
        }

        // Sepette Miktar Azaltma (-)
        if (e.target.classList.contains('minus-btn')) {
            const id = e.target.getAttribute('data-id');
            const itemIndex = cart.findIndex(item => item.id === id);
            if (itemIndex > -1) {
                cart[itemIndex].qty--;
                if (cart[itemIndex].qty <= 0) {
                    cart.splice(itemIndex, 1);
                }
            }
            updateCartUI();
        }

        // Sepetten Ürünü Tamamen Silme (Çöp Sepeti)
        if (e.target.classList.contains('cart-item-remove-btn') || e.target.closest('.cart-item-remove-btn')) {
            const btn = e.target.classList.contains('cart-item-remove-btn') ? e.target : e.target.closest('.cart-item-remove-btn');
            const id = btn.getAttribute('data-id');
            const itemIndex = cart.findIndex(item => item.id === id);
            if (itemIndex > -1) {
                cart.splice(itemIndex, 1);
            }
            updateCartUI();
        }
    });
});