// PayPal Integration for T-shirt Store
class PayPalIntegration {
    constructor() {
        // *** Live Andreas account
        // this.paypalClientId = 'ENaMSdvm4ATz6XfV7r9r_5mGNf3EmHiiKDc2XcfLtJe8t21DAtzBuA86TuuZ5AXcwpFFdbYsCi0y85Kd'; // Thay thế bằng Client ID thực tế
        // *** Sandbox Thi account
        this.paypalClientId = 'AUTJCGZY2VvXmJIqCJ7kFO5DD_ESho40dm95S1XKJolyryezuz9XQJgFrKCDsR1YLUvWTItMq7B_jRVG'; // Thay thế bằng Client ID thực tế
        this.environment = 'sandbox'; // 'sandbox' cho testing, 'production' cho live
        this.isTestMode = false; // Flag để track test mode
        this.init();
    }

    init() {
        // Load PayPal SDK
        this.loadPayPalSDK();

        // PayPal Integration đã được khởi tạo
    }

    loadPayPalSDK() {
        // Kiểm tra xem PayPal SDK đã được load chưa
        if (window.paypal) {
            this.setupPayPal();
            return;
        }

        // Load PayPal SDK
        const script = document.createElement('script');
        script.src = `https://www.paypal.com/sdk/js?client-id=${this.paypalClientId}&currency=USD&intent=capture`;
        script.onload = () => {
            this.setupPayPal();
        };
        script.onerror = (error) => {
            console.error('Failed to load PayPal SDK:', error);
            this.showPayPalError();
        };
        document.head.appendChild(script);
    }

    setupPayPal() {
        if (!window.paypal) {
            console.error('PayPal SDK not available');
            return;
        }

        console.log('PayPal SDK loaded successfully');

        // Tạo PayPal buttons
        this.createPayPalButtons();
    }

    createPayPalButtons() {
        const paypalContainer = document.getElementById('paypal-button-container');
        if (!paypalContainer) {
            console.error('PayPal container not found');
            return;
        }

        console.log('Creating PayPal buttons...');
        paypalContainer.innerHTML = '';

        try {
            const buttons = paypal.Buttons({
                // Tạo order
                createOrder: (data, actions) => {
                    console.log('PayPal createOrder called with data:', data);
                    console.log('PayPal createOrder called with actions:', actions);
                    return this.createOrder(actions);
                },

                // Xử lý khi thanh toán thành công
                onApprove: (data, actions) => {
                    console.log('PayPal onApprove called with data:', data);
                    console.log('PayPal onApprove called with order ID:', data.orderID);
                    return this.handlePaymentSuccess(data, actions);
                },

                // Xử lý khi có lỗi
                onError: (err) => {
                    console.error('PayPal onError called:', err);
                    this.handlePaymentError(err);
                },

                // Xử lý khi người dùng hủy
                onCancel: (data) => {
                    console.log('PayPal onCancel called:', data);
                    this.handlePaymentCancel(data);
                }
            });

            if (buttons.isEligible()) {
                buttons.render(paypalContainer);
                console.log('PayPal buttons rendered successfully');
            } else {
                console.error('PayPal buttons not eligible for rendering');
                this.showPayPalError('PayPal buttons are not eligible for this transaction');
            }
        } catch (error) {
            console.error('Error rendering PayPal buttons:', error);
            this.showPayPalError();
        }
    }

