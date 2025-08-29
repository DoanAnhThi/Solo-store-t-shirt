// Tạo sự kiện giả lập PayPal thanh toán thành công
document.getElementById("createOrderBtn").addEventListener("click", async () => {
    try {
      console.log("🔄 Giả lập PayPal thanh toán thành công...");

      // Kiểm tra PayPal integration đã sẵn sàng chưa
      if (!window.paypalIntegration) {
        throw new Error("PayPal integration chưa được tải. Vui lòng đợi trang load xong.");
      }

      // Kiểm tra method simulatePaymentSuccess có tồn tại không
      if (!window.paypalIntegration.simulatePaymentSuccess) {
        throw new Error("Method simulatePaymentSuccess không tìm thấy. Có thể cần reload trang.");
      }

      // Tạo fake PayPal order data
      const fakePayPalOrder = {
        id: "TEST_ORDER_" + Date.now(),
        purchase_units: [{
          payments: {
            captures: [{
              id: "TEST_CAPTURE_" + Date.now(),
              amount: { value: "25.00" }
            }]
          },
          amount: { value: "25.00" }
        }],
        payer: {
          email_address: "test@example.com",
          name: {
            given_name: "Test",
            surname: "User"
          }
        }
      };

      // Gọi PayPal integration để xử lý như thanh toán thật
      await window.paypalIntegration.simulatePaymentSuccess(fakePayPalOrder);

    } catch (err) {
      console.error("❌ Lỗi khi giả lập thanh toán:", err);
      alert("❌ Có lỗi khi giả lập thanh toán: " + err.message);
    }
  });
  