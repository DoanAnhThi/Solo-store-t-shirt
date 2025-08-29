// Quick test script for minicart functionality
(function() {
  console.log('🚀 Quick Test Started');
  
  function testElements() {
    const mini = document.querySelector('.mini-cart');
    const backdrop = document.querySelector('.mini-cart__backdrop');
    const toggleBtn = document.querySelector('[data-toggle-bag]');
    
    console.log('📋 Element Check:', {
      minicart: !!mini,
      backdrop: !!backdrop,
      toggleButton: !!toggleBtn
    });
    
    return {mini, backdrop, toggleBtn};
  }
  
  function testToggle() {
    const {mini, toggleBtn} = testElements();
    if (!mini || !toggleBtn) {
      console.log('❌ Missing elements for toggle test');
      return;
    }
    
    console.log('🔄 Testing toggle...');
    toggleBtn.click();
    
    setTimeout(() => {
      const isOpen = mini.classList.contains('is-open');
      console.log(isOpen ? '✅ Toggle works' : '❌ Toggle failed');
      
      if (isOpen) {
        // Test close with X button
        const closeBtn = document.querySelector('.mini-cart__close');
        if (closeBtn) {
          setTimeout(() => {
            closeBtn.click();
            setTimeout(() => {
              const isClosed = !mini.classList.contains('is-open');
              console.log(isClosed ? '✅ Close button works' : '❌ Close button failed');
            }, 100);
          }, 500);
        }
      }
    }, 200);
  }
  
  // Run tests after page is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      setTimeout(testToggle, 2000);
    });
  } else {
    setTimeout(testToggle, 2000);
  }
  
  // Test backdrop click (manual trigger)
  window.testBackdrop = function() {
    const {mini, backdrop} = testElements();
    if (!mini || !backdrop) {
      console.log('❌ Missing elements for backdrop test');
      return;
    }
    
    // First open if closed
    if (!mini.classList.contains('is-open')) {
      const toggleBtn = document.querySelector('[data-toggle-bag]');
      if (toggleBtn) toggleBtn.click();
      
      setTimeout(() => {
        backdrop.click();
        setTimeout(() => {
          const isClosed = !mini.classList.contains('is-open');
          console.log(isClosed ? '✅ Backdrop click works' : '❌ Backdrop click failed');
        }, 100);
      }, 300);
    } else {
      backdrop.click();
      setTimeout(() => {
        const isClosed = !mini.classList.contains('is-open');
        console.log(isClosed ? '✅ Backdrop click works' : '❌ Backdrop click failed');
      }, 100);
    }
  };
  
  console.log('💡 Run window.testBackdrop() to test backdrop click manually');
})();
