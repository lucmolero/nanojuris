const state = {
  sources: [],
  defaultSources: [],
  selected: new Set(),
  results: [],
  status: {},
  routing: [],
  loading: false,
  error: "",
  lastQuery: "",
  filters: {
    date_from: "",
    date_to: "",
    number: "",
    page_size: "10",
  },
};

const app = document.querySelector("#app");

function sourceLabel(source) {
  return source.display_name || source.source;
}

function resultTitle(result) {
  return (
    result.title ||
    result.case_class ||
    result.decision_type ||
    result.precedent_type ||
    result.type ||
    result.id
  );
}

function resultSummary(result) {
  return result.summary || result.thesis || result.question || result.full_text || result.text || "";
}

function metadata(result) {
  return [
    ["Fonte", result.source],
    ["Tribunal", result.court],
    ["Processo", result.case_number || result.number],
    ["Classe", result.case_class],
    ["Relator", result.rapporteur],
    ["Orgao julgador", result.judging_body],
    ["Julgamento", result.judgment_date],
    ["Publicacao", result.publication_date || result.updated_at],
    ["Tipo", result.decision_type || result.precedent_type || result.type],
    ["Documento", result.document_url || result.url],
  ].filter(([, value]) => value !== undefined && value !== null && String(value).trim());
}

function render() {
  app.innerHTML = `
    <main class="studio">
      <div class="shell">
        <header class="topbar">
          <div class="brand">
            <div class="mark">NJ</div>
            <div>
              <h1>NanoJuris Studio</h1>
              <p>Pesquisa unificada de jurisprudencia publica brasileira</p>
            </div>
          </div>
          <div class="terminal-pill"><span class="terminal-dot"></span> local-first - aurora terminal</div>
        </header>

        <section class="search-panel">
          <form class="command" id="search-form">
            <input
              class="query-input"
              id="query"
              autocomplete="off"
              placeholder="> idpj desconsideracao personalidade juridica"
              value="${escapeAttribute(state.lastQuery)}"
            />
            <button class="primary" type="submit" ${state.loading ? "disabled" : ""}>
              ${state.loading ? "Buscando..." : "Buscar"}
            </button>
          </form>

          <div class="filters">
            <div class="field">
              <label for="date-from">Publicacao de</label>
              <input id="date-from" type="date" value="${escapeAttribute(state.filters.date_from)}" />
            </div>
            <div class="field">
              <label for="date-to">Publicacao ate</label>
              <input id="date-to" type="date" value="${escapeAttribute(state.filters.date_to)}" />
            </div>
            <div class="field">
              <label for="number">Processo ou tema</label>
              <input
                id="number"
                placeholder="0000000-00.0000.0.00.0000"
                value="${escapeAttribute(state.filters.number)}"
              />
            </div>
            <div class="field">
              <label for="limit">Limite por fonte</label>
              <select id="limit">
                ${[5, 10, 20, 50]
                  .map(
                    (value) =>
                      `<option value="${value}" ${
                        String(value) === String(state.filters.page_size) ? "selected" : ""
                      }>${value}</option>`,
                  )
                  .join("")}
              </select>
            </div>
          </div>

          <div class="workspace">
            <aside class="sidebar">
              <div class="sidebar-header">
                <h2>Fontes</h2>
                <span class="selection-count">${state.selected.size}/${state.sources.length}</span>
              </div>
              <div class="source-presets" aria-label="Presets de fontes">
                <button class="ghost" data-preset="default" type="button">maduras</button>
                <button class="ghost" data-preset="juris" type="button">jurisprudencia</button>
                <button class="ghost" data-preset="all" type="button">todas</button>
                <button class="ghost" data-preset="clear" type="button">limpar</button>
              </div>
              ${renderSelectionWarning()}
              <div class="source-list">
                ${state.sources.map(renderSource).join("")}
              </div>
            </aside>

            <section class="content">
              ${renderStatus()}
              ${renderDiagnostics()}
              ${state.error ? `<div class="empty">${escapeHtml(state.error)}</div>` : renderResults()}
            </section>
          </div>
        </section>
      </div>
    </main>
  `;
  bindEvents();
}

function renderSelectionWarning() {
  const restricted = selectedSources().filter((source) => source.studio_tier === "restricted");
  if (!restricted.length) return "";
  return `
    <div class="warning">
      ${restricted.length} fonte(s) com risco alto selecionada(s). A busca pode exigir validacao,
      falhar por SSL/WAF ou demorar mais.
    </div>
  `;
}