    async createOrder(actions) {
        try {
            console.log('createOrder method called with actions:', actions);
            console.log('Actions object:', actions);
            console.log('Actions type:', typeof actions);

            // Lấy thông tin giỏ hàng
            const cartData = this.getCartData();
            if (!cartData || !cartData.items || cartData.items.length === 0) {
                throw new Error('No items in cart');
            }

            console.log('Cart data for order:', cartData);

            // Tạo danh sách items cho PayPal
            const items = cartData.items.map(item => ({
                name: item.product.name,
                quantity: item.quantity.toString(),
                unit_amount: {
                    currency_code: 'USD',
                    value: (parseFloat(item.total_price) / item.quantity).toFixed(2)
                }
            }));

            console.log('PayPal items:', items);

            // Tính toán tổng tiền
            const subtotal = parseFloat(cartData.total_amount);
            const shipping = 5.99;
            const tax = subtotal * 0.08;
            const total = subtotal + shipping + tax;

            console.log('Creating PayPal order with total:', total);

            // Tạo order
            const order = await actions.order.create({
                purchase_units: [{
                    amount: {
                        currency_code: 'USD',
                        value: total.toFixed(2),
                        breakdown: {
                            item_total: {
                                currency_code: 'USD',
                                value: subtotal.toFixed(2)
                            },
                            shipping: {
                                currency_code: 'USD',
                                value: shipping.toFixed(2)
                            },
                            tax_total: {
                                currency_code: 'USD',
                                value: tax.toFixed(2)
                            }
                        }
                    },
                    items: items,
                    shipping: {
                        name: {
                            full_name: this.getCustomerName()
                        },
                        address: {
                            address_line_1: document.getElementById('address')?.value || '',
                            admin_area_2: document.getElementById('city')?.value || '',
                            admin_area_1: document.getElementById('state')?.value || '',
                            postal_code: document.getElementById('zipCode')?.value || '',
                            country_code: document.getElementById('country')?.value || 'US'
                        }
                    }
                }],
                application_context: {
                    shipping_preference: 'SET_PROVIDED_ADDRESS',
                    user_action: 'PAY_NOW'
                }
            });

            console.log('PayPal order created successfully:', order);
            console.log('Order ID:', order);
            console.log('Order object type:', typeof order);

            // PayPal SDK returns order ID directly as string, not as object with id property
            if (typeof order === 'string') {
                console.log('Order ID is string:', order);
                if (!order || order.length === 0) {
                    console.error('PayPal order created but order ID is empty string:', order);
                    throw new Error('PayPal order created but order ID is empty');
                }
                return order;
            } else if (typeof order === 'object' && order.id) {
                console.log('Order ID from object:', order.id);
                return order.id;
            } else {
                console.error('PayPal order created but order format is unexpected:', order);
                console.log('Order object keys:', Object.keys(order || {}));
                throw new Error('PayPal order created but order format is unexpected');
            }

        } catch (error) {
            console.error('Error creating PayPal order:', error);
            // Hide loading state on error
            this.hideLoading();

            // Also hide loading from checkout page if available
            if (typeof hideLoading === 'function') {
                hideLoading();
            }

            throw error;
        }
    }

    async handlePaymentSuccess(data, actions) {
        console.log('✅ PayPal handlePaymentSuccess called');
        console.log('📋 Payment data received:', data);

        // Reset all messages to initial state
        this.resetMessages();

        try {
            // Capture payment
            console.log('🔄 Starting payment capture...');
            const order = await actions.order.capture();
            console.log('✅ Payment captured successfully:', order);

            // Hide loading state
            this.hideLoading();

            // Also hide loading from checkout page if available
            if (typeof hideLoading === 'function') {
                hideLoading();
            }

            // Xử lý thanh toán thành công
            console.log('🔄 Processing successful payment...');
            await this.processSuccessfulPayment(order);

            console.log('✅ processSuccessfulPayment completed, now showing success message...');

            // Hiển thị thông báo thành công
            console.log('🎉 Showing success message...');
            this.showSuccessMessage(order);

            console.log('✅ Payment flow completed successfully');
            return order;

        } catch (error) {
            console.error('❌ Error in handlePaymentSuccess:', error);
            console.error('❌ Error details:', {
                message: error.message,
                name: error.name,
                stack: error.stack
            });

            this.hideLoading();

            // Check if this is a client ID mismatch error
            if (error.message && error.message.includes('order')) {
                console.error('🚨 Possible Client ID mismatch! The Client ID in your code may not match the PayPal account you used to pay.');
                console.error('💡 Solution: Update the paypalClientId in paypal-integration.js to match your sandbox account.');
            }

            this.handlePaymentError(error);
        }
    }

