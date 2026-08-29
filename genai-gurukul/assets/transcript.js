(function () {
  function resolveHref(mod, base) {
    if (!mod.href) return "#";
    if (base === "modules") {
      return mod.href.replace(/^modules\//, "");
    }
    return mod.href;
  }

  function phaseApi() {
    return window.GURUKUL_PHASE;
  }

  function selectedPhase(root) {
    var api = phaseApi();
    var override = parseInt(root.getAttribute("data-phase") || "0", 10);
    if (override === 1 || override === 2) return override;
    var current = root.getAttribute("data-current") || "";
    return api ? api.resolve({ currentId: current }) : 1;
  }

  function pinStrip() {
    var header = document.querySelector(".site-header");
    var h = header ? header.offsetHeight : 64;
    document.querySelectorAll("[data-transcript]").forEach(function (el) {
      el.style.top = h + "px";
    });
  }

  function markHeaderPhase(phase) {
    document.querySelectorAll(".site-header nav a[data-phase-link]").forEach(function (a) {
      var n = a.getAttribute("data-phase-link");
      if (String(phase) === n) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
  }

  function ensurePhaseHeaderLinks() {
    var nav = document.querySelector(".site-header nav");
    if (!nav) return;
    var api = phaseApi();
    var base = document.body.getAttribute("data-base") || "";
    var href1 = api ? api.catalogHref(1, base) : (base === "modules" ? "../index.html#catalog" : "#catalog");
    var href2 = api ? api.catalogHref(2, base) : (base === "modules" ? "../index.html#em" : "#em");

    function hasPhaseLink(phase) {
      if (nav.querySelector('a[data-phase-link="' + phase + '"]')) return true;
      var nodes = nav.querySelectorAll("a[href]");
      for (var i = 0; i < nodes.length; i++) {
        var href = (nodes[i].getAttribute("href") || "").toLowerCase();
        if (phase === 2 && href.indexOf("#em") !== -1) return true;
        if (phase === 1 && (href.indexOf("#catalog") !== -1 || href.indexOf("#phase-1") !== -1)) return true;
      }
      return false;
    }

    function insertAfterCatalog(node) {
      var catalog = null;
      nav.querySelectorAll("a").forEach(function (a) {
        var t = (a.textContent || "").trim().toLowerCase();
        var href = (a.getAttribute("href") || "").toLowerCase();
        if (t === "catalog" || href.indexOf("index.html") !== -1 && href.indexOf("#em") === -1) {
          if (!catalog) catalog = a;
        }
      });
      if (catalog && catalog.nextSibling) nav.insertBefore(node, catalog.nextSibling);
      else if (catalog) nav.appendChild(node);
      else if (nav.firstChild) nav.insertBefore(node, nav.firstChild);
      else nav.appendChild(node);
    }

    if (!hasPhaseLink(1)) {
      var a1 = document.createElement("a");
      a1.href = href1;
      a1.textContent = "Phase 1";
      a1.setAttribute("data-phase-link", "1");
      insertAfterCatalog(a1);
    } else {
      var existing1 = nav.querySelector('a[href*="#catalog"]');
      if (existing1 && !existing1.getAttribute("data-phase-link")) {
        existing1.setAttribute("data-phase-link", "1");
      }
    }

    if (!hasPhaseLink(2)) {
      var a2 = document.createElement("a");
      a2.href = href2;
      a2.textContent = "Phase 2";
      a2.setAttribute("data-phase-link", "2");
      var p1 = nav.querySelector('a[data-phase-link="1"]') || nav.querySelector('a[href*="#catalog"]');
      if (p1 && p1.nextSibling) nav.insertBefore(a2, p1.nextSibling);
      else if (p1) nav.appendChild(a2);
      else insertAfterCatalog(a2);
    } else {
      var existing2 = nav.querySelector('a[href*="#em"]');
      if (existing2 && !existing2.getAttribute("data-phase-link")) {
        existing2.setAttribute("data-phase-link", "2");
      }
    }
  }

  function renderPhaseSwitch(root, selected) {
    var wrap = document.createElement("div");
    wrap.className = "phase-switch";
    wrap.setAttribute("role", "tablist");
    wrap.setAttribute("aria-label", "Course phase");

    [1, 2].forEach(function (phase) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "phase-switch-btn";
      btn.setAttribute("role", "tab");
      btn.setAttribute("aria-selected", selected === phase ? "true" : "false");
      btn.setAttribute("data-phase", String(phase));
      btn.textContent = phase === 1 ? "Phase 1" : "Phase 2";
      btn.addEventListener("click", function () {
        var api = phaseApi();
        root.setAttribute("data-phase", String(phase));
        if (api) api.write(phase);
        var onCatalog = !!document.querySelector("[data-catalog]");
        if (onCatalog) {
          var hash = phase === 2 ? "#em" : "#catalog";
          if (history.replaceState) history.replaceState(null, "", hash);
          else location.hash = hash;
          window.dispatchEvent(new Event("gurukul:phase"));
        }
        renderTranscript(root);
      });
      wrap.appendChild(btn);
    });
    return wrap;
  }

  function renderTranscript(root) {
    var modules = window.GURUKUL_MODULES || [];
    var current = root.getAttribute("data-current") || "";
    var base = document.body.getAttribute("data-base") || "";
    var api = phaseApi();
    var selected = selectedPhase(root);
    if (api) api.write(selected);

    var list = modules.filter(function (mod) {
      return !api || api.ofModule(mod) === selected;
    });

    var frag = document.createDocumentFragment();
    frag.appendChild(renderPhaseSwitch(root, selected));

    var scroller = document.createElement("div");
    scroller.className = "transcript-modules";

    list.forEach(function (mod, i) {
      if (i > 0) {
        var sep = document.createElement("span");
        sep.className = "sep";
        sep.setAttribute("aria-hidden", "true");
        sep.textContent = "·";
        scroller.appendChild(sep);
      }

      var isCurrent = mod.id === current || mod.code === current;
      var isAvailable = mod.status === "available";

      if (isAvailable) {
        var a = document.createElement("a");
        a.href = resolveHref(mod, base);
        a.textContent = mod.code;
        a.title = mod.title;
        if (isCurrent) a.setAttribute("data-current", "true");
        scroller.appendChild(a);
      } else {
        var span = document.createElement("span");
        span.className = "is-locked locked";
        span.textContent = mod.code;
        span.title = mod.title + " (locked)";
        if (isCurrent) span.setAttribute("data-current", "true");
        scroller.appendChild(span);
      }
    });

    frag.appendChild(scroller);
    root.textContent = "";
    root.appendChild(frag);
    markHeaderPhase(selected);
    pinStrip();

    var currentEl = scroller.querySelector('[data-current="true"]');
    if (currentEl && currentEl.scrollIntoView) {
      try {
        currentEl.scrollIntoView({ inline: "center", block: "nearest" });
      } catch (e) {}
    }
  }

  function init() {
    ensurePhaseHeaderLinks();
    document.querySelectorAll("[data-transcript]").forEach(renderTranscript);
    pinStrip();
    window.addEventListener("resize", pinStrip);
    window.addEventListener("hashchange", function () {
      document.querySelectorAll("[data-transcript]").forEach(function (root) {
        root.removeAttribute("data-phase");
        renderTranscript(root);
      });
    });
    window.addEventListener("gurukul:phase", function () {
      document.querySelectorAll("[data-transcript]").forEach(function (root) {
        root.removeAttribute("data-phase");
        renderTranscript(root);
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
