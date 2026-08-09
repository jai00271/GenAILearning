/**
 * Open outbound / lab / catalog module links in a new tab.
 * Keep in-lesson nav (prev/next, brand, catalog) in the same window.
 */
(function () {
  function shouldOpenBlank(a) {
    var href = a.getAttribute("href") || "";
    if (!href || href.charAt(0) === "#" || href.indexOf("javascript:") === 0) {
      return false;
    }
    if (a.classList.contains("brand")) return false;
    if (a.closest(".lesson-nav")) return false;
    if (a.closest(".site-footer") && href.indexOf("genai-gurukul-labs") === -1) {
      return false;
    }
    // Catalog / back-to-index stay in this window unless Labs
    if (
      (href === "index.html" || href === "../index.html" || /\/index\.html$/.test(href)) &&
      href.indexOf("genai-gurukul-labs") === -1
    ) {
      return false;
    }
    if (/^https?:\/\//i.test(href)) return true;
    if (href.indexOf("genai-gurukul-labs") !== -1) return true;
    if (a.classList.contains("module-card")) return true;
    if (a.closest("[data-transcript]")) return true;
    if (a.classList.contains("btn-primary")) return true;
    // Header "Start FOUND-101" and similar lesson deep-links from home
    if (a.closest(".site-header") && /\.html(?:$|#)/.test(href)) return true;
    return false;
  }

  function decorate(a) {
    if (!a || a.tagName !== "A") return;
    if (!shouldOpenBlank(a)) return;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
  }

  function decorateTree(root) {
    if (!root) return;
    if (root.tagName === "A") decorate(root);
    if (root.querySelectorAll) {
      root.querySelectorAll("a[href]").forEach(decorate);
    }
  }

  function init() {
    decorateTree(document);
    var obs = new MutationObserver(function (mutations) {
      mutations.forEach(function (m) {
        m.addedNodes.forEach(function (node) {
          if (node.nodeType === 1) decorateTree(node);
        });
      });
    });
    obs.observe(document.documentElement, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
