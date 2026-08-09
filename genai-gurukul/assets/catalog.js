(function () {
  var TRACK_META = {
    FOUND: { title: "Foundation", blurb: "Python, math intuition (including log-probs/perplexity), and how networks learn — the floor, not the career." },
    CORE: { title: "Language & Transformers", blurb: "Tokenization, the Transformer, how LLMs are trained, embeddings. Track challenge after CORE 204." },
    APP: { title: "Building GenAI Applications", blurb: "Prompts, APIs, context/memory, evaluation fundamentals — then RAG, agents, multi-agent. Eval before RAG." },
    PROD: { title: "Customization & Production", blurb: "Advanced eval, PEFT, guardrails, observability/cost, deploy, prompt/model CI/CD. Eval before fine-tune." },
    CAP: { title: "Capstone & Career", blurb: "Portfolio RAG+agent under written acceptance criteria, then interview prep. English artifacts only." }
  };

  var TRACK_ORDER = ["FOUND", "CORE", "APP", "PROD", "CAP"];

  function resolveHref(mod, base) {
    if (!mod.href) return null;
    if (base === "modules") {
      return mod.href.replace(/^modules\//, "");
    }
    return mod.href;
  }

  function renderCatalog(root) {
    var modules = window.GURUKUL_MODULES || [];
    var base = document.body.getAttribute("data-base") || "";
    var byTrack = {};

    modules.forEach(function (mod) {
      var t = mod.track || "OTHER";
      if (!byTrack[t]) byTrack[t] = [];
      byTrack[t].push(mod);
    });

    var frag = document.createDocumentFragment();

    var intro = document.createElement("div");
    intro.className = "catalog-intro";
    intro.innerHTML =
      "<h2>Course catalog</h2>" +
      "<p>Twenty-four modules across five tracks. Foundations unlock first; later tracks open as you clear Definition of Done gates.</p>";
    frag.appendChild(intro);

    TRACK_ORDER.forEach(function (trackKey) {
      var list = byTrack[trackKey];
      if (!list || !list.length) return;
      var meta = TRACK_META[trackKey] || { title: trackKey, blurb: "" };

      var section = document.createElement("section");
      section.className = "track";
      section.setAttribute("data-track", trackKey);

      var header = document.createElement("div");
      header.className = "track-header";
      header.innerHTML =
        '<span class="track-code">' +
        trackKey +
        '</span><h3 class="track-title">' +
        meta.title +
        "</h3>";
      section.appendChild(header);

      if (meta.blurb) {
        var p = document.createElement("p");
        p.style.margin = "0 0 1rem";
        p.style.color = "var(--ink-muted)";
        p.textContent = meta.blurb;
        section.appendChild(p);
      }

      var grid = document.createElement("div");
      grid.className = "module-grid";

      list.forEach(function (mod) {
        var available = mod.status === "available";
        var el = document.createElement(available ? "a" : "div");
        el.className = "module-card" + (available ? "" : " is-locked");
        if (available) {
          el.href = resolveHref(mod, base);
          el.target = "_blank";
          el.rel = "noopener noreferrer";
        }
        el.innerHTML =
          '<span class="code">' +
          mod.code +
          '</span><span class="title">' +
          mod.title +
          '</span><span class="status ' +
          (mod.status || "") +
          '">' +
          (mod.status || "unknown") +
          "</span>";
        grid.appendChild(el);
      });

      section.appendChild(grid);
      frag.appendChild(section);
    });

    root.textContent = "";
    root.appendChild(frag);
  }

  function init() {
    document.querySelectorAll("[data-catalog]").forEach(renderCatalog);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
