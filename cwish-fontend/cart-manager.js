class CartManager {
    constructor() {
        this.apiBase = 'http://localhost:8000/api';
        this.cartData = null;
        this.bonusCartData = null;
        this.init();
    }

    async init() {
        // Kiểm tra xem user đã đăng nhập chưa
        const isLoggedIn = await this.checkAuthStatus();
        if (isLoggedIn) {
            await this.loadCart();
            await this.loadBonusCart();
            this.updateCartDisplay();
        } else {
            // Ngay cả khi chưa đăng nhập, vẫn cập nhật shipping threshold với 0 items
            this.updateShippingThreshold();
        }
    }

    async checkAuthStatus() {
        try {
            const response = await fetch(`${this.apiBase}/auth/me/`, {
                credentials: 'include'
            });
            const data = await response.json();
            return data.id !== null;
        } catch (error) {
            console.error('Error checking auth status:', error);
            return false;
        }
    }

    async loadCart() {
        try {
            const response = await fetch(`${this.apiBase}/cart/`, {
                credentials: 'include'
            });
            if (response.ok) {
                this.cartData = await response.json();
                return this.cartData;
            }
        } catch (error) {
            console.error('Error loading cart:', error);
        }
        return null;
    }

    async loadBonusCart() {
        try {
            const response = await fetch(`${this.apiBase}/bonus-cart/`, {
                credentials: 'include'
            });
            if (response.ok) {
                this.bonusCartData = await response.json();
                return this.bonusCartData;
            }
        } catch (error) {
            console.error('Error loading bonus cart:', error);
        }
        return null;
    }

    async addToCart(quantity = 1) {
        try {
            const response = await fetch(`${this.apiBase}/cart/add_to_cart/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'include',
                body: JSON.stringify({ quantity: quantity })
            });

            if (response.ok) {
                this.cartData = await response.json();
                this.updateCartDisplay();
                this.showNotification('Product added to cart successfully!', 'success');
                return true;
            } else {
                const error = await response.json();
                this.showNotification(`Error: ${error.error || 'Failed to add to cart'}`, 'error');
                return false;
            }
        } catch (error) {
            console.error('Error adding to cart:', error);
            this.showNotification('Network error. Please try again.', 'error');
            return false;
        }
    }

    async addBonusToCart(quantity = 1) {
        try {
            const response = await fetch(`${this.apiBase}/bonus-cart/add_to_cart/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'include',
                body: JSON.stringify({ quantity: quantity })
            });

            if (response.ok) {
                this.bonusCartData = await response.json();
                console.log('Bonus cart updated:', this.bonusCartData);
                
                // Cập nhật display để hiển thị bonus product mới
                this.updateCartDisplay();
                this.showNotification('Bonus product added to cart successfully!', 'success');
                return true;
            } else {
                const error = await response.json();
                this.showNotification(`Error: ${error.error || 'Failed to add bonus to cart'}`, 'error');
                return false;
            }
        } catch (error) {
            console.error('Error adding bonus to cart:', error);
            this.showNotification('Network error. Please try again.', 'error');
            return false;
        }
    }

    async updateCartQuantity(quantity) {
        try {
            const response = await fetch(`${this.apiBase}/cart/update_quantity/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'include',
                body: JSON.stringify({ quantity: quantity })
            });

            if (response.ok) {
                this.cartData = await response.json();
                this.updateCartDisplay();
                this.showNotification('Cart updated successfully!', 'success');
                return true;
            } else {
                const error = await response.json();
                this.showNotification(`Error: ${error.error || 'Failed to update cart'}`, 'error');
                return false;
            }
        } catch (error) {
            console.error('Error updating cart:', error);
            this.showNotification('Network error. Please try again.', 'error');
            return false;
        }
    }

    async updateBonusCartQuantity(quantity) {
        try {
            const response = await fetch(`${this.apiBase}/bonus-cart/update_quantity/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'include',
                body: JSON.stringify({ quantity: quantity })
            });

            if (response.ok) {
                this.bonusCartData = await response.json();
                console.log('Bonus cart updated:', this.bonusCartData);
                
                // Cập nhật display để hiển thị thay đổi
                this.updateCartDisplay();
                this.showNotification('Bonus cart updated successfully!', 'success');
                return true;
            } else {
                const error = await response.json();
                this.showNotification(`Error: ${error.error || 'Failed to update bonus cart'}`, 'error');
                return false;
            }
        } catch (error) {
            console.error('Error updating bonus cart:', error);
            this.showNotification('Network error. Please try again.', 'error');
            return false;
        }
    }

    async clearCart() {
        try {
            const response = await fetch(`${this.apiBase}/cart/clear_cart/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'include'
            });

            if (response.ok) {
                this.cartData = { items: [], total_amount: 0, item_count: 0 };
                this.updateCartDisplay();
                this.showNotification('Cart cleared successfully!', 'success');
                return true;
            }
        } catch (error) {
            console.error('Error clearing cart:', error);
            this.showNotification('Network error. Please try again.', 'error');
        }
        return false;
    }

    async clearBonusCart() {
        try {
            const response = await fetch(`${this.apiBase}/bonus-cart/clear_cart/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'include'
            });

            if (response.ok) {
                this.bonusCartData = { items: [], total_amount: 0, item_count: 0 };
                this.updateCartDisplay();
                this.showNotification('Bonus cart cleared successfully!', 'success');
                return true;
            }
        } catch (error) {
            console.error('Error clearing bonus cart:', error);
            this.showNotification('Network error. Please try again.', 'error');
        }
        return false;
    }

    updateCartDisplay() {
        if (!this.cartData) return;

        // Lưu cart data vào sessionStorage để checkout page có thể sử dụng
        sessionStorage.setItem('cartData', JSON.stringify(this.cartData));

        // Cập nhật số lượng trong mini-cart
        const cartQuantity = document.querySelector('.cart__item__qty .quantity-display');
        if (cartQuantity) {
            cartQuantity.textContent = this.cartData.item_count || 0;
            console.log('Updated cart quantity display:', this.cartData.item_count);
        }

        // Cập nhật giá trong mini-cart
        const cartPrice = document.querySelector('.cart__item__price');
        if (cartPrice) {
            cartPrice.textContent = `$${(this.cartData.total_amount || 0).toFixed(2)}`;
            console.log('Updated cart price display:', this.cartData.total_amount);
        }

        // Cập nhật số lượng hiển thị trên header (nếu có)
        const cartCount = document.querySelector('.cart-count');
        if (cartCount) {
            cartCount.textContent = this.cartData.item_count || 0;
        }

        // Cập nhật cart count badge trên header
        const cartBadge = document.querySelector('.bag__item-alert');
        if (cartBadge) {
            if (this.cartData.item_count > 0) {
                cartBadge.classList.add('is-visible');
                cartBadge.textContent = this.cartData.item_count;
            } else {
                cartBadge.classList.remove('is-visible');
            }
        }

        // Cập nhật mini-cart content
        this.updateMiniCartContent();
        
        // Cập nhật shipping threshold
        this.updateShippingThreshold();
        
        // Cập nhật vị trí hiển thị bonus product
        this.updateBonusProductPosition();
    }

    updateShippingThreshold() {
        const shippingMessage = document.getElementById('shipping-message');
        const shippingProgress = document.getElementById('shipping-progress');
        
        if (!shippingMessage || !shippingProgress) return;
        
        const itemCount = this.cartData?.item_count || 0;
        
        if (itemCount >= 2) {
            // Từ 2 sản phẩm trở lên - đã unlock free shipping
            shippingMessage.textContent = "Congrats! You've unlocked FREE SHIPPING";
            shippingProgress.style.width = "100%";
        } else if (itemCount === 1) {
            // 1 sản phẩm - cần thêm 1 sản phẩm nữa
            shippingMessage.textContent = "Get 1 more item to unlock FREE SHIPPING on your order..";
            shippingProgress.style.width = "50%";
        } else {
            // 0 sản phẩm - cần thêm 2 sản phẩm
            shippingMessage.textContent = "Get 2 more items to unlock FREE SHIPPING on your order..";
            shippingProgress.style.width = "0%";
        }
    }

    updateBonusProductPosition() {
        const upsellBlock = document.querySelector('.product-page--upsell');
        const cartItemsContainer = document.querySelector('.cart__items');
        
        if (!upsellBlock || !cartItemsContainer) return;
        
        // Kiểm tra xem có bonus product trong cart không
        const hasBonusInCart = this.bonusCartData && this.bonusCartData.items && this.bonusCartData.items.length > 0;
        
        if (hasBonusInCart) {
            // Nếu đã có bonus trong cart, ẩn khối upsell
            upsellBlock.style.display = 'none';
        } else {
            // Nếu không có bonus trong cart, hiển thị khối upsell
            upsellBlock.style.display = 'block';
            
            // Cập nhật hình ảnh của khối upsell từ database
            this.updateBonusUpsellImage();
            
            // Nếu có sản phẩm chính trong giỏ hàng, hiển thị bonus product bên dưới
            if (this.cartData && this.cartData.items && this.cartData.items.length > 0) {
                // Di chuyển bonus product xuống dưới cart items
                cartItemsContainer.appendChild(upsellBlock);
            } else {
                // Nếu không có sản phẩm chính, giữ bonus product ở vị trí cũ
                const originalPosition = document.querySelector('.cart__body');
                if (originalPosition && !originalPosition.contains(upsellBlock)) {
                    originalPosition.appendChild(upsellBlock);
                }
            }
        }
    }

    updateBonusUpsellImage() {
        // Lấy thông tin bonus product từ API
        this.loadBonusProductInfo().then(bonusProduct => {
            if (bonusProduct && bonusProduct.image) {
                const upsellImage = document.getElementById('bonus-upsell-image');
                if (upsellImage) {
                    // Cập nhật src và alt
                    upsellImage.src = bonusProduct.image;
                    upsellImage.alt = bonusProduct.name;
                    console.log('Updated bonus upsell image:', bonusProduct.image);
                }
            }
        }).catch(error => {
            console.error('Error loading bonus product info:', error);
            // Sử dụng ảnh mặc định nếu có lỗi
            const upsellImage = document.getElementById('bonus-upsell-image');
            if (upsellImage) {
                upsellImage.src = './assets/nectar/nectar_files/The_Best_Hummingbird_Food_1_200x200.jpg';
                upsellImage.alt = 'Digital Design Package';
            }
        });
    }

    async loadBonusProductInfo() {
        try {
            const response = await fetch(`${this.apiBase}/bonus-product/`, {
                credentials: 'include'
            });
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Error loading bonus product info:', error);
        }
        return null;
    }

    updateMiniCartContent() {
        const miniCart = document.querySelector('.mini-cart');
        if (!miniCart || !this.cartData) return;

        const cartItemsContainer = miniCart.querySelector('.cart__items');
        const cartItemTemplate = miniCart.querySelector('.cart__item');
        const emptyCartMessage = miniCart.querySelector('.cart__empty');

        if (!cartItemsContainer || !cartItemTemplate) return;

        // Xóa tất cả cart items thực sự (không phải khối bonus)
        const existingItems = cartItemsContainer.querySelectorAll('.cart__item:not([style*="display: none"]):not(.cart__upsell .cart__item)');
        existingItems.forEach(item => item.remove());

        let hasAnyItems = false;

        // Hiển thị cart items từ sản phẩm chính
        if (this.cartData.items && this.cartData.items.length > 0) {
            hasAnyItems = true;
            this.cartData.items.forEach(item => {
                const cartItem = cartItemTemplate.cloneNode(true);
                cartItem.style.display = 'flex';
                
                // Cập nhật thông tin sản phẩm
                const productName = cartItem.querySelector('.cart__item__title');
                if (productName) {
                    productName.textContent = item.product.name;
                }

                const productImage = cartItem.querySelector('.cart__item__image img');
                if (productImage) {
                    if (item.product.image) {
                        productImage.src = item.product.image;
                    } else {
                        // Sử dụng ảnh mặc định nếu không có ảnh
                        productImage.src = './assets/nectar/nectar_files/The_Best_Hummingbird_Food_1_200x200.jpg';
                    }
                    productImage.alt = item.product.name;
                }

                // Cập nhật số lượng và giá
                const quantityDisplay = cartItem.querySelector('.quantity-display');
                if (quantityDisplay) {
                    quantityDisplay.textContent = item.quantity;
                    console.log('Updated quantity display:', item.quantity);
                }

                const priceElement = cartItem.querySelector('.cart__item__price');
                if (priceElement) {
                    priceElement.textContent = `$${item.total_price}`;
                }

                // Thêm event listeners cho nút + và -
                const qtyUpBtn = cartItem.querySelector('.qty-up');
                const qtyDownBtn = cartItem.querySelector('.qty-down');
                
                if (qtyUpBtn) {
                    qtyUpBtn.addEventListener('click', () => this.incrementQuantity());
                }
                
                if (qtyDownBtn) {
                    qtyDownBtn.addEventListener('click', () => this.decrementQuantity());
                }

                cartItemsContainer.appendChild(cartItem);
            });
        }

        // Hiển thị cart items từ sản phẩm bonus
        if (this.bonusCartData && this.bonusCartData.items && this.bonusCartData.items.length > 0) {
            hasAnyItems = true;
            this.bonusCartData.items.forEach(item => {
                const cartItem = cartItemTemplate.cloneNode(true);
                cartItem.style.display = 'flex';
                cartItem.classList.add('bonus-cart-item'); // Thêm class để phân biệt
                
                // Cập nhật thông tin sản phẩm bonus
                const productName = cartItem.querySelector('.cart__item__title');
                if (productName) {
                    productName.textContent = item.product.name;
                }

                const productImage = cartItem.querySelector('.cart__item__image img');
                if (productImage) {
                    if (item.product.image) {
                        productImage.src = item.product.image;
                    } else {
                        // Sử dụng ảnh mặc định cho bonus product
                        productImage.src = './assets/nectar/nectar_files/The_Best_Hummingbird_Food_1_200x200.jpg';
                    }
                    productImage.alt = item.product.name;
                }

                // Cập nhật số lượng và giá
                const quantityDisplay = cartItem.querySelector('.quantity-display');
                if (quantityDisplay) {
                    quantityDisplay.textContent = item.quantity;
                    console.log('Updated bonus quantity display:', item.quantity);
                }

                const priceElement = cartItem.querySelector('.cart__item__price');
                if (priceElement) {
                    priceElement.textContent = `$${item.total_price}`;
                }

                // Thêm event listeners cho nút + và - của bonus product
                const qtyUpBtn = cartItem.querySelector('.qty-up');
                const qtyDownBtn = cartItem.querySelector('.qty-down');
                
                if (qtyUpBtn) {
                    qtyUpBtn.addEventListener('click', () => this.incrementBonusQuantity());
                }
                
                if (qtyDownBtn) {
                    qtyDownBtn.addEventListener('click', () => this.decrementBonusQuantity());
                }

                cartItemsContainer.appendChild(cartItem);
            });
        }

        // Hiển thị/ẩn empty message
        if (emptyCartMessage) {
            if (hasAnyItems) {
                emptyCartMessage.style.display = 'none';
            } else {
                emptyCartMessage.style.display = 'block';
            }
        }

        // Cập nhật tổng giá trị (bao gồm cả sản phẩm chính và bonus)
        const subtotalElement = miniCart.querySelector('.mini-cart__subtotal__price .money');
        if (subtotalElement) {
            const mainTotal = this.cartData?.total_amount || 0;
            const bonusTotal = this.bonusCartData?.total_amount || 0;
            const totalAmount = mainTotal + bonusTotal;
            subtotalElement.textContent = `$${totalAmount.toFixed(2)}`;
        }
    }

    getCSRFToken() {
        // Lấy CSRF token từ cookie hoặc meta tag
        const csrfCookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
        if (csrfCookie) {
            return csrfCookie.split('=')[1];
        }
        
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) {
            return csrfMeta.getAttribute('content');
        }
        
        return '';
    }

    showNotification(message, type = 'info') {
        // Tạo notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style cho notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;

        // Màu sắc theo type
        if (type === 'success') {
            notification.style.backgroundColor = '#4CAF50';
        } else if (type === 'error') {
            notification.style.backgroundColor = '#f44336';
        } else {
            notification.style.backgroundColor = '#2196F3';
        }

        // Thêm CSS animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);

        // Thêm vào DOM
        document.body.appendChild(notification);

        // Tự động xóa sau 3 giây
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Method để xử lý nút + trong mini-cart
    async incrementQuantity() {
        if (!this.cartData || !this.cartData.items.length) return;
        
        const currentQuantity = this.cartData.items[0].quantity;
        await this.updateCartQuantity(currentQuantity + 1);
    }

    // Method để xử lý nút - trong mini-cart
    async decrementQuantity() {
        if (!this.cartData || !this.cartData.items.length) return;
        
        const currentQuantity = this.cartData.items[0].quantity;
        if (currentQuantity > 1) {
            await this.updateCartQuantity(currentQuantity - 1);
        } else {
            // Nếu số lượng = 1, giảm xuống 0 sẽ xóa sản phẩm
            await this.updateCartQuantity(0);
        }
    }

    // Method để xử lý nút + trong bonus cart
    async incrementBonusQuantity() {
        if (!this.bonusCartData || !this.bonusCartData.items.length) return;
        
        const currentQuantity = this.bonusCartData.items[0].quantity;
        await this.updateBonusCartQuantity(currentQuantity + 1);
    }

    // Method để xử lý nút - trong bonus cart
    async decrementBonusQuantity() {
        if (!this.bonusCartData || !this.bonusCartData.items.length) return;
        
        const currentQuantity = this.bonusCartData.items[0].quantity;
        if (currentQuantity > 1) {
            await this.updateBonusCartQuantity(currentQuantity - 1);
        } else {
            // Nếu số lượng = 1, giảm xuống 0 sẽ xóa sản phẩm
            await this.updateBonusCartQuantity(0);
        }
    }
}

