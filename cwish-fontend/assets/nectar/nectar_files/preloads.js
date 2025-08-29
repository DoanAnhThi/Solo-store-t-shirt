
    (function() {
      var cdnOrigin = "https://cdn.shopify.com";
      var scripts = ["https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/polyfills.i4n1wfLs.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/app.DuCPPURx.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/en.CjZaRl-j.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/page-OnePage.qnZmJf-R.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/DeliveryMethodSelectorSection.B-K2hL6z.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/useUiComponentsColorContrast.MtKXv-t_.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/VaultedPayment.3bBw0YVt.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/LocalizationExtensionField.FolvmiyA.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/ShopPayOptInDisclaimer.B9ruwm1B.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/ShipmentBreakdown.YLRhLvtB.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/MerchandiseModal.DHzvx1HX.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/StackedMerchandisePreview.DpnChhPD.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/PayButtonSection.BrVFnhdI.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/component-ShopPayVerificationSwitch.CkGCDYc1.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/useSubscribeMessenger.BtY6_QqQ.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/index.Dq0bvAkf.js"];
      var styles = ["https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/assets/app.CgiKZeiF.css","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/assets/OnePage.PMX4OSBO.css","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/assets/DeliveryMethodSelectorSection.BvrdqG-K.css","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/assets/VaultedPayment.OxMVm7u-.css","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/assets/StackedMerchandisePreview.CKAakmU8.css","https://cdn.shopify.com/shopifycloud/checkout-web/assets/c1/assets/ShopPayVerificationSwitch.DW7NMDXG.css"];
      var fontPreconnectUrls = [];
      var fontPrefetchUrls = [];
      var imgPrefetchUrls = [];

      function preconnect(url, callback) {
        var link = document.createElement('link');
        link.rel = 'dns-prefetch preconnect';
        link.href = url;
        link.crossOrigin = '';
        link.onload = link.onerror = callback;
        document.head.appendChild(link);
      }

      function preconnectAssets() {
        var resources = [cdnOrigin].concat(fontPreconnectUrls);
        var index = 0;
        (function next() {
          var res = resources[index++];
          if (res) preconnect(res, next);
        })();
      }

      function prefetch(url, as, callback) {
        var link = document.createElement('link');
        if (link.relList.supports('prefetch')) {
          link.rel = 'prefetch';
          link.fetchPriority = 'low';
          link.as = as;
          if (as === 'font') link.type = 'font/woff2';
          link.href = url;
          link.crossOrigin = '';
          link.onload = link.onerror = callback;
          document.head.appendChild(link);
        } else {
          var xhr = new XMLHttpRequest();
          xhr.open('GET', url, true);
          xhr.onloadend = callback;
          xhr.send();
        }
      }

      function prefetchAssets() {
        var resources = [].concat(
          scripts.map(function(url) { return [url, 'script']; }),
          styles.map(function(url) { return [url, 'style']; }),
          fontPrefetchUrls.map(function(url) { return [url, 'font']; }),
          imgPrefetchUrls.map(function(url) { return [url, 'image']; })
        );
        var index = 0;
        function run() {
          var res = resources[index++];
          if (res) prefetch(res[0], res[1], next);
        }
        var next = (self.requestIdleCallback || setTimeout).bind(self, run);
        next();
      }

      function onLoaded() {
        try {
          if (parseFloat(navigator.connection.effectiveType) > 2 && !navigator.connection.saveData) {
            preconnectAssets();
            prefetchAssets();
          }
        } catch (e) {}
      }

      if (document.readyState === 'complete') {
        onLoaded();
      } else {
        addEventListener('load', onLoaded);
      }
    })();
  