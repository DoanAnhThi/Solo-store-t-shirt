// Debug script for backdrop click issue
(function() {
  console.log('Debug backdrop script loaded');
  
  // Monitor all clicks on the page
  document.addEventListener('click', function(e) {
    console.log('🖱️ Click detected:', {
      target: e.target,
      tagName: e.target.tagName,
      className: e.target.className,
      classList: Array.from(e.target.classList || []),
      id: e.target.id,
      isBackdrop: e.target.classList?.contains('mini-cart__backdrop'),
      path: e.composedPath?.() || []
    });
    
    // Check if this is a backdrop-related element
    if (e.target.className && e.target.className.includes('backdrop')) {
      console.log('🎯 Backdrop-related click detected!');
    }
    
    // Check if click is inside minicart
    const miniCart = document.querySelector('.mini-cart');
    if (miniCart && miniCart.contains(e.target)) {
      console.log('📦 Click inside minicart');
    }
  }, true);
  
  // Monitor backdrop visibility changes
  function monitorBackdrop() {
    const backdrop = document.querySelector('.mini-cart__backdrop');
    if (backdrop) {
      const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
          if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
            console.log('🔄 Backdrop class changed:', {
              isVisible: backdrop.classList.contains('is-visible'),
              allClasses: Array.from(backdrop.classList)
            });
          }
        });
      });
      
      observer.observe(backdrop, { attributes: true });
      console.log('👀 Backdrop observer attached');
    } else {
      console.log('❌ No backdrop found to observe');
    }
  }
  
  // Wait for minicart to be available
  function waitForBackdrop(retries = 10) {
    if (retries <= 0) {
      console.log('❌ Backdrop not found after retries');
      return;
    }
    
    const backdrop = document.querySelector('.mini-cart__backdrop');
    if (backdrop) {
      console.log('✅ Backdrop found, setting up monitoring');
      monitorBackdrop();
    } else {
      console.log(`⏳ Waiting for backdrop... (${retries} retries left)`);
      setTimeout(() => waitForBackdrop(retries - 1), 500);
    }
  }
  
  // Start monitoring when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => waitForBackdrop());
  } else {
    waitForBackdrop();
  }
  
  // Listen for minicart loaded event
  document.addEventListener('minicartLoaded', function() {
    console.log('🎉 Minicart loaded event received');
    setTimeout(() => monitorBackdrop(), 100);
  });
})();