function renderSource(source) {
  const checked = state.selected.has(source.source) ? "checked" : "";
  const filters = (source.supported_filters || []).slice(0, 4).join(" - ");
  const tier = source.studio_tier || "experimental";
  return `
    <label class="source-card ${escapeHtml(tier)}" title="${escapeAttribute(
      source.jurimetry_fit || "",
    )}">
      <input type="checkbox" data-source="${escapeAttribute(source.source)}" ${checked} />
      <span>
        <span class="source-name">
          <span>${escapeHtml(sourceLabel(source))}</span>
          <span class="muted">${escapeHtml(source.source)}</span>
        </span>
        <span class="source-meta">
          ${escapeHtml(source.category)}
          - nivel ${escapeHtml(source.contract_level || "?")}
          - risco ${escapeHtml(source.risk_level || "?")}
          ${filters ? ` - ${escapeHtml(filters)}` : ""}
        </span>
      </span>
    </label>
  `;
}

function renderStatus() {
  const entries = Object.entries(state.status);
  const total = state.results.length;
  const ok = entries.filter(([, item]) => item.status === "ok").length;
  const failed = entries.filter(([, item]) => item.status === "failed").length;
  const skipped = entries.filter(([, item]) => item.status === "skipped").length;
  return `
    <div class="metrics">
      <div class="metric"><strong>${total}</strong><span>resultados normalizados</span></div>
      <div class="metric"><strong>${ok}</strong><span>fontes consultadas</span></div>
      <div class="metric"><strong>${skipped}</strong><span>fora do escopo</span></div>
      <div class="metric"><strong>${failed}</strong><span>falhas visiveis</span></div>
    </div>
    <div class="status-strip">
      ${
        entries.length
          ? entries
              .map(
                ([source, item]) =>
                  `<span class="status-chip ${escapeHtml(item.status)}" title="${escapeAttribute(
                    item.message || "",
                  )}">${escapeHtml(source)} - ${item.count || 0} - ${escapeHtml(
                    item.status,
                  )}</span>`,
              )
              .join("")
          : '<span class="status-chip">pronto para pesquisar</span>'
      }
    </div>
  `;
}

function renderDiagnostics() {
  const entries = Object.entries(state.status).filter(([, item]) =>
    ["failed", "skipped", "unknown"].includes(item.status),
  );
  if (!entries.length) return "";
  return `
    <details class="diagnostics" open>
      <summary>Diagnostico das fontes</summary>
      <div class="diagnostic-list">
        ${entries
          .map(
            ([source, item]) => `
              <div class="diagnostic ${escapeHtml(item.status)}">
                <strong>${escapeHtml(source)} - ${escapeHtml(item.status)}</strong>
                <span>${escapeHtml(item.reason || "sem motivo declarado")}</span>
                <p>${escapeHtml(item.message || "Sem mensagem tecnica retornada.")}</p>
              </div>
            `,
          )
          .join("")}
      </div>
    </details>
  `;
}

function renderResults() {
  if (state.loading) {
    return '<div class="empty">Consultando fontes publicas. Algumas rotas podem demorar ou exigir validacao externa.</div>';
  }
  if (!state.results.length) {
    return '<div class="empty">Digite uma tese, termo juridico ou numero de processo para iniciar.</div>';
  }
  return `
    <div class="results-header">
      <h2>Resultados completos</h2>
      <button class="ghost" id="copy-all" type="button">copiar JSON</button>
    </div>
    <div class="results">
      ${state.results.map(renderResult).join("")}
    </div>
  `;
}

