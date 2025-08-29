// Test script for nectar page
(function() {
  console.log('🧪 Nectar Test Script Loaded');
  
  function testNectar() {
    console.log('🔍 Testing nectar page...');
    
    // Check elements
    const mini = document.querySelector('.mini-cart');
    const backdrop = document.querySelector('.mini-cart__backdrop');
    const toggleBtn = document.querySelector('[data-toggle-bag]');
    
    console.log('📋 Elements found:', {
      minicart: !!mini,
      backdrop: !!backdrop,
      toggleButton: !!toggleBtn
    });
    
    if (mini && backdrop && toggleBtn) {
      console.log('✅ All elements found - nectar should work!');
      
      // Test toggle
      setTimeout(() => {
        console.log('🔄 Testing toggle...');
        toggleBtn.click();
        
        setTimeout(() => {
          const isOpen = mini.classList.contains('is-open');
          console.log(isOpen ? '✅ Toggle works!' : '❌ Toggle failed');
        }, 200);
      }, 1000);
      
    } else {
      console.log('❌ Missing elements - nectar needs fallback');
    }
  }
  
  // Run test after page loads
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', testNectar);
  } else {
    setTimeout(testNectar, 1000);
  }
})();
