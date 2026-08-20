/**
 * Ask Gurukul — right sidepanel (same shell as concept panel).
 * Talks to /api/tutor via serve.py + Cursor SDK. Sends current lesson as context.
 */
(function () {
  var STORAGE_PREFIX = "gurukul.tutor.";
  var root = null;

  function $(sel, base) {
    return (base || document).querySelector(sel);
  }

  function gatherContext() {
    var strip = $("[data-transcript]");
    var moduleId = strip ? strip.getAttribute("data-current") || "" : "";
    var h1 = $("article.lesson h1");
    var kicker = $("article.lesson .lesson-kicker");
    var article = $("article.lesson");
    var excerpt = article ? (article.innerText || "").replace(/\s+\n/g, "\n").trim() : "";
    var title =
      (h1 && h1.textContent.trim()) ||
      (kicker && kicker.textContent.trim()) ||
      document.title;
    if (!moduleId && /\/genai-gurukul\/?$/.test(location.pathname)) {
      moduleId = "catalog";
      title = "Course catalog";
    }
    return {
      moduleId: moduleId || "unknown",
      title: title,
      url: location.href,
      excerpt: excerpt.slice(0, 8000),
    };
  }

  function storageKey(ctx) {
    return STORAGE_PREFIX + (ctx.moduleId || "unknown");
  }

  function loadSession(ctx) {
    try {
      return JSON.parse(sessionStorage.getItem(storageKey(ctx)) || "null") || { agentId: null, messages: [] };
    } catch (err) {
      return { agentId: null, messages: [] };
    }
  }

  function saveSession(ctx, session) {
    sessionStorage.setItem(storageKey(ctx), JSON.stringify(session));
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function formatInline(s) {
    s = s.replace(/`([^`]+)`/g, "<code>$1</code>");
    s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    s = s.replace(/(^|[^\*])\*([^*\n]+)\*(?!\*)/g, "$1<em>$2</em>");
    s = s.replace(
      /\[([^\]]+)\]\((https?:[^)\s]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
    );
    return s;
  }

  function isTableSep(line) {
    return /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line);
  }

  function splitRow(line) {
    var s = String(line || "").trim();
    if (s.charAt(0) === "|") s = s.slice(1);
    if (s.charAt(s.length - 1) === "|") s = s.slice(0, -1);
    return s.split("|").map(function (c) {
      return c.trim();
    });
  }

  function renderTable(headers, rows) {
    var html = '<div class="tutor-table-wrap"><table><thead><tr>';
    headers.forEach(function (h) {
      html += "<th>" + formatInline(h) + "</th>";
    });
    html += "</tr></thead><tbody>";
    rows.forEach(function (row) {
      html += "<tr>";
      for (var c = 0; c < headers.length; c++) {
        html += "<td>" + formatInline(row[c] || "") + "</td>";
      }
      html += "</tr>";
    });
    html += "</tbody></table></div>";
    return html;
  }

  function formatText(raw) {
    var html = escapeHtml(String(raw || ""));
    var fences = [];
    html = html.replace(/```(?:[a-zA-Z0-9_+-]*)\n?([\s\S]*?)```/g, function (_, code) {
      fences.push("<pre><code>" + code.trim() + "</code></pre>");
      return "\n%%FENCE" + (fences.length - 1) + "%%\n";
    });

    var lines = html.split(/\r?\n/);
    var out = [];
    var para = [];
    var i = 0;

    function flushPara() {
      if (!para.length) return;
      out.push("<p>" + formatInline(para.join("<br>")) + "</p>");
      para = [];
    }

    while (i < lines.length) {
      var line = lines[i];
      var fence = /^%%FENCE(\d+)%%$/.exec(line.trim());
      if (fence) {
        flushPara();
        out.push(fences[Number(fence[1])]);
        i += 1;
        continue;
      }
      if (/^\s*---+\s*$/.test(line) || /^\s*\*\*\*+\s*$/.test(line)) {
        flushPara();
        out.push("<hr>");
        i += 1;
        continue;
      }
      var heading = /^\s*(#{1,4})\s+(.+)$/.exec(line);
      if (heading) {
        flushPara();
        var tag = "h" + Math.min(Math.max(heading[1].length, 2), 4);
        out.push("<" + tag + ">" + formatInline(heading[2]) + "</" + tag + ">");
        i += 1;
        continue;
      }
      if (i + 1 < lines.length && /\|/.test(line) && isTableSep(lines[i + 1])) {
        flushPara();
        var headers = splitRow(line);
        i += 2;
        var rows = [];
        while (
          i < lines.length &&
          /\|/.test(lines[i]) &&
          !isTableSep(lines[i]) &&
          !/^%%FENCE/.test(lines[i].trim())
        ) {
          rows.push(splitRow(lines[i]));
          i += 1;
        }
        out.push(renderTable(headers, rows));
        continue;
      }
      var ul = /^\s*[-*]\s+(.+)$/.exec(line);
      if (ul) {
        flushPara();
        out.push("<ul>");
        while (i < lines.length) {
          var um = /^\s*[-*]\s+(.+)$/.exec(lines[i]);
          if (!um) break;
          out.push("<li>" + formatInline(um[1]) + "</li>");
          i += 1;
        }
        out.push("</ul>");
        continue;
      }
      var ol = /^\s*\d+\.\s+(.+)$/.exec(line);
      if (ol) {
        flushPara();
        out.push("<ol>");
        while (i < lines.length) {
          var om = /^\s*\d+\.\s+(.+)$/.exec(lines[i]);
          if (!om) break;
          out.push("<li>" + formatInline(om[1]) + "</li>");
          i += 1;
        }
        out.push("</ol>");
        continue;
      }
      if (!line.trim()) {
        flushPara();
        i += 1;
        continue;
      }
      para.push(line);
      i += 1;
    }
    flushPara();
    return out.join("");
  }

  function copyText(text, btn) {
    var value = String(text || "");
    function done(ok) {
      if (!btn) return;
      var prev = btn.getAttribute("data-label") || btn.textContent;
      btn.setAttribute("data-label", prev);
      btn.textContent = ok ? "Copied" : "Failed";
      setTimeout(function () {
        btn.textContent = prev;
      }, 1400);
    }
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = value;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.left = "-9999px";
      document.body.appendChild(ta);
      ta.select();
      try {
        done(document.execCommand("copy"));
      } catch (err) {
        done(false);
      }
      document.body.removeChild(ta);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(value).then(
        function () {
          done(true);
        },
        fallback
      );
    } else {
      fallback();
    }
  }

  function apiCandidates() {
    var port = location.port || "8080";
    var urls = [];
    if (location.protocol === "http:" || location.protocol === "https:") {
      urls.push(location.origin + "/api/tutor");
    }
    urls.push("http://127.0.0.1:" + port + "/api/tutor");
    urls.push("http://localhost:" + port + "/api/tutor");
    return urls.filter(function (u, i, arr) {
      return arr.indexOf(u) === i;
    });
  }

  function parseBody(res) {
    return res.text().then(function (text) {
      try {
        return { res: res, data: JSON.parse(text) };
      } catch (err) {
        var hint =
          res.status === 404
            ? " /api/tutor 404. Repo root se `python serve.py` chalao (plain http.server nahi)."
            : "Server ne JSON nahi diya (HTTP " + res.status + ").";
        return { res: res, data: { ok: false, error: hint } };
      }
    });
  }

  function postTutor(payload) {
    var urls = apiCandidates();
    var i = 0;

    function tryNext(lastErr) {
      if (i >= urls.length) {
        return Promise.reject(lastErr || new Error("Tutor API unreachable"));
      }
      var url = urls[i++];
      return fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }).then(parseBody, function (err) {
        return tryNext(err);
      });
    }

    return tryNext(null);
  }

  function ensureUi() {
    if (root) return root;

    var fab = document.createElement("button");
    fab.type = "button";
    fab.className = "tutor-fab";
    fab.setAttribute("aria-label", "Ask Gurukul");
    fab.title = "Ask Gurukul";
    fab.innerHTML =
      '<svg viewBox="0 0 24 24" aria-hidden="true">' +
      '<path fill="currentColor" d="M4 4h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H8l-4 4V6a2 2 0 0 1 2-2zm3 5v2h10V9H7zm0 4v2h7v-2H7z"/>' +
      "</svg>";

    root = document.createElement("div");
    root.id = "gurukul-tutor";
    root.className = "sidepanel tutor-sidepanel";
    root.setAttribute("aria-hidden", "true");
    root.innerHTML =
      '<div class="sidepanel-backdrop" data-tutor-close="true"></div>' +
      '<div class="sidepanel-drawer" role="dialog" aria-modal="true" aria-labelledby="tutor-title">' +
      '<header class="sidepanel-header">' +
      '<p class="sidepanel-kicker">Ask Gurukul</p>' +
      '<h2 class="sidepanel-title" id="tutor-title">Doubt desk</h2>' +
      '<p class="sidepanel-blurb" id="tutor-page"></p>' +
      '<button type="button" class="sidepanel-close" data-tutor-close="true" aria-label="Close">&times;</button>' +
      "</header>" +
      '<div class="sidepanel-body tutor-log" id="tutor-log"></div>' +
      '<footer class="sidepanel-related">' +
      '<form class="tutor-form" id="tutor-form">' +
      '<textarea id="tutor-input" rows="3" placeholder="Is page pe doubt likho…" required></textarea>' +
      '<button type="submit" class="tutor-send">Send</button>' +
      "</form></footer></div>";

    document.body.appendChild(fab);
    document.body.appendChild(root);
    if (window.GurukulSidepanelChrome && typeof window.GurukulSidepanelChrome.attach === "function") {
      window.GurukulSidepanelChrome.attach(root);
    }
    root._fab = fab;
    return root;
  }

  function renderLog(logEl, messages) {
    logEl.innerHTML = "";
    if (!messages.length) {
      logEl.innerHTML =
        '<p class="tutor-empty">Current lesson automatically context mein jaati hai. ' +
        "Cursor agent jawab dega — files edit nahi karega. Pehla jawab 10–20s le sakta hai.</p>";
      return;
    }
    messages.forEach(function (m) {
      var wrap = document.createElement("div");
      wrap.className = "tutor-msg tutor-" + m.role;

      var div = document.createElement("div");
      div.className = "tutor-bubble tutor-" + m.role;
      if (m.role === "assistant") div.innerHTML = formatText(m.text);
      else div.textContent = m.text || "";

      var copyBtn = document.createElement("button");
      copyBtn.type = "button";
      copyBtn.className = "tutor-copy";
      copyBtn.textContent = "Copy";
      copyBtn.setAttribute("aria-label", "Copy message");
      copyBtn.addEventListener("click", function () {
        copyText(m.text || "", copyBtn);
      });

      wrap.appendChild(div);
      wrap.appendChild(copyBtn);
      logEl.appendChild(wrap);
    });
    logEl.scrollTop = logEl.scrollHeight;
  }

  function setBusy(form, busy) {
    var input = $("#tutor-input", form);
    var btn = $(".tutor-send", form);
    input.disabled = busy;
    btn.disabled = busy;
    btn.innerHTML = busy
      ? '<span class="tutor-spinner tutor-spinner-sm" aria-hidden="true"></span> Wait'
      : "Send";
  }

  function showWaiting(logEl) {
    hideWaiting(logEl);
    var div = document.createElement("div");
    div.className = "tutor-bubble tutor-assistant tutor-waiting";
    div.setAttribute("aria-live", "polite");
    div.innerHTML =
      '<span class="tutor-spinner" aria-hidden="true"></span>' +
      "<span>Soch raha hoon — jawab aa raha hai…</span>";
    logEl.appendChild(div);
    logEl.scrollTop = logEl.scrollHeight;
  }

  function hideWaiting(logEl) {
    logEl.querySelectorAll(".tutor-waiting").forEach(function (el) {
      el.remove();
    });
  }

  function openChat() {
    ensureUi();
    if (window.GurukulSidepanel && typeof window.GurukulSidepanel.close === "function") {
      window.GurukulSidepanel.close();
    }
    var ctx = gatherContext();
    $("#tutor-page", root).textContent =
      (ctx.moduleId ? ctx.moduleId.toUpperCase() + " · " : "") + ctx.title;
    renderLog($("#tutor-log", root), loadSession(ctx).messages);
    root.classList.add("is-open");
    root.setAttribute("aria-hidden", "false");
    document.body.classList.add("tutor-open");
    if (root._fab) root._fab.setAttribute("aria-expanded", "true");
    if (window.GurukulSidepanelChrome) {
      if (typeof window.GurukulSidepanelChrome.attach === "function") {
        window.GurukulSidepanelChrome.attach(root);
      }
      if (typeof window.GurukulSidepanelChrome.expand === "function") {
        window.GurukulSidepanelChrome.expand(root);
      }
    }
    var input = $("#tutor-input", root);
    if (input) input.focus();
  }

  function closeChat() {
    if (!root) return;
    root.classList.remove("is-open");
    root.setAttribute("aria-hidden", "true");
    document.body.classList.remove("tutor-open");
    if (root._fab) root._fab.setAttribute("aria-expanded", "false");
  }

  function init() {
    ensureUi();
    var fab = root._fab;
    var form = $("#tutor-form", root);
    var input = $("#tutor-input", root);
    var logEl = $("#tutor-log", root);

    fab.addEventListener("click", function () {
      if (root.classList.contains("is-open")) closeChat();
      else openChat();
    });

    root.addEventListener("click", function (e) {
      if (e.target.closest("[data-tutor-close]")) closeChat();
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && root.classList.contains("is-open")) closeChat();
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var question = input.value.trim();
      if (!question) return;
      if (location.protocol === "file:") {
        renderLog(logEl, [
          {
            role: "assistant",
            text: "Yeh page file:// se khula hai. http://127.0.0.1:8080/genai-gurukul/ use karo — `python serve.py`.",
          },
        ]);
        return;
      }
      var ctx = gatherContext();
      $("#tutor-page", root).textContent =
        (ctx.moduleId ? ctx.moduleId.toUpperCase() + " · " : "") + ctx.title;
      var session = loadSession(ctx);
      session.messages.push({ role: "user", text: question });
      input.value = "";
      renderLog(logEl, session.messages);
      showWaiting(logEl);
      setBusy(form, true);

      postTutor({
        question: question,
        agentId: session.agentId,
        context: ctx,
      })
        .then(function (out) {
          var data = out.data || {};
          if (!out.res.ok || data.ok === false) {
            session.messages.push({
              role: "assistant",
              text:
                data.error ||
                data.text ||
                "Tutor unavailable. `python serve.py` restart + .env mein CURSOR_API_KEY check karo.",
            });
          } else {
            if (data.agentId) session.agentId = data.agentId;
            session.messages.push({ role: "assistant", text: data.text || "(empty reply)" });
          }
          saveSession(ctx, session);
          renderLog(logEl, session.messages);
        })
        .catch(function (err) {
          session.messages.push({
            role: "assistant",
            text:
              "Tutor API nahi mili. Repo root se `python serve.py` chalao, phir http://127.0.0.1:8080/genai-gurukul/ kholo. " +
              (err && err.message ? "(" + err.message + ")" : ""),
          });
          saveSession(ctx, session);
          renderLog(logEl, session.messages);
        })
        .finally(function () {
          setBusy(form, false);
          input.focus();
        });
    });

    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        form.requestSubmit();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.GurukulTutor = { open: openChat, close: closeChat };
})();