function renderResult(result, index) {
  const summary = resultSummary(result);
  const sourceUrl = result.document_url || result.url;
  return `
    <details class="result" ${index === 0 ? "open" : ""}>
      <summary>
        <div class="result-top">
          <span class="badge source">${escapeHtml(result.source || "")}</span>
          <span class="badge">${escapeHtml(result.court || "tribunal")}</span>
          <span class="badge">${escapeHtml(result.decision_type || result.precedent_type || result.type || "registro")}</span>
        </div>
        <h3 class="result-title">${escapeHtml(resultTitle(result))}</h3>
        <p class="result-summary">${escapeHtml(summary || "Resultado publico sem resumo textual normalizado.")}</p>
      </summary>
      <div class="result-body">
        <div class="metadata-grid">
          ${metadata(result)
            .map(
              ([label, value]) =>
                `<div class="metadata"><span>${escapeHtml(label)}</span><strong>${escapeHtml(String(value))}</strong></div>`,
            )
            .join("")}
        </div>
        ${summary ? `<p>${escapeHtml(summary)}</p>` : ""}
        <div class="actions">
          <button class="ghost" data-copy="${index}" type="button">copiar resultado</button>
          ${
            sourceUrl
              ? `<a class="ghost" href="${escapeAttribute(sourceUrl)}" target="_blank" rel="noreferrer">abrir fonte</a>`
              : ""
          }
        </div>
        <pre class="json-view">${escapeHtml(JSON.stringify(result, null, 2))}</pre>
      </div>
    </details>
  `;
}

function bindEvents() {
  document.querySelector("#search-form")?.addEventListener("submit", submitSearch);
  document.querySelectorAll("[data-preset]").forEach((item) => {
    item.addEventListener("click", () => applyPreset(item.dataset.preset));
  });
  document.querySelector("#query")?.addEventListener("input", updateStateFromInputs);
  document.querySelector("#date-from")?.addEventListener("change", updateStateFromInputs);
  document.querySelector("#date-to")?.addEventListener("change", updateStateFromInputs);
  document.querySelector("#number")?.addEventListener("input", updateStateFromInputs);
  document.querySelector("#limit")?.addEventListener("change", updateStateFromInputs);
  document.querySelector("#copy-all")?.addEventListener("click", () => {
    copyText(JSON.stringify(state.results, null, 2));
  });
  document.querySelectorAll("[data-source]").forEach((item) => {
    item.addEventListener("change", (event) => {
      const source = event.target.dataset.source;
      if (event.target.checked) state.selected.add(source);
      else state.selected.delete(source);
      render();
    });
  });
  document.querySelectorAll("[data-copy]").forEach((item) => {
    item.addEventListener("click", (event) => {
      const result = state.results[Number(event.target.dataset.copy)];
      copyText(JSON.stringify(result, null, 2));
    });
  });
}

async function submitSearch(event) {
  event.preventDefault();
  updateStateFromInputs();
  const query = state.lastQuery.trim();
  const filters = {
    date_from: state.filters.date_from,
    date_to: state.filters.date_to,
    number: state.filters.number,
  };
  state.loading = true;
  state.error = "";
  render();
  try {
    const response = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query,
        sources: [...state.selected],
        page_size: Number(state.filters.page_size || 10),
        filters,
      }),
    });
    if (!response.ok) throw new Error(await response.text());
    const payload = await response.json();
    state.results = payload.results || [];
    state.status = payload.source_status || {};
    state.routing = payload.routing_summary || [];
  } catch (error) {
    state.error = error.message || String(error);
  } finally {
    state.loading = false;
    render();
  }
}

function updateStateFromInputs() {
  state.lastQuery = document.querySelector("#query")?.value || state.lastQuery;
  state.filters = {
    date_from: document.querySelector("#date-from")?.value || "",
    date_to: document.querySelector("#date-to")?.value || "",
    number: document.querySelector("#number")?.value || "",
    page_size: document.querySelector("#limit")?.value || state.filters.page_size,
  };
}

function applyPreset(preset) {
  updateStateFromInputs();
  if (preset === "clear") {
    state.selected.clear();
  } else if (preset === "all") {
    state.sources.forEach((source) => state.selected.add(source.source));
  } else if (preset === "juris") {
    state.selected = new Set(
      state.sources
        .filter((source) => source.recommended_for_studio)
        .map((source) => source.source),
    );
  } else {
    state.selected = new Set(state.defaultSources);
  }
  render();
}

function selectedSources() {
  return state.sources.filter((source) => state.selected.has(source.source));
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const element = document.createElement("textarea");
    element.value = text;
    document.body.appendChild(element);
    element.select();
    document.execCommand("copy");
    element.remove();
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttribute(value) {
  return escapeHtml(value).replaceAll("`", "&#096;");
}

async function init() {
  render();
  try {
    const response = await fetch("/api/sources");
    const payload = await response.json();
    state.sources = payload.sources || [];
    state.defaultSources = payload.default_sources || [];
    state.selected = new Set(state.defaultSources);
  } catch (error) {
    state.error = error.message || String(error);
  }
  render();
}

init();
