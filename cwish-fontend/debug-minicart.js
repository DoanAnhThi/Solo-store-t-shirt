// Debug script for minicart issues
(function() {
    console.log('=== MINICART DEBUG START ===');
    
    function log(message, data = null) {
        const timestamp = new Date().toLocaleTimeString();
        console.log(`[${timestamp}] ${message}`, data || '');
    }
    
    function checkElements() {
        const elements = {
            'Mini-cart': document.querySelector('.mini-cart'),
            'Backdrop': document.querySelector('.mini-cart__backdrop'),
            'Toggle button': document.querySelector('[data-toggle-bag]'),
            'Minicart hook': document.querySelector('[data-include="minicart"]'),
            'Header hook': document.querySelector('[data-include="header"]'),
            'Footer hook': document.querySelector('[data-include="footer"]')
        };
        
        log('=== ELEMENTS CHECK ===');
        Object.entries(elements).forEach(([name, element]) => {
            if (element) {
                log(`✓ ${name}: Found`, {
                    tagName: element.tagName,
                    className: element.className,
                    innerHTML: element.innerHTML.substring(0, 100) + '...'
                });
            } else {
                log(`✗ ${name}: Not found`);
            }
        });
        
        return elements;
    }
    
    function checkScripts() {
        log('=== SCRIPTS CHECK ===');
        
        const scripts = [
            'include.js',
            'local-fixes.js',
            'cart-manager.js'
        ];
        
        scripts.forEach(script => {
            const scriptElement = document.querySelector(`script[src*="${script}"]`);
            if (scriptElement) {
                log(`✓ ${script}: Loaded`);
            } else {
                log(`✗ ${script}: Not loaded`);
            }
        });
        
        // Check global functions
        log('Global functions:', {
            'window.loadPartial': typeof window.loadPartial,
            'window.miniCartToggle': typeof window.miniCartToggle,
            'window.CartManager': typeof window.CartManager
        });
    }
    
    function checkMinicartState() {
        log('=== MINICART STATE CHECK ===');
        
        const mini = document.querySelector('.mini-cart');
        const backdrop = document.querySelector('.mini-cart__backdrop');
        
        if (mini) {
            log('Mini-cart classes:', mini.className);
            log('Mini-cart styles:', {
                position: getComputedStyle(mini).position,
                right: getComputedStyle(mini).right,
                zIndex: getComputedStyle(mini).zIndex
            });
        }
        
        if (backdrop) {
            log('Backdrop classes:', backdrop.className);
            log('Backdrop styles:', {
                position: getComputedStyle(backdrop).position,
                opacity: getComputedStyle(backdrop).opacity,
                visibility: getComputedStyle(backdrop).visibility
            });
        }
    }
    
    function forceLoadMinicart() {
        log('=== FORCE LOADING MINICART ===');
        
        const minicartHook = document.querySelector('[data-include="minicart"]');
        
        if (!minicartHook) {
            log('Creating minicart hook...');
            const newHook = document.createElement('div');
            newHook.setAttribute('data-include', 'minicart');
            document.body.appendChild(newHook);
            log('Minicart hook created');
        }
        
        if (window.loadPartial) {
            log('Using window.loadPartial to load minicart...');
            const hook = document.querySelector('[data-include="minicart"]');
            window.loadPartial(hook, './partials/minicart.html').then(function() {
                log('Minicart loaded successfully via loadPartial');
                document.dispatchEvent(new Event('minicartLoaded'));
                setTimeout(checkElements, 500);
            }).catch(function(error) {
                log('Error loading minicart via loadPartial:', error);
            });
        } else {
            log('window.loadPartial not available, trying fetch...');
            const hook = document.querySelector('[data-include="minicart"]');
            fetch('./partials/minicart.html')
                .then(response => response.text())
                .then(html => {
                    hook.innerHTML = html;
                    log('Minicart loaded successfully via fetch');
                    document.dispatchEvent(new Event('minicartLoaded'));
                    setTimeout(checkElements, 500);
                })
                .catch(error => {
                    log('Error loading minicart via fetch:', error);
                });
        }
    }
    
    function testMinicartToggle() {
        log('=== TESTING MINICART TOGGLE ===');
        
        if (window.miniCartToggle) {
            log('miniCartToggle available, testing open...');
            window.miniCartToggle.open();
            setTimeout(() => {
                checkMinicartState();
            }, 1000);
        } else {
            log('miniCartToggle not available');
        }
    }
    
    // Initial checks
    setTimeout(() => {
        checkElements();
        checkScripts();
        checkMinicartState();
    }, 1000);
    
    // Additional checks with delays
    setTimeout(() => {
        log('=== DELAYED CHECK 1 ===');
        checkElements();
    }, 3000);
    
    setTimeout(() => {
        log('=== DELAYED CHECK 2 ===');
        checkElements();
        if (!document.querySelector('.mini-cart')) {
            log('Minicart still not found, forcing load...');
            forceLoadMinicart();
        }
    }, 5000);
    
    // Listen for minicart loaded event
    document.addEventListener('minicartLoaded', function() {
        log('=== MINICART LOADED EVENT ===');
        setTimeout(() => {
            checkElements();
            checkMinicartState();
        }, 500);
    });
    
    // Expose debug functions globally
    window.debugMinicart = {
        checkElements,
        checkScripts,
        checkMinicartState,
        forceLoadMinicart,
        testMinicartToggle
    };
    
    log('=== MINICART DEBUG READY ===');
    log('Use window.debugMinicart.* to debug manually');
    
})();
