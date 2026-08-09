/**
 * Concept sidepanel: auto-link glossary terms in lesson text,
 * open a right-hand explainer with diagrams / charts / pitfalls.
 */
(function () {
  var MAX_LINKS_PER_CONCEPT = 2;
  var STORAGE_W = "gurukul.sidepanel.width";
  var STORAGE_C = "gurukul.sidepanel.collapsed";
  var DEFAULT_W = 690;
  var MIN_W = 280;
  var ICON_COLLAPSE =
    '<svg viewBox="0 0 16 16" aria-hidden="true"><path fill="currentColor" d="M6.2 2.3 11 8l-4.8 5.7-1.5-1.3L8.2 8 4.7 3.6z"/></svg>';
  var ICON_EXPAND =
    '<svg viewBox="0 0 16 16" aria-hidden="true"><path fill="currentColor" d="M9.8 2.3 5 8l4.8 5.7 1.5-1.3L7.8 8l3.5-4.4z"/></svg>';
  var panel = null;
  var lastFocus = null;

  function maxSidepanelWidth() {
    return window.innerWidth < 720
      ? window.innerWidth
      : Math.round(window.innerWidth * 0.7);
  }

  function clampWidth(w) {
    var maxW = maxSidepanelWidth();
    var minW = Math.min(MIN_W, window.innerWidth);
    var n = Number(w);
    if (!isFinite(n) || n <= 0) n = DEFAULT_W;
    return Math.max(minW, Math.min(maxW, Math.round(n)));
  }

  function loadWidth() {
    try {
      return clampWidth(localStorage.getItem(STORAGE_W) || DEFAULT_W);
    } catch (err) {
      return clampWidth(DEFAULT_W);
    }
  }

  function saveWidth(w) {
    try {
      localStorage.setItem(STORAGE_W, String(clampWidth(w)));
    } catch (err) {
      /* ignore */
    }
  }

  function loadCollapsed() {
    try {
      return localStorage.getItem(STORAGE_C) === "1";
    } catch (err) {
      return false;
    }
  }

  function saveCollapsed(on) {
    try {
      localStorage.setItem(STORAGE_C, on ? "1" : "0");
    } catch (err) {
      /* ignore */
    }
  }

  function applyWidth(px) {
    var w = clampWidth(px);
    document.documentElement.style.setProperty("--sidepanel-w", w + "px");
    return w;
  }

  function applyCollapsed(target, on) {
    if (!target) return;
    target.classList.toggle("is-collapsed", !!on);
    var collapseBtn = target.querySelector(".sidepanel-collapse");
    var expandBtn = target.querySelector(".sidepanel-rail-expand");
    if (collapseBtn) collapseBtn.setAttribute("aria-expanded", on ? "false" : "true");
    if (expandBtn) expandBtn.setAttribute("aria-expanded", on ? "false" : "true");
  }

  function setCollapsed(target, on) {
    applyCollapsed(target, on);
    saveCollapsed(!!on);
  }

  function attachChrome(target) {
    if (!target) return target;
    var drawer = target.querySelector(".sidepanel-drawer");
    if (!drawer) return target;
    if (drawer.getAttribute("data-sidepanel-chrome") === "1") {
      applyWidth(loadWidth());
      return target;
    }
    drawer.setAttribute("data-sidepanel-chrome", "1");

    var header = drawer.querySelector(".sidepanel-header");
    var closeBtn = header && header.querySelector(".sidepanel-close");
    var actions = document.createElement("div");
    actions.className = "sidepanel-actions";

    var collapseBtn = document.createElement("button");
    collapseBtn.type = "button";
    collapseBtn.className = "sidepanel-collapse";
    collapseBtn.setAttribute("aria-label", "Minimise panel");
    collapseBtn.title = "Minimise";
    collapseBtn.innerHTML = ICON_COLLAPSE;

    var expandBtn = document.createElement("button");
    expandBtn.type = "button";
    expandBtn.className = "sidepanel-rail-expand";
    expandBtn.setAttribute("aria-label", "Expand panel");
    expandBtn.title = "Expand";
    expandBtn.innerHTML = ICON_EXPAND;

    if (closeBtn) {
      closeBtn.parentNode.insertBefore(actions, closeBtn);
      actions.appendChild(collapseBtn);
      actions.appendChild(expandBtn);
      actions.appendChild(closeBtn);
    } else if (header) {
      header.appendChild(actions);
      actions.appendChild(collapseBtn);
      actions.appendChild(expandBtn);
    }

    var resize = document.createElement("button");
    resize.type = "button";
    resize.className = "sidepanel-resize";
    resize.setAttribute("aria-label", "Resize panel");
    resize.title = "Drag to resize";
    drawer.insertBefore(resize, drawer.firstChild);

    collapseBtn.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      setCollapsed(target, true);
    });
    expandBtn.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      setCollapsed(target, false);
    });

    resize.addEventListener("pointerdown", function (e) {
      if (target.classList.contains("is-collapsed")) return;
      if (e.button != null && e.button !== 0) return;
      e.preventDefault();
      resize.setPointerCapture(e.pointerId);
      target.classList.add("is-resizing");
      document.body.classList.add("sidepanel-resizing");
      var startX = e.clientX;
      var startW = drawer.getBoundingClientRect().width;

      function onMove(ev) {
        applyWidth(startW + (startX - ev.clientX));
      }
      function onUp(ev) {
        try {
          resize.releasePointerCapture(ev.pointerId);
        } catch (err) {
          /* ignore */
        }
        resize.removeEventListener("pointermove", onMove);
        resize.removeEventListener("pointerup", onUp);
        resize.removeEventListener("pointercancel", onUp);
        target.classList.remove("is-resizing");
        document.body.classList.remove("sidepanel-resizing");
        saveWidth(drawer.getBoundingClientRect().width);
      }

      resize.addEventListener("pointermove", onMove);
      resize.addEventListener("pointerup", onUp);
      resize.addEventListener("pointercancel", onUp);
    });

    applyWidth(loadWidth());
    return target;
  }

  applyWidth(loadWidth());

  function conceptsMap() {
    return window.GURUKUL_CONCEPTS || {};
  }

  function escapeRegExp(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function buildIndex(concepts) {
    var aliasToId = {};
    var aliases = [];
    Object.keys(concepts).forEach(function (id) {
      var c = concepts[id];
      var list = (c.aliases && c.aliases.length ? c.aliases : [c.title]).slice();
      list.forEach(function (alias) {
        var key = String(alias).toLowerCase();
        if (!key || aliasToId[key]) return;
        aliasToId[key] = id;
        aliases.push(alias);
      });
    });
    aliases.sort(function (a, b) {
      return b.length - a.length;
    });
    if (!aliases.length) return null;
    var pattern =
      "\\b(" +
      aliases
        .map(function (a) {
          return escapeRegExp(a);
        })
        .join("|") +
      ")\\b";
    return {
      aliasToId: aliasToId,
      regex: new RegExp(pattern, "gi"),
    };
  }

  function isSkipped(node) {
    var el = node.nodeType === 3 ? node.parentElement : node;
    while (el && el.nodeType === 1) {
      var tag = el.tagName;
      if (/^(SCRIPT|STYLE|PRE|CODE|SVG|A|BUTTON|TEXTAREA|KBD|NOSCRIPT|MATH)$/.test(tag)) {
        return true;
      }
      if (tag === "H1") return true;
      if (
        el.classList &&
        (el.classList.contains("concept") ||
          el.classList.contains("callout-label") ||
          el.classList.contains("lesson-kicker") ||
          el.classList.contains("lesson-meta") ||
          el.classList.contains("sidepanel"))
      ) {
        return true;
      }
      el = el.parentElement;
    }
    return false;
  }

  function collectTextNodes(root) {
    var nodes = [];
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        if (!node.nodeValue || !/\S/.test(node.nodeValue)) return NodeFilter.FILTER_REJECT;
        if (isSkipped(node)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    });
    var n;
    while ((n = walker.nextNode())) nodes.push(n);
    return nodes;
  }

  function linkTextNode(node, index, used) {
    var text = node.nodeValue;
    index.regex.lastIndex = 0;
    var hits = [];
    var m;
    while ((m = index.regex.exec(text))) {
      var id = index.aliasToId[m[0].toLowerCase()];
      if (!id) continue;
      if ((used[id] || 0) >= MAX_LINKS_PER_CONCEPT) continue;
      if (hits.length && m.index < hits[hits.length - 1].end) continue;
      hits.push({ index: m.index, end: m.index + m[0].length, id: id });
      used[id] = (used[id] || 0) + 1;
    }
    if (!hits.length) return;

    var frag = document.createDocumentFragment();
    var cursor = 0;
    var concepts = conceptsMap();
    hits.forEach(function (hit) {
      if (hit.index > cursor) {
        frag.appendChild(document.createTextNode(text.slice(cursor, hit.index)));
      }
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "concept";
      btn.setAttribute("data-concept", hit.id);
      btn.textContent = text.slice(hit.index, hit.end);
      var title = (concepts[hit.id] && concepts[hit.id].title) || hit.id;
      btn.title = title;
      frag.appendChild(btn);
      cursor = hit.end;
    });
    if (cursor < text.length) {
      frag.appendChild(document.createTextNode(text.slice(cursor)));
    }
    node.parentNode.replaceChild(frag, node);
  }

  function ensurePanel() {
    if (panel) return panel;
    panel = document.createElement("div");
    panel.id = "gurukul-sidepanel";
    panel.className = "sidepanel";
    panel.setAttribute("aria-hidden", "true");
    panel.innerHTML =
      '<div class="sidepanel-backdrop" data-sidepanel-close="true"></div>' +
      '<div class="sidepanel-drawer" role="dialog" aria-modal="true" aria-labelledby="sidepanel-title">' +
      '<header class="sidepanel-header">' +
      '<p class="sidepanel-kicker" id="sidepanel-kicker">Concept</p>' +
      '<h2 class="sidepanel-title" id="sidepanel-title"></h2>' +
      '<p class="sidepanel-blurb" id="sidepanel-blurb"></p>' +
      '<button type="button" class="sidepanel-close" data-sidepanel-close="true" aria-label="Close concept panel">&times;</button>' +
      "</header>" +
      '<div class="sidepanel-body" id="sidepanel-body"></div>' +
      '<footer class="sidepanel-related" id="sidepanel-related" hidden>' +
      '<span class="sidepanel-related-label">Related concepts</span>' +
      '<div class="sidepanel-related-list" id="sidepanel-related-list"></div>' +
      "</footer></div>";
    document.body.appendChild(panel);
    attachChrome(panel);

    panel.addEventListener("click", function (e) {
      var close = e.target.closest("[data-sidepanel-close]");
      if (close) {
        closePanel();
        return;
      }
      var chip = e.target.closest("[data-open-concept]");
      if (chip) {
        openConcept(chip.getAttribute("data-open-concept"), chip);
      }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && panel.classList.contains("is-open")) {
        closePanel();
      }
    });
    return panel;
  }

  function renderRelated(ids) {
    var wrap = document.getElementById("sidepanel-related");
    var list = document.getElementById("sidepanel-related-list");
    var concepts = conceptsMap();
    list.textContent = "";
    var shown = 0;
    (ids || []).forEach(function (id) {
      var c = concepts[id];
      if (!c) return;
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "sidepanel-chip";
      btn.setAttribute("data-open-concept", id);
      btn.textContent = c.title;
      list.appendChild(btn);
      shown += 1;
    });
    wrap.hidden = shown === 0;
  }

  function openConcept(id, trigger) {
    var concepts = conceptsMap();
    var c = concepts[id];
    if (!c) return;
    ensurePanel();
    attachChrome(panel);
    if (window.GurukulTutor && typeof window.GurukulTutor.close === "function") {
      window.GurukulTutor.close();
    }
    if (trigger && trigger.focus) lastFocus = trigger;

    document.getElementById("sidepanel-kicker").textContent =
      (c.track ? c.track + " · " : "") + "Concept";
    document.getElementById("sidepanel-title").textContent = c.title;
    document.getElementById("sidepanel-blurb").textContent = c.blurb || "";
    document.getElementById("sidepanel-body").innerHTML = c.body || "<p>Explainer coming soon.</p>";
    renderRelated(c.related);

    panel.classList.add("is-open");
    panel.setAttribute("aria-hidden", "false");
    document.body.classList.add("sidepanel-open");
    if (trigger) setCollapsed(panel, false);
    else applyCollapsed(panel, loadCollapsed());
    var closeBtn = panel.querySelector(".sidepanel-close");
    if (closeBtn && !panel.classList.contains("is-collapsed")) closeBtn.focus();

    try {
      history.replaceState(null, "", "#concept/" + id);
    } catch (err) {
      /* ignore */
    }
  }

  function closePanel() {
    if (!panel) return;
    panel.classList.remove("is-open");
    panel.setAttribute("aria-hidden", "true");
    document.body.classList.remove("sidepanel-open");
    if (location.hash.indexOf("#concept/") === 0) {
      try {
        history.replaceState(null, "", location.pathname + location.search);
      } catch (err) {
        /* ignore */
      }
    }
    if (lastFocus && typeof lastFocus.focus === "function") {
      lastFocus.focus();
      lastFocus = null;
    }
  }

  function handleClick(e) {
    var el = e.target.closest("[data-concept]");
    if (!el) return;
    e.preventDefault();
    openConcept(el.getAttribute("data-concept"), el);
  }

  function openFromHash() {
    var m = location.hash.match(/^#concept\/([a-z0-9-]+)/i);
    if (!m) return;
    if (conceptsMap()[m[1]]) openConcept(m[1], null);
  }

  function init() {
    var concepts = conceptsMap();
    var index = buildIndex(concepts);
    document.querySelectorAll("article.lesson").forEach(function (article) {
      if (index) {
        var used = {};
        collectTextNodes(article).forEach(function (node) {
          linkTextNode(node, index, used);
        });
      }
    });
    document.addEventListener("click", handleClick);
    ensurePanel();
    openFromHash();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.GurukulSidepanel = { open: openConcept, close: closePanel, attachChrome: attachChrome };
  window.GurukulSidepanelChrome = {
    attach: attachChrome,
    expand: function (target) {
      setCollapsed(target, false);
    },
    collapse: function (target) {
      setCollapsed(target, true);
    },
  };
})();
