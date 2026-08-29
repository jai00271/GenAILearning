(function () {
  var TRACK_META = {
    FOUND: { title: "Foundation", blurb: "Python, math intuition (including log-probs/perplexity), and how networks learn — the floor, not the career." },
    CORE: { title: "Language & Transformers", blurb: "Tokenization, the Transformer, how LLMs are trained, embeddings. Track challenge after CORE 204." },
    APP: { title: "Building GenAI Applications", blurb: "Prompts, APIs, context/memory, evaluation fundamentals — then RAG, agents, multi-agent. Eval before RAG." },
    PROD: { title: "Customization & Production", blurb: "Advanced eval, PEFT, guardrails, observability/cost, deploy, prompt/model CI/CD. Eval before fine-tune." },
    CAP: { title: "Capstone & Career", blurb: "Portfolio RAG+agent under written acceptance criteria, then interview prep. English artifacts only." },
    EM: {
      title: "Phase 2 · Engineering Manager",
      blurb:
        "For Technical Managers moving to EM at large orgs: people systems, hiring bar, performance, delivery ownership, GenAI team design, culture, incidents, and leadership narrative. Builds on Phase 1 GenAI depth — does not replace it.",
    },
  };

  var INTRO = {
    1: {
      title: "Phase 1 · GenAI practitioner",
      body:
        "FOUND → CORE → APP → PROD → CAP. Twenty-four lessons plus track challenges. Eval before RAG, eval before fine-tune, capstone under written acceptance. Phase 2 sits on top — it does not replace this path.",
    },
    2: {
      title: "Phase 2 · Engineering Manager",
      body:
        "Director lens: hiring managers at Apple/Walmart-class orgs hire EMs who raise the bar on people, delivery, and judgment — not just the strongest coder on the team. Start at EM 601 after (or alongside) your GenAI portfolio work.",
    },
  };

  function resolveHref(mod, base) {
    if (!mod.href) return null;
    if (base === "modules") {
      return mod.href.replace(/^modules\//, "");
    }
    return mod.href;
  }

  function phaseApi() {
    return window.GURUKUL_PHASE;
  }

  function currentPhase() {
    var api = phaseApi();
    return api ? api.resolve({}) : 1;
  }

  function setPhase(phase) {
    var api = phaseApi();
    if (api) api.write(phase);
    var hash = phase === 2 ? "#em" : "#catalog";
    if ((location.hash || "") !== hash) {
      if (history.replaceState) history.replaceState(null, "", hash);
      else location.hash = hash;
    }
    window.dispatchEvent(new Event("gurukul:phase"));
  }

  function renderPhaseTabs(selected) {
    var tabs = document.createElement("div");
    tabs.className = "phase-tabs";
    tabs.setAttribute("role", "tablist");
    tabs.setAttribute("aria-label", "Course phase");

    [
      { phase: 1, label: "Phase 1 · GenAI", hint: "FOUND → CAP" },
      { phase: 2, label: "Phase 2 · EM", hint: "EM 601–612" },
    ].forEach(function (item) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "phase-tab";
      btn.setAttribute("role", "tab");
      btn.setAttribute("aria-selected", selected === item.phase ? "true" : "false");
      btn.setAttribute("id", item.phase === 2 ? "em" : "phase-1");
      btn.innerHTML =
        "<span class=\"phase-tab-label\">" +
        item.label +
        "</span><span class=\"phase-tab-hint\">" +
        item.hint +
        "</span>";
      btn.addEventListener("click", function () {
        setPhase(item.phase);
      });
      tabs.appendChild(btn);
    });
    return tabs;
  }

  function renderCatalog(root) {
    var modules = window.GURUKUL_MODULES || [];
    var base = document.body.getAttribute("data-base") || "";
    var api = phaseApi();
    var selected = currentPhase();
    if (api) api.write(selected);

    var byTrack = {};
    modules.forEach(function (mod) {
      var t = mod.track || "OTHER";
      if (!byTrack[t]) byTrack[t] = [];
      byTrack[t].push(mod);
    });

    var frag = document.createDocumentFragment();
    frag.appendChild(renderPhaseTabs(selected));

    var introMeta = INTRO[selected] || INTRO[1];
    var intro = document.createElement("div");
    intro.className = "catalog-intro";
    intro.innerHTML = "<h2>" + introMeta.title + "</h2><p>" + introMeta.body + "</p>";
    if (selected === 2) {
      var start = document.createElement("p");
      start.className = "catalog-start";
      start.innerHTML = 'Start at <a href="modules/em-601-role-shift.html">EM 601 · Role Shift</a>.';
      intro.appendChild(start);
    }
    frag.appendChild(intro);

    var trackOrder = api ? api.tracks(selected) : ["FOUND", "CORE", "APP", "PROD", "CAP"];

    trackOrder.forEach(function (trackKey) {
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
    window.addEventListener("hashchange", function () {
      document.querySelectorAll("[data-catalog]").forEach(renderCatalog);
    });
    window.addEventListener("gurukul:phase", function () {
      document.querySelectorAll("[data-catalog]").forEach(renderCatalog);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