    async processSuccessfulPayment(order) {
        console.log('🚀 processSuccessfulPayment STARTED');
        console.log('📋 PayPal order object:', order);

        try {
            // Lấy thông tin khách hàng
            const customerData = this.getCustomerData();

            console.log('📋 Customer data for backend:', customerData);
            console.log('✅ Customer data retrieved successfully');

            // Tạo order data theo đúng format mà backend mong đợi
            // Backend OrderCreateSerializer chỉ cần: email, first_name, last_name, address, city, country, postal_code, phone
            const orderData = {
                // Thông tin khách hàng (snake_case như backend mong đợi)
                email: customerData.email,
                first_name: customerData.firstName,  // camelCase → snake_case
                last_name: customerData.lastName,    // camelCase → snake_case
                address: customerData.address,
                city: customerData.city,
                country: customerData.country,
                postal_code: customerData.zipCode,   // zipCode → postal_code
                phone: customerData.phone
            };

            // Lưu thông tin PayPal riêng biệt để debug (backend không lưu)
            const paypalInfo = {
                paypalOrderId: order.id,
                paypalTransactionId: order.purchase_units[0].payments.captures[0].id,
                total: parseFloat(order.purchase_units[0].amount.value),
                paymentMethod: 'PayPal',
                paymentStatus: 'completed',
                orderDate: new Date().toISOString(),
                items: this.getCartData().items,
                paypalData: order
            };

            console.log('💳 PayPal transaction details:', paypalInfo);

            console.log('📤 Sending order data to backend:', orderData);

            // Gửi order đến backend
            console.log('🔄 Sending request to backend...');
            const backendResponse = await this.sendOrderToBackend(orderData, this.isTestMode, paypalInfo);
            console.log('✅ Backend response:', backendResponse);

            // Lưu order vào localStorage (bao gồm cả thông tin PayPal)
            this.saveOrderLocally({
                ...orderData,
                ...paypalInfo,
                backendResponse: backendResponse
            });

            // Xóa giỏ hàng
            this.clearCart();

            console.log('✅ processSuccessfulPayment COMPLETED SUCCESSFULLY');

        } catch (error) {
            console.error('❌ Error in processSuccessfulPayment:', error);
            console.error('❌ Error details:', {
                message: error.message,
                name: error.name,
                stack: error.stack
            });
            throw error;
        }
    }

