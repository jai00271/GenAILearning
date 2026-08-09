/**
 * Open only external websites (and labs folder) in a new tab.
 * Course modules, catalog cards, and the transcript strip stay in this window.
 */
(function () {
  function shouldOpenBlank(a) {
    var href = a.getAttribute("href") || "";
    if (!href || href.charAt(0) === "#" || href.indexOf("javascript:") === 0) {
      return false;
    }
    if (a.classList.contains("concept") || a.getAttribute("data-concept")) {
      return false;
    }
    if (a.closest("[data-transcript]")) return false;
    if (a.classList.contains("module-card")) return false;
    // Other websites (arxiv, docs, HF, …)
    if (/^https?:\/\//i.test(href)) return true;
    // Labs live in a separate folder — keep opening them in a new tab
    if (href.indexOf("genai-gurukul-labs") !== -1) return true;
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