// Khởi tạo CartManager khi DOM load xong
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing CartManager...');
    
    // Khởi tạo CartManager ngay lập tức
    window.cartManager = new CartManager();
    
    // Xử lý nút Add to Cart cho sản phẩm chính
    const addToCartBtn = document.querySelector('.add-to-cart:not(#add-bonus-to-cart)');
    console.log('Found Add to Cart button:', addToCartBtn);
    
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            console.log('Add to Cart button clicked!');

            try {
                // Kiểm tra radio button quantity nào được chọn
                const selectedQuantity = document.querySelector('input[name="quantity"]:checked');
                console.log('Selected quantity radio:', selectedQuantity);

                if (selectedQuantity) {
                    const quantityValue = selectedQuantity.value;
                    console.log('Selected quantity value:', quantityValue);

                    // Xác định hành động dựa trên quantity được chọn
                    if (selectedQuantity.id === 'quantity1') {
                        // Quantity 1: Thêm 1 single product
                        console.log('Adding 1 single product to cart');
                        await window.cartManager.addToCart(1);
                    } else if (selectedQuantity.id === 'quantity2') {
                        // Quantity 2: Thêm 2 single products
                        console.log('Adding 2 single products to cart');
                        await window.cartManager.addToCart(2);
                    } else if (selectedQuantity.id === 'quantity3') {
                        // Quantity 3: Thêm 1 digital product (bonus product)
                        console.log('Adding 1 digital product to cart');
                        await window.cartManager.addBonusToCart(1);
                    } else {
                        // Fallback: thêm 1 single product
                        console.log('Unknown quantity selection, adding 1 single product as fallback');
                        await window.cartManager.addToCart(1);
                    }
                } else {
                    // Không có radio nào được chọn, fallback
                    console.log('No quantity selected, adding 1 single product as fallback');
                    await window.cartManager.addToCart(1);
                }
            } catch (error) {
                console.error('Error in Add to Cart click handler:', error);
            }
        });
        console.log('Event listener attached to Add to Cart button');
    } else {
        console.error('Add to Cart button not found!');
    }

    // Xử lý nút Add to Cart cho sản phẩm bonus
    const addBonusToCartBtn = document.getElementById('add-bonus-to-cart');
    console.log('Looking for bonus button with ID "add-bonus-to-cart":', addBonusToCartBtn);
    
    if (addBonusToCartBtn) {
        addBonusToCartBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            console.log('Add Bonus to Cart button clicked!');
            
            try {
                const quantity = 1; // Bonus product luôn thêm với số lượng 1
                await window.cartManager.addBonusToCart(quantity);
            } catch (error) {
                console.error('Error in Add Bonus to Cart click handler:', error);
            }
        });
        console.log('Event listener attached to Add Bonus to Cart button');
    } else {
        console.error('Add Bonus to Cart button not found!');
        // Thử tìm bằng class selector
        const bonusButtons = document.querySelectorAll('.add-to-cart');
        console.log('Found all add-to-cart buttons:', bonusButtons);
        bonusButtons.forEach((btn, index) => {
            console.log(`Button ${index}:`, btn.id, btn.textContent);
        });
    }

    // Xử lý nút + và - trong mini-cart
    document.addEventListener('click', function(e) {
        // Kiểm tra xem có phải là nút + hoặc - không
        if (e.target.classList.contains('qty-up') || e.target.classList.contains('qty-down')) {
            e.preventDefault();
            
            // Kiểm tra xem nút này thuộc về cart item nào
            const cartItem = e.target.closest('.cart__item');
            if (cartItem) {
                if (cartItem.classList.contains('bonus-cart-item')) {
                    // Đây là bonus product
                    if (e.target.classList.contains('qty-up')) {
                        window.cartManager.incrementBonusQuantity();
                    } else {
                        window.cartManager.decrementBonusQuantity();
                    }
                } else {
                    // Đây là single product
                    if (e.target.classList.contains('qty-up')) {
                        window.cartManager.incrementQuantity();
                    } else {
                        window.cartManager.decrementQuantity();
                    }
                }
            }
        } else if (e.target.id === 'add-bonus-to-cart' || e.target.closest('#add-bonus-to-cart')) {
            e.preventDefault();
            console.log('Bonus button clicked via event delegation!');
            if (window.cartManager) {
                window.cartManager.addBonusToCart(1);
            }
        }
    });
});

// Thêm event listener để khởi tạo lại khi minicart được load
document.addEventListener('minicartLoaded', function() {
    if (window.cartManager) {
        window.cartManager.updateCartDisplay();
    }
});