    async sendOrderToBackend(orderData, isTestModeOverride = null, paypalInfo = null) {
        try {
            // Luôn dùng endpoint production để tạo order thật
            const isTestMode = false;
            const endpoint = 'http://localhost:8000/api/orders/';

            console.log(`📡 Using endpoint: ${endpoint} (test mode: ${isTestMode})`);

            console.log(`📤 Sending request to: ${endpoint}`);
            console.log(`📦 Request data:`, orderData);

            // Đảm bảo có CSRF cookie trước khi POST (Django yêu cầu khi dùng session)
            await this.ensureCsrfCookie();

            const csrfToken = this.getCsrfToken();

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Gửi CSRF token nếu có (phòng tránh 403 Forbidden)
                    'X-CSRFToken': csrfToken || ''
                },
                credentials: 'include',
                body: JSON.stringify(orderData)
            });

            console.log(`📥 Response status: ${response.status}`);
            console.log(`📄 Response headers:`, [...response.headers.entries()]);
            console.log(`📊 Response ok: ${response.ok}`);

            if (!response.ok) {
                const errorText = await response.text();
                console.error(`❌ Backend error response: ${errorText}`);
                throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
            }

            console.log('🔄 Parsing JSON response...');
            let responseData;
            try {
                const responseText = await response.text();
                console.log('📄 Raw response text:', responseText);
                responseData = JSON.parse(responseText);
                console.log('✅ JSON parsed successfully');
            } catch (parseError) {
                console.error('❌ JSON parse error:', parseError);
                throw new Error(`JSON parse error: ${parseError.message}`);
            }

            // Log status từ Shirtigo API ra console
            if (responseData.shirtigo_status) {
                console.log(`🎯 Shirtigo API Status: ${responseData.shirtigo_status}`);
                if (responseData.shirtigo_status === 500) {
                    console.log(`❌ Shirtigo API thất bại! (Đây là lỗi từ Shirtigo, không phải backend của chúng ta)`);
                } else if (responseData.shirtigo_status === 200 || responseData.shirtigo_status === 201) {
                    console.log(`✅ Shirtigo API thành công!`);
                }
            }

            console.log(`📄 Backend response data:`, responseData);

            // Log ra console để debug
            console.log('🎉 Payment process completed successfully!');
            console.log('📋 Order details:');
            if (paypalInfo) {
                console.log('   - PayPal Order ID:', paypalInfo.paypalOrderId);
                console.log('   - PayPal Transaction ID:', paypalInfo.paypalTransactionId);
                console.log('   - Total Amount:', paypalInfo.total);
            }
            // Customer log removed to avoid referencing undefined variable

            return responseData;

        } catch (error) {
            console.error('Backend not available, storing locally only');
            throw error;
        }
    }

    // -------- CSRF helpers for Django (session-based auth) --------
    getCsrfToken() {
        try {
            const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
            return match ? decodeURIComponent(match[1]) : null;
        } catch (e) {
            return null;
        }
    }

    async ensureCsrfCookie() {
        try {
            if (this.getCsrfToken()) {
                return;
            }
            // Endpoint có @ensure_csrf_cookie để set cookie
            await fetch('http://localhost:8000/api/auth/me/', {
                method: 'GET',
                credentials: 'include'
            });
        } catch (e) {
            console.warn('Could not ensure CSRF cookie:', e);
        }
    }

    saveOrderLocally(orderData) {
        try {
            const orders = JSON.parse(localStorage.getItem('orders') || '[]');
            orders.push(orderData);
            localStorage.setItem('orders', JSON.stringify(orders));
        } catch (error) {
            console.error('Error saving order locally:', error);
        }
    }

    // Method giả lập PayPal thanh toán thành công (dùng cho nút test)
    simulatePaymentSuccess = async (fakePayPalOrder) => {
        try {
            // Set test mode flag
            this.isTestMode = true;

            // Tạo fake actions object
            const fakeActions = {
                order: {
                    capture: async () => {
                        return fakePayPalOrder;
                    }
                }
            };

            // Tạo fake data
            const fakeData = {
                orderID: fakePayPalOrder.id
            };

            // Gọi handlePaymentSuccess như PayPal thật
            await this.handlePaymentSuccess(fakeData, fakeActions);

            alert("🎭 Đã giả lập thanh toán PayPal thành công! Đơn hàng đã được tạo và gửi đến Shirtigo.");

        } catch (error) {
            console.error("❌ Lỗi khi giả lập thanh toán:", error);
            alert("❌ Lỗi khi giả lập thanh toán: " + error.message);
            throw error;
        } finally {
            // Reset test mode flag
            this.isTestMode = false;
        }
    }



    clearCart() {
        try {
            sessionStorage.removeItem('cartData');
            localStorage.removeItem('cartData');
        } catch (error) {
            console.error('Error clearing cart:', error);
        }
    }

    getCartData() {
        try {
            const cartData = sessionStorage.getItem('cartData') || localStorage.getItem('cartData');

            if (cartData) {
                const parsedData = JSON.parse(cartData);
                return parsedData;
            } else {
                return null;
            }
        } catch (error) {
            console.error('Error getting cart data:', error);
            return null;
        }
    }

    getCustomerData() {
        const customerData = {
            firstName: document.getElementById('firstName')?.value || '',
            lastName: document.getElementById('lastName')?.value || '',
            email: document.getElementById('email')?.value || '',
            phone: document.getElementById('phone')?.value || '',
            address: document.getElementById('address')?.value || '',
            city: document.getElementById('city')?.value || '',
            state: document.getElementById('state')?.value || '',
            zipCode: document.getElementById('zipCode')?.value || '',
            country: document.getElementById('country')?.value || '',
            notes: document.getElementById('notes')?.value || ''
        };

        return customerData;
    }

    getCustomerName() {
        const firstName = document.getElementById('firstName')?.value || '';
        const lastName = document.getElementById('lastName')?.value || '';
        const fullName = `${firstName} ${lastName}`.trim();
        console.log('Customer name:', { firstName, lastName, fullName });
        return fullName || 'Customer';
    }

    handlePaymentError(error) {
        console.error('PayPal payment error:', error);
        console.error('Error details:', {
            message: error.message,
            stack: error.stack,
            name: error.name,
            type: typeof error
        });

        // Reset messages to clean state before showing error
        this.resetMessages();

        // Hide loading state
        this.hideLoading();

        // Provide more specific error messages based on error type
        let errorMessage = 'Payment failed. Please try again.';
        if (error.message) {
            if (error.message.includes('order id') || error.message.includes('order ID')) {
                errorMessage = 'Payment failed: Order processing issue. Please try again.';
            } else if (error.message.includes('validation')) {
                errorMessage = 'Payment failed: Please check your information and try again.';
            } else if (error.message.includes('network') || error.message.includes('timeout')) {
                errorMessage = 'Payment failed: Network issue. Please check your connection and try again.';
            } else if (error.message.includes('cart') || error.message.includes('items')) {
                errorMessage = 'Payment failed: Cart issue. Please refresh the page and try again.';
            } else if (error.message.includes('format') || error.message.includes('unexpected')) {
                errorMessage = 'Payment failed: System error. Please try again or contact support.';
            }
        }

        // Hiển thị thông báo lỗi
        this.showErrorMessage(errorMessage);

        // Enable lại nút thanh toán
        const paypalButton = document.getElementById('paypalButton');
        if (paypalButton) {
            paypalButton.disabled = false;
        }

        // Also hide loading from checkout page if available
        if (typeof hideLoading === 'function') {
            hideLoading();
        }
    }

    handlePaymentCancel(data) {
        console.log('Payment cancelled by user:', data);

        // Hide loading state
        this.hideLoading();

        // Hiển thị thông báo hủy
        this.showCancelMessage('Payment was cancelled.');

        // Enable lại nút thanh toán
        const paypalButton = document.getElementById('paypalButton');
        if (paypalButton) {
            paypalButton.disabled = false;
        }

        // Also hide loading from checkout page if available
        if (typeof hideLoading === 'function') {
            hideLoading();
        }
    }

    resetMessages() {
        console.log('🔄 Resetting all messages to initial state');

        // Hide error message
        const errorMessage = document.getElementById('errorMessage');
        if (errorMessage) {
            errorMessage.style.display = 'none';
        }

        // Hide success message (let showSuccessMessage handle displaying it)
        const successMessage = document.getElementById('successMessage');
        if (successMessage) {
            successMessage.style.display = 'none';
        }

        // Show checkout content
        const checkoutContent = document.querySelector('.checkout-content');
        if (checkoutContent) {
            checkoutContent.style.display = 'block';
        }

        console.log('✅ All messages reset');
    }

    showSuccessMessage(order) {
        console.log('🎉 showSuccessMessage CALLED with order:', order);

        // Ẩn error message trước nếu đang hiển thị
        const errorMessage = document.getElementById('errorMessage');
        if (errorMessage) {
            errorMessage.style.cssText = 'display: none !important;';
            errorMessage.style.display = 'none';
            console.log('✅ Error message hidden with force');
        }

        // Gọi function hideError từ HTML nếu có
        if (typeof hideError === 'function') {
            hideError();
            console.log('✅ hideError function called');
        }

        // Ẩn checkout content
        const checkoutContent = document.querySelector('.checkout-content');
        console.log('📋 Checkout content element:', checkoutContent);
        if (checkoutContent) {
            checkoutContent.style.display = 'none';
            console.log('✅ Checkout content hidden');
        }

        // Hiển thị success message
        const successMessage = document.getElementById('successMessage');
        console.log('📋 Success message element:', successMessage);
        if (successMessage) {
            // Force hiển thị success message với !important style
            successMessage.style.cssText = 'display: block !important;';
            successMessage.style.display = 'block';
            console.log('✅ Success message displayed with force');

            // Cập nhật order ID
            const orderIdElement = document.getElementById('orderId');
            if (orderIdElement) {
                orderIdElement.textContent = order.id;
            }
        }
    }

    showErrorMessage(message) {
        // Tạo notification
        this.showNotification(message, 'error');

        // Also show error in checkout page if available
        if (typeof showError === 'function') {
            showError(message);
        }
    }

    showCancelMessage(message) {
        // Tạo notification
        this.showNotification(message, 'warning');
    }

    showPayPalError(message = 'Failed to load PayPal. Please refresh the page.') {
        this.showNotification(message, 'error');
    }

    hideLoading() {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.style.display = 'none';
        }
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
        } else if (type === 'warning') {
            notification.style.backgroundColor = '#ff9800';
        } else {
            notification.style.backgroundColor = '#2196F3';
        }

        // Thêm CSS animation
        if (!document.querySelector('#notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }

        // Thêm vào DOM
        document.body.appendChild(notification);

        // Tự động xóa sau 5 giây
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Khởi tạo PayPal Integration khi DOM load xong
document.addEventListener('DOMContentLoaded', function () {
    // Chỉ khởi tạo PayPal nếu đang ở trang checkout
    if (window.location.pathname.includes('checkout.html')) {
        console.log('Initializing PayPal Integration...');
        window.paypalIntegration = new PayPalIntegration();
    }
});

// Export cho việc sử dụng trong các file khác
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PayPalIntegration;
}
