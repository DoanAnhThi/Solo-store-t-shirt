(function () {
    function ready(f) { if (document.readyState !== 'loading') { f() } else { document.addEventListener('DOMContentLoaded', f) } }
    function runScripts(container){
        var scripts = container.querySelectorAll('script');
        scripts.forEach(function(oldScript){
            var s = document.createElement('script');
            // copy attributes
            for (var i = 0; i < oldScript.attributes.length; i++) {
                var attr = oldScript.attributes[i];
                s.setAttribute(attr.name, attr.value);
            }
            s.text = oldScript.text;
            oldScript.parentNode.replaceChild(s, oldScript);
        });
    }
    function load(el, path) {
        console.log('Loading partial:', path, 'into element:', el);
        return fetch(path).then(function(r){ 
            if (!r.ok) {
                throw new Error(`Failed to load ${path}: ${r.status} ${r.statusText}`);
            }
            return r.text(); 
        }).then(function(h){
            el.innerHTML = h;
            runScripts(el);
            console.log('Successfully loaded partial:', path);
            
            // ensure header/footer base styles are available if partial doesn't include them
            if(!document.querySelector('link[href*="theme.scss.css"]')){
                var link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = './assets/home/home_files/theme.scss.css';
                document.head.appendChild(link);
            }
            
            // After header loads, automatically load minicart
            if (el.getAttribute('data-include') === 'header') {
                console.log('Header loaded, now loading minicart...');
                loadMinicart();
            }
        }).catch(function(error){ 
            console.error('Error loading partial:', path, error);
            el.innerHTML = '<p style="color: red;">Error loading ' + path + '</p>'; 
        });
    }
    
    function loadMinicart() {
        console.log('loadMinicart called');
        var hook = document.querySelector('[data-include="minicart"]');
        console.log('Found minicart hook:', hook);
        
        if (hook) {
            console.log('Loading minicart into existing hook');
            load(hook, './partials/minicart.html').then(function() {
                console.log('Minicart loaded successfully');

                // Move minicart to body to prevent being trapped in header
                setTimeout(function() {
                    const minicart = document.querySelector('.mini-cart');
                    const backdrop = document.querySelector('.mini-cart__backdrop');

                    if (minicart && minicart.parentElement !== document.body) {
                        console.log('Moving minicart to body...');
                        document.body.appendChild(minicart);
                    }

                    if (backdrop && backdrop.parentElement !== document.body) {
                        console.log('Moving backdrop to body...');
                        document.body.appendChild(backdrop);
                    }

                    console.log('Minicart moved to body, dispatching event');
                    document.dispatchEvent(new Event('minicartLoaded'));
                }, 100);
            }).catch(function(error) {
                console.error('Error loading minicart:', error);
            });
        } else {
            console.log('No minicart hook found, creating new one directly in body');
            // Nếu không có minicart hook, tạo một cái mới trực tiếp trong body
            var newHook = document.createElement('div');
            newHook.setAttribute('data-include', 'minicart');
            newHook.style.position = 'fixed';
            newHook.style.top = '0';
            newHook.style.right = '0';
            newHook.style.zIndex = '9999';
            document.body.appendChild(newHook);

            console.log('Created new minicart hook in body:', newHook);
            load(newHook, './partials/minicart.html').then(function() {
                console.log('Minicart loaded into body hook, dispatching event');
                document.dispatchEvent(new Event('minicartLoaded'));
            }).catch(function(error) {
                console.error('Error loading minicart into body hook:', error);
            });
        }
    }
    
    // Expose load function globally for other scripts
    window.loadPartial = load;
    window.loadMinicart = loadMinicart;
    
    ready(function () {
        console.log('include.js ready, processing includes...');
        document.querySelectorAll('[data-include]').forEach(function (el) {
            var name = el.getAttribute('data-include');
            console.log('Processing include:', name, 'for element:', el);
            if (name === 'header') { load(el, './partials/header.html'); }
            if (name === 'footer') { load(el, './partials/footer.html'); }
            if (name === 'minicart') { load(el, './partials/minicart.html'); }
        });
        
        // Đảm bảo minicart được load sau khi tất cả partials đã load
        setTimeout(function() {
            console.log('Timeout check: ensuring minicart is loaded');
            var minicartHook = document.querySelector('[data-include="minicart"]');
            if (!minicartHook) {
                console.log('No minicart hook found after timeout, creating one');
                var newHook = document.createElement('div');
                newHook.setAttribute('data-include', 'minicart');
                newHook.style.position = 'fixed';
                newHook.style.top = '0';
                newHook.style.right = '0';
                newHook.style.zIndex = '9999';
                document.body.appendChild(newHook);
                
                load(newHook, './partials/minicart.html').then(function() {
                    console.log('Minicart loaded after timeout');

                    // Move minicart to body
                    setTimeout(function() {
                        const minicart = document.querySelector('.mini-cart');
                        const backdrop = document.querySelector('.mini-cart__backdrop');

                        if (minicart && minicart.parentElement !== document.body) {
                            console.log('Moving minicart to body after timeout...');
                            document.body.appendChild(minicart);
                        }
                        if (backdrop && backdrop.parentElement !== document.body) {
                            console.log('Moving backdrop to body after timeout...');
                            document.body.appendChild(backdrop);
                        }

                        console.log('Minicart moved to body after timeout, dispatching event');
                        document.dispatchEvent(new Event('minicartLoaded'));
                    }, 100);
                }).catch(function(error) {
                    console.error('Error loading minicart after timeout:', error);
                });
            } else {
                console.log('Minicart hook found after timeout:', minicartHook);
            }
        }, 2000);
    });
})();
