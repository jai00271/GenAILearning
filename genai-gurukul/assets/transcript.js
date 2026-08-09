(function () {
  function resolveHref(mod, base) {
    if (!mod.href) return "#";
    if (base === "modules") {
      // Lesson pages live in /modules/; strip leading modules/
      return mod.href.replace(/^modules\//, "");
    }
    return mod.href;
  }

  function renderTranscript(root) {
    var modules = window.GURUKUL_MODULES || [];
    var current = root.getAttribute("data-current") || "";
    var base = document.body.getAttribute("data-base") || "";
    var frag = document.createDocumentFragment();

    modules.forEach(function (mod, i) {
      if (i > 0) {
        var sep = document.createElement("span");
        sep.className = "sep";
        sep.setAttribute("aria-hidden", "true");
        sep.textContent = "·";
        frag.appendChild(sep);
      }

      var isCurrent = mod.id === current || mod.code === current;
      var isAvailable = mod.status === "available";

      if (isAvailable) {
        var a = document.createElement("a");
        a.href = resolveHref(mod, base);
        a.textContent = mod.code;
        a.title = mod.title;
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        if (isCurrent) a.setAttribute("data-current", "true");
        frag.appendChild(a);
      } else {
        var span = document.createElement("span");
        span.className = "is-locked locked";
        span.textContent = mod.code;
        span.title = mod.title + " (locked)";
        if (isCurrent) span.setAttribute("data-current", "true");
        frag.appendChild(span);
      }
    });

    root.textContent = "";
    root.appendChild(frag);
  }

  function init() {
    document.querySelectorAll("[data-transcript]").forEach(renderTranscript);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
