(function(){
  function getEls(){
    return {
      mini: document.querySelector('.mini-cart'),
      backdrop: document.querySelector('.mini-cart__backdrop')
    };
  }

  function waitForMinicart(callback, maxRetries = 100, retryCount = 0) {
    var els = getEls();
    if (els.mini && els.backdrop) {
      callback(els);
    } else if (retryCount < maxRetries) {
      // Nếu đã thử nhiều lần mà chưa có, thử trigger load minicart manually
      if (retryCount === 20) {
        var minicartHook = document.querySelector('[data-include="minicart"]');
        if (minicartHook && !minicartHook.innerHTML.trim()) {
          // Minicart hook exists but empty, try to load it
          if (window.loadPartial) {
            window.loadPartial(minicartHook, './partials/minicart.html').then(function() {
              document.dispatchEvent(new Event('minicartLoaded'));
            });
          }
        }
      }
      
      // Nếu không có minicart hook, tạo một cái mới
      if (retryCount === 30) {
        var existingHook = document.querySelector('[data-include="minicart"]');
        if (!existingHook) {
          var newHook = document.createElement('div');
          newHook.setAttribute('data-include', 'minicart');
          document.body.appendChild(newHook);
          
          if (window.loadPartial) {
            window.loadPartial(newHook, './partials/minicart.html').then(function() {
              document.dispatchEvent(new Event('minicartLoaded'));
            });
          }
        }
      }
      
      setTimeout(function() {
        waitForMinicart(callback, maxRetries, retryCount + 1);
      }, 100);
    } else {
      console.warn('Minicart elements not found after maximum retries');
    }
  }

  function openCart(){
    waitForMinicart(function(els) {
      els.mini.classList.add('is-open');
      els.backdrop.classList.add('is-visible');
      document.body.style.overflow = 'hidden';
    });
  }

  function closeCart(){
    var els = getEls();
    if(els.mini) els.mini.classList.remove('is-open');
    if(els.backdrop) els.backdrop.classList.remove('is-visible');
    document.body.style.overflow = '';
  }

  function toggleCart() {
    var els = getEls();
    if (els.mini && els.mini.classList.contains('is-open')) {
      closeCart();
    } else {
      openCart();
    }
  }

  // Event delegation so it works with dynamically injected header
  document.addEventListener('click', function(e){
    var t = e.target && e.target.closest('[data-toggle-bag]');
    if(!t) return;
    e.preventDefault();
    toggleCart();
  });

  document.addEventListener('click', function(e){
    var els = getEls();
    if(els.backdrop && e.target === els.backdrop && els.backdrop.classList.contains('is-visible')){ 
      closeCart(); 
    }
  });

  document.addEventListener('keydown', function(e){ if(e.key === 'Escape') closeCart(); });

  // Listen for minicart loaded event to ensure elements are available
  document.addEventListener('minicartLoaded', function() {
    console.log('Minicart loaded, elements should be available');
  });

  // Expose functions for external use
  window.miniCartToggle = {
    open: openCart,
    close: closeCart,
    toggle: toggleCart
  };

  // Expose hook if needed by other scripts after partials load
  window.initMiniCartToggle = function(){ /* no-op; delegation handles it */ };
  
  // Additional fallback: Force check after DOM is fully ready
  document.addEventListener('DOMContentLoaded', function() {
    // Check multiple times with increasing delays for problematic pages like nectar
    var checkTimes = [500, 1000, 2000, 3000, 5000];
    
    function checkMinicart(attemptIndex) {
      if (attemptIndex >= checkTimes.length) {
        return;
      }
      
      setTimeout(function() {
        var els = getEls();
        
        if (!els.mini || !els.backdrop) {
          var minicartHook = document.querySelector('[data-include="minicart"]');
          
          if (minicartHook && window.loadPartial) {
            // Check if hook is empty
            if (!minicartHook.innerHTML.trim()) {
              window.loadPartial(minicartHook, './partials/minicart.html').then(function() {
                document.dispatchEvent(new Event('minicartLoaded'));
              });
            }
          } else if (!minicartHook) {
            // Create minicart hook if it doesn't exist
            var newHook = document.createElement('div');
            newHook.setAttribute('data-include', 'minicart');
            document.body.appendChild(newHook);
            
            if (window.loadPartial) {
              window.loadPartial(newHook, './partials/minicart.html').then(function() {
                document.dispatchEvent(new Event('minicartLoaded'));
              });
            }
          }
        }
        
        // Continue checking
        checkMinicart(attemptIndex + 1);
      }, checkTimes[attemptIndex]);
    }
    
    checkMinicart(0);
  });

  // Additional check when window loads
  window.addEventListener('load', function() {
    setTimeout(function() {
      var els = getEls();
      if (!els.mini || !els.backdrop) {
        console.log('Minicart still not available after window load, attempting to create...');
        
        var minicartHook = document.querySelector('[data-include="minicart"]');
        if (!minicartHook) {
          var newHook = document.createElement('div');
          newHook.setAttribute('data-include', 'minicart');
          document.body.appendChild(newHook);
          
          if (window.loadPartial) {
            window.loadPartial(newHook, './partials/minicart.html').then(function() {
              document.dispatchEvent(new Event('minicartLoaded'));
            });
          }
        }
      }
    }, 1000);
  });
})();
