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
        return fetch(path).then(function(r){ return r.text(); }).then(function(h){
            el.innerHTML = h;
            runScripts(el);
            // ensure header/footer base styles are available if partial doesn't include them
            if(!document.querySelector('link[href*="theme.scss.css"]')){
                var link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = './assets/home/home_files/theme.scss.css';
                document.head.appendChild(link);
            }
            // After header loads, if it requested minicart include, load it
            if (el.getAttribute('data-include') === 'header') {
                var hook = document.querySelector('[data-include="minicart"]');
                if (hook) { 
                    load(hook, './partials/minicart.html').then(function() {
                        // Trigger event khi minicart được load xong
                        document.dispatchEvent(new Event('minicartLoaded'));
                    });
                } else {
                    // Nếu không có minicart hook, tạo một cái mới
                    var newHook = document.createElement('div');
                    newHook.setAttribute('data-include', 'minicart');
                    document.body.appendChild(newHook);
                    
                    load(newHook, './partials/minicart.html').then(function() {
                        document.dispatchEvent(new Event('minicartLoaded'));
                    });
                }
            }
        }).catch(function(){ el.innerHTML = ''; });
    }
    
    // Expose load function globally for other scripts
    window.loadPartial = load;
    ready(function () {
        document.querySelectorAll('[data-include]').forEach(function (el) {
            var name = el.getAttribute('data-include');
            if (name === 'header') { load(el, './partials/header.html'); }
            if (name === 'footer') { load(el, './partials/footer.html'); }
            if (name === 'minicart') { load(el, './partials/minicart.html'); }
        });
        
        // Đảm bảo minicart được load sau khi tất cả partials đã load
        setTimeout(function() {
            var minicartHook = document.querySelector('[data-include="minicart"]');
            if (!minicartHook) {
                var newHook = document.createElement('div');
                newHook.setAttribute('data-include', 'minicart');
                document.body.appendChild(newHook);
                
                load(newHook, './partials/minicart.html').then(function() {
                    document.dispatchEvent(new Event('minicartLoaded'));
                });
            }
        }, 2000);
    });
})();
