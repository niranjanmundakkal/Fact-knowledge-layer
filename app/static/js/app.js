/**
 * Client application logic for Superjoin Fact Knowledge Layer dashboard.
 */

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initTabs();
  initModals();
  initDropzone();
  initFilters();
  loadAllData();
});

let cachedFacts = [];
let cachedRelationships = [];
let cachedDocuments = [];

// 0. Theme Manager (Default: Realistic White)
function initTheme() {
  const savedTheme = localStorage.getItem("fkl_theme") || "light";
  applyTheme(savedTheme);

  const toggleBtn = document.getElementById("btn-theme-toggle");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "light";
      const nextTheme = current === "dark" ? "light" : "dark";
      applyTheme(nextTheme);
      localStorage.setItem("fkl_theme", nextTheme);
    });
  }
}

function applyTheme(theme) {
  const icon = document.getElementById("theme-toggle-icon");
  const text = document.getElementById("theme-toggle-text");
  if (theme === "dark") {
    document.documentElement.setAttribute("data-theme", "dark");
    if (icon) icon.innerText = "☀️";
    if (text) text.innerText = "Light";
  } else {
    document.documentElement.removeAttribute("data-theme");
    if (icon) icon.innerText = "🌙";
    if (text) text.innerText = "Dark";
  }
}

// 1. Tab Navigation
function initTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add("active");
    });
  });
}

// 2. Load All Data from REST API
async function loadAllData() {
  try {
    await Promise.all([
      loadStats(),
      loadFourCases(),
      loadRelationships(),
      loadFacts(),
      loadDocuments()
    ]);
  } catch (err) {
    console.error("Error loading dashboard data:", err);
  }
}

// 3. Stats Loader
async function loadStats() {
  try {
    const res = await fetch("/api/stats");
    const data = await res.json();

    document.getElementById("stat-docs").innerText = data.total_documents;
    document.getElementById("stat-facts").innerText = data.total_facts;
    document.getElementById("stat-corrob").innerText = data.corroborations_count;
    document.getElementById("stat-contra").innerText = data.contradictions_count;
    document.getElementById("stat-reconc").innerText = data.reconciled_count;

    document.getElementById("tab-facts-badge").innerText = data.total_facts;
    document.getElementById("tab-docs-badge").innerText = data.total_documents;
    document.getElementById("tab-rel-badge").innerText = data.total_relationships;
  } catch (e) {
    console.error("Failed to load stats:", e);
  }
}

// 4. The 4 Required Cases Loader
async function loadFourCases() {
  const container = document.getElementById("four-cases-container");
  try {
    const res = await fetch("/api/four-cases");
    const data = await res.json();

    if (!data.cases || data.cases.length === 0) {
      container.innerHTML = "<div class='stat-sub'>No cases loaded yet. Click 'Load Starter Dataset' above.</div>";
      return;
    }

    container.innerHTML = data.cases.map(item => renderCaseCard(item)).join("");
  } catch (e) {
    container.innerHTML = `<div style="color: var(--contra-color);">Error loading cases: ${e.message}</div>`;
  }
}

function renderCaseCard(c) {
  let badgeClass = "badge-corrob";
  let borderClass = "case-corrob";
  let badgeLabel = "Corroboration";

  if (c.case_type === "CONTRADICTING") {
    badgeClass = "badge-contra";
    borderClass = "case-contra";
    badgeLabel = "Genuine Contradiction";
  } else if (c.case_type === "RECONCILED") {
    badgeClass = "badge-reconc";
    borderClass = "case-reconc";
    badgeLabel = "Reconciled by Context";
  } else if (c.case_type === "REASONING_EXTRACTION_FAILURE") {
    badgeClass = "badge-failure";
    borderClass = "case-failure";
    badgeLabel = "Failure Analysis & Mitigation";
  }

  const evA = c.evidence_a;
  const evB = c.evidence_b;

  return `
    <article class="case-card ${borderClass}">
      <div class="case-header">
        <div>
          <div class="case-meta">
            <span class="case-num">CASE ${c.case_number}</span>
            <span class="case-badge ${badgeClass}">${badgeLabel}</span>
          </div>
          <h2 class="case-title">${escapeHtml(c.case_title)}</h2>
          <p class="case-claim">${escapeHtml(c.claim_summary)}</p>
        </div>
      </div>

      <div class="evidence-split">
        <div class="evidence-box">
          <div class="evidence-source">
            <span class="doc-name" style="cursor: pointer; text-decoration: underline;" onclick="openDocumentModal('${escapeHtml(evA.document_name)}')" title="Click to inspect PDF dossier">📄 ${escapeHtml(evA.document_name)}</span>
            <span class="page-tag">Page ${evA.page_number}</span>
          </div>
          <div class="evidence-quote">"${escapeHtml(evA.exact_quote)}"</div>
          <div class="evidence-value">Extracted Value: <span style="color: var(--accent-cyan);">${escapeHtml(evA.value)}</span></div>
        </div>

        ${evB ? `
        <div class="evidence-box">
          <div class="evidence-source">
            <span class="doc-name" style="cursor: pointer; text-decoration: underline;" onclick="openDocumentModal('${escapeHtml(evB.document_name)}')" title="Click to inspect PDF dossier">📄 ${escapeHtml(evB.document_name)}</span>
            <span class="page-tag">Page ${evB.page_number}</span>
          </div>
          <div class="evidence-quote">"${escapeHtml(evB.exact_quote)}"</div>
          <div class="evidence-value">Extracted Value: <span style="color: var(--accent-cyan);">${escapeHtml(evB.value)}</span></div>
        </div>
        ` : `
        <div class="evidence-box" style="display: flex; flex-direction: column; justify-content: center;">
          <div style="color: var(--failure-color); font-weight: 700; margin-bottom: 6px;">Root Cause & Challenge</div>
          <p style="font-size: 13px; color: #cbd5e1;">${escapeHtml(c.context_explanation)}</p>
        </div>
        `}
      </div>

      <div class="reasoning-box">
        <div class="reasoning-label"><span>🧠</span> System Epistemic Reasoning & Contextual Resolution</div>
        <div class="reasoning-text">${escapeHtml(c.system_reasoning)}</div>
      </div>

      ${c.mitigation_or_improvement ? `
      <div class="mitigation-box">
        <h4>🛠️ How We Handled & Future Architectural Mitigations</h4>
        <pre>${escapeHtml(c.mitigation_or_improvement)}</pre>
      </div>
      ` : ''}
    </article>
  `;
}

// 5. Cross-Document Relationships Loader
async function loadRelationships(filter = "all") {
  const container = document.getElementById("relationships-container");
  try {
    const res = await fetch(`/api/relationships?type=${filter}`);
    cachedRelationships = await res.json();

    document.getElementById("rel-count-summary").innerText = `Showing ${cachedRelationships.length} relationships`;

    if (cachedRelationships.length === 0) {
      container.innerHTML = "<div class='stat-sub' style='padding: 20px;'>No relationships match the selected filter.</div>";
      return;
    }

    container.innerHTML = cachedRelationships.map(r => renderRelCard(r)).join("");
  } catch (e) {
    container.innerHTML = `<div style="color: var(--contra-color);">Error loading relationships: ${e.message}</div>`;
  }
}

function renderRelCard(r) {
  let badgeClass = "badge-corrob";
  let label = "Corroborating";
  if (r.relationship_type === "CONTRADICTING") {
    badgeClass = "badge-contra";
    label = "Contradicting";
  } else if (r.relationship_type === "RECONCILED") {
    badgeClass = "badge-reconc";
    label = `Reconciled (${r.reconciliation_category.replace('_', ' ')})`;
  }

  return `
    <div class="rel-card">
      <div class="rel-header">
        <span class="rel-type-tag ${badgeClass}">${label}</span>
        <span class="rel-entity">Entity: <b>${escapeHtml(r.fact_a.entity)}</b></span>
      </div>

      <div class="evidence-split" style="margin-bottom: 12px;">
        <div class="evidence-box">
          <div class="evidence-source">
            <span class="doc-name" style="cursor: pointer; text-decoration: underline;" onclick="openDocumentModal('${escapeHtml(r.fact_a.document_name)}')" title="Click to inspect PDF dossier">📄 ${escapeHtml(r.fact_a.document_name)}</span>
            <span class="page-tag">P.${r.fact_a.page_number}</span>
          </div>
          <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">${escapeHtml(r.fact_a.attribute)}</div>
          <div class="evidence-value">${escapeHtml(r.fact_a.value)}</div>
          <div class="evidence-quote" style="margin-top: 6px;">"${escapeHtml(r.fact_a.exact_quote)}"</div>
        </div>

        <div class="evidence-box">
          <div class="evidence-source">
            <span class="doc-name" style="cursor: pointer; text-decoration: underline;" onclick="openDocumentModal('${escapeHtml(r.fact_b.document_name)}')" title="Click to inspect PDF dossier">📄 ${escapeHtml(r.fact_b.document_name)}</span>
            <span class="page-tag">P.${r.fact_b.page_number}</span>
          </div>
          <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">${escapeHtml(r.fact_b.attribute)}</div>
          <div class="evidence-value">${escapeHtml(r.fact_b.value)}</div>
          <div class="evidence-quote" style="margin-top: 6px;">"${escapeHtml(r.fact_b.exact_quote)}"</div>
        </div>
      </div>

      <div class="reasoning-box" style="margin-top: 8px;">
        <div class="reasoning-label"><span>💡</span> Reconciliation Explanation</div>
        <div class="reasoning-text">${escapeHtml(r.reasoning)}</div>
        ${r.context_nuance ? `<div style="font-size: 12px; color: var(--accent-cyan); margin-top: 6px;"><b>Nuance:</b> ${escapeHtml(r.context_nuance)}</div>` : ''}
      </div>
    </div>
  `;
}

// 6. Grounded Facts Table Loader
async function loadFacts() {
  try {
    const res = await fetch("/api/facts");
    cachedFacts = await res.json();
    populateFactFilters(cachedFacts);
    renderFactsTable(cachedFacts);
  } catch (e) {
    console.error("Error loading facts:", e);
  }
}

function renderFactsTable(facts) {
  const tbody = document.getElementById("facts-table-body");
  if (!facts || facts.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted);">No facts match current filters.</td></tr>`;
    return;
  }

  tbody.innerHTML = facts.map(f => `
    <tr>
      <td>
        <span class="tag tag-doc" style="cursor: pointer;" onclick="openDocumentModal('${escapeHtml(f.document_id)}')" title="Click to inspect this PDF in detail">📄 ${escapeHtml(f.document_name)}</span><br/>
        <span class="tag tag-page">Page ${f.page_number}</span>
      </td>
      <td><b>${escapeHtml(f.entity)}</b></td>
      <td>${escapeHtml(f.attribute)}</td>
      <td style="font-family: var(--font-mono); font-weight: 700; color: #fff;">${escapeHtml(f.value)}</td>
      <td style="font-size: 12px; color: var(--text-muted);">${escapeHtml(f.temporal_scope || 'N/A')}</td>
      <td style="max-width: 380px;">
        <div style="font-style: italic; font-size: 12px; line-height: 1.4; color: #cbd5e1;">"${escapeHtml(f.exact_quote)}"</div>
      </td>
      <td>
        <div class="confidence-bar">
          <div class="conf-track">
            <div class="conf-fill" style="width: ${Math.round(f.confidence * 100)}%;"></div>
          </div>
          <span style="font-size: 11px; font-family: var(--font-mono);">${Math.round(f.confidence * 100)}%</span>
        </div>
      </td>
    </tr>
  `).join("");
}

function populateFactFilters(facts) {
  const docSelect = document.getElementById("fact-doc-filter");
  const entitySelect = document.getElementById("fact-entity-filter");

  const docs = Array.from(new Set(facts.map(f => f.document_name))).sort();
  const entities = Array.from(new Set(facts.map(f => f.entity))).sort();

  docSelect.innerHTML = `<option value="">All Documents (${docs.length})</option>` + 
    docs.map(d => `<option value="${escapeHtml(d)}">${escapeHtml(d)}</option>`).join("");

  entitySelect.innerHTML = `<option value="">All Entities (${entities.length})</option>` + 
    entities.map(e => `<option value="${escapeHtml(e)}">${escapeHtml(e)}</option>`).join("");
}

// 7. Documents Loader & Individual PDF Dossier System
let activeDocumentId = null;

async function loadDocuments() {
  try {
    const res = await fetch("/api/documents");
    cachedDocuments = await res.json();
    
    // Render the interactive card selector
    renderDocumentCards(cachedDocuments);

    // Populate Quick Select dropdown
    const quickSelect = document.getElementById("doc-quick-select");
    if (quickSelect) {
      quickSelect.innerHTML = `<option value="">Choose a document to inspect (${cachedDocuments.length})...</option>` +
        cachedDocuments.map(d => `<option value="${d.id}">${escapeHtml(d.filename)}</option>`).join("");
      if (activeDocumentId) quickSelect.value = activeDocumentId;
    }

    // Render the overview table
    const tbody = document.getElementById("docs-table-body");
    if (tbody) {
      if (cachedDocuments.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No documents ingested yet.</td></tr>`;
      } else {
        tbody.innerHTML = cachedDocuments.map(d => `
          <tr>
            <td style="font-family: var(--font-mono); font-weight: 600; color: var(--accent-cyan); cursor: pointer;" onclick="selectDocument('${d.id}', true)">
              📄 ${escapeHtml(d.filename)}
            </td>
            <td>${d.page_count} pages</td>
            <td><b style="color: #10b981;">${d.fact_count} facts</b></td>
            <td style="font-size: 12px; color: var(--text-muted);">${formatBytes(d.file_size_bytes)}</td>
            <td style="font-size: 12px; color: var(--text-muted);">${escapeHtml(d.uploaded_at)}</td>
            <td>
              <button class="btn btn-secondary" style="padding: 4px 10px; font-size: 11px;" onclick="selectDocument('${d.id}', true)">
                Inspect Dossier 🔍
              </button>
            </td>
          </tr>
        `).join("");
      }
    }

    // Auto-select first document if none selected
    if (!activeDocumentId && cachedDocuments.length > 0) {
      selectDocument(cachedDocuments[0].id, false);
    }
  } catch (e) {
    console.error("Error loading documents:", e);
  }
}

function renderDocumentCards(docs) {
  const grid = document.getElementById("docs-cards-grid");
  if (!grid) return;

  if (docs.length === 0) {
    grid.innerHTML = `<div class="stat-sub" style="padding: 20px;">No documents indexed. Click 'Load Starter Dataset' above.</div>`;
    return;
  }

  grid.innerHTML = docs.map(d => {
    let icon = "📄";
    let cat = "Corporate Filing";
    const fnLower = d.filename.toLowerCase();
    if (fnLower.includes("prospectus")) { icon = "📜"; cat = "SEBI Offering Prospectus"; }
    else if (fnLower.includes("earnings")) { icon = "📈"; cat = "Q4 Investor Presentation"; }
    else if (fnLower.includes("annual")) { icon = "📘"; cat = "Audited Annual Report"; }
    else if (fnLower.includes("survey") || fnLower.includes("economic")) { icon = "🌐"; cat = "Macroeconomic Policy Survey"; }

    const isSelected = activeDocumentId === d.id || activeDocumentId === d.filename;

    return `
      <div class="doc-select-card ${isSelected ? 'selected' : ''}" data-id="${d.id}" data-filename="${escapeHtml(d.filename)}" onclick="selectDocument('${d.id}', true)">
        <div>
          <div class="doc-select-card-header">
            <div class="doc-icon-badge">${icon}</div>
            <div style="flex: 1; min-width: 0;">
              <span class="doc-card-cat">${cat}</span>
              <div class="doc-card-title">${escapeHtml(d.filename)}</div>
            </div>
          </div>
          <div class="doc-card-stats">
            <div class="doc-stat-item">
              <span class="doc-stat-val">${d.page_count}</span>
              <span class="doc-stat-lbl">Pages</span>
            </div>
            <div class="doc-stat-item">
              <span class="doc-stat-val" style="color: #10b981;">${d.fact_count}</span>
              <span class="doc-stat-lbl">Facts</span>
            </div>
            <div class="doc-stat-item">
              <span class="doc-stat-val">${formatBytes(d.file_size_bytes)}</span>
              <span class="doc-stat-lbl">Size</span>
            </div>
          </div>
          <p style="font-size: 12px; color: var(--text-muted); line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
            ${escapeHtml(d.text_preview || 'Parsed PDF file ready for cross-document analysis.')}
          </p>
        </div>
        <div class="doc-card-footer">
          <span>Uploaded ${escapeHtml(d.uploaded_at.split(' ')[0])}</span>
          <button class="btn btn-secondary" style="padding: 4px 10px; font-size: 11px;" onclick="event.stopPropagation(); selectDocument('${d.id}', true);">
            Inspect Dossier 🔍
          </button>
        </div>
      </div>
    `;
  }).join("");
}

async function selectDocument(docIdOrName, autoScroll = false) {
  activeDocumentId = docIdOrName;

  // Highlight active card
  document.querySelectorAll(".doc-select-card").forEach(c => {
    if (c.getAttribute("data-id") === docIdOrName || c.getAttribute("data-filename") === docIdOrName) {
      c.classList.add("selected");
    } else {
      c.classList.remove("selected");
    }
  });

  const quickSelect = document.getElementById("doc-quick-select");
  if (quickSelect) quickSelect.value = docIdOrName;

  const container = document.getElementById("selected-doc-dossier");
  if (!container) return;

  container.style.display = "block";
  container.innerHTML = `<div style="padding: 30px; text-align: center; color: var(--text-muted);">
    <div style="font-size: 24px; margin-bottom: 8px;">⏳</div>
    Loading detailed document dossier...
  </div>`;

  try {
    const res = await fetch(`/api/documents/${encodeURIComponent(docIdOrName)}`);
    if (!res.ok) throw new Error("Document not found");
    const data = await res.json();
    renderDossierIntoContainer(data, container, "panel");

    if (autoScroll) {
      container.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  } catch (err) {
    container.innerHTML = `<div style="color: var(--contra-color); padding: 20px;">Failed to load dossier: ${err.message}</div>`;
  }
}

async function openDocumentModal(docIdOrName) {
  const modal = document.getElementById("doc-dossier-modal");
  const body = document.getElementById("modal-dossier-body");
  if (!modal || !body) return;

  body.innerHTML = `<div style="padding: 40px; text-align: center; color: var(--text-muted);">
    <div style="font-size: 24px; margin-bottom: 8px;">⏳</div>
    Loading document dossier...
  </div>`;
  modal.classList.add("open");

  try {
    const res = await fetch(`/api/documents/${encodeURIComponent(docIdOrName)}`);
    if (!res.ok) throw new Error("Document not found");
    const data = await res.json();
    renderDossierIntoContainer(data, body, "modal");
  } catch (e) {
    body.innerHTML = `<div style="color: var(--contra-color); padding: 20px;">Error loading document dossier: ${e.message}</div>`;
  }
}

function renderDossierIntoContainer(data, container, context = "panel") {
  const doc = data.document;
  const profile = data.profile;
  const stats = data.stats;
  const facts = data.facts || [];
  const rels = data.relationships || [];
  const pages = data.pages || [];

  const uid = context + "_" + (doc.id || Math.random().toString(36).substr(2, 5));

  let icon = "📄";
  if (doc.filename.toLowerCase().includes("prospectus")) icon = "📜";
  else if (doc.filename.toLowerCase().includes("earnings")) icon = "📈";
  else if (doc.filename.toLowerCase().includes("annual")) icon = "📘";
  else if (doc.filename.toLowerCase().includes("survey") || doc.filename.toLowerCase().includes("economic")) icon = "🌐";

  const highlightsHtml = (profile.key_highlights || []).map(h => `
    <div class="highlight-pill">
      <span>🔹</span> ${escapeHtml(h)}
    </div>
  `).join("");

  const factsRowsHtml = facts.map(f => `
    <tr>
      <td><span class="tag tag-page">Page ${f.page_number}</span></td>
      <td><b>${escapeHtml(f.attribute)}</b></td>
      <td style="font-family: var(--font-mono); font-weight: 700; color: var(--accent-cyan);">${escapeHtml(f.value)}</td>
      <td style="font-size: 12px; color: var(--text-muted);">${escapeHtml(f.temporal_scope || 'N/A')}</td>
      <td style="max-width: 380px;">
        <div style="font-style: italic; font-size: 12px; line-height: 1.4; color: var(--text-main);">"${escapeHtml(f.exact_quote)}"</div>
      </td>
      <td>
        <div class="confidence-bar">
          <div class="conf-track"><div class="conf-fill" style="width: ${Math.round(f.confidence * 100)}%;"></div></div>
          <span style="font-size: 11px; font-family: var(--font-mono);">${Math.round(f.confidence * 100)}%</span>
        </div>
      </td>
    </tr>
  `).join("");

  const relsCardsHtml = rels.length === 0 
    ? `<div class="stat-sub" style="padding: 20px; text-align: center;">No cross-document relationships recorded for this document yet.</div>`
    : rels.map(r => {
        let badgeClass = "badge-corrob";
        let label = "Corroborating";
        if (r.relationship_type === "CONTRADICTING") {
          badgeClass = "badge-contra";
          label = "Contradicting";
        } else if (r.relationship_type === "RECONCILED") {
          badgeClass = "badge-reconc";
          label = `Reconciled (${r.reconciliation_category.replace('_', ' ')})`;
        }
        const isA = r.fact_a.document_name === doc.filename || r.fact_a.document_id === doc.id;
        const myFact = isA ? r.fact_a : r.fact_b;
        const otherFact = isA ? r.fact_b : r.fact_a;

        return `
          <div class="rel-card" style="margin-bottom: 12px;">
            <div class="rel-header">
              <span class="rel-type-tag ${badgeClass}">${label}</span>
              <span class="rel-entity">Subject: <b>${escapeHtml(myFact.attribute)}</b></span>
            </div>
            <div class="evidence-split">
              <div class="evidence-box" style="border-left: 3px solid var(--primary);">
                <div class="evidence-source">
                  <span class="doc-name">This PDF: ${escapeHtml(doc.filename)}</span>
                  <span class="page-tag">Page ${myFact.page_number}</span>
                </div>
                <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">${escapeHtml(myFact.attribute)}</div>
                <div class="evidence-value" style="color: var(--accent-cyan); font-weight: 700;">${escapeHtml(myFact.value)}</div>
                <div class="evidence-quote" style="margin-top: 6px;">"${escapeHtml(myFact.exact_quote)}"</div>
              </div>
              <div class="evidence-box">
                <div class="evidence-source">
                  <span class="doc-name" style="cursor: pointer; text-decoration: underline;" onclick="openDocumentModal('${escapeHtml(otherFact.document_name)}')">Other PDF: ${escapeHtml(otherFact.document_name)}</span>
                  <span class="page-tag">Page ${otherFact.page_number}</span>
                </div>
                <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">${escapeHtml(otherFact.attribute)}</div>
                <div class="evidence-value" style="color: var(--accent-cyan); font-weight: 700;">${escapeHtml(otherFact.value)}</div>
                <div class="evidence-quote" style="margin-top: 6px;">"${escapeHtml(otherFact.exact_quote)}"</div>
              </div>
            </div>
            <div class="reasoning-box" style="margin-top: 10px;">
              <div class="reasoning-label"><span>🧠</span> Epistemic Reasoning</div>
              <div class="reasoning-text">${escapeHtml(r.reasoning)}</div>
              ${r.context_nuance ? `<div style="font-size: 12px; color: var(--accent-cyan); margin-top: 6px;"><b>Resolving Context:</b> ${escapeHtml(r.context_nuance)}</div>` : ''}
            </div>
          </div>
        `;
      }).join("");

  const pagePillsHtml = pages.map((p, idx) => `
    <button class="page-pill ${idx === 0 ? 'active' : ''}" data-target="${uid}_page_${p.page_number}">
      Page ${p.page_number} (${p.facts_count} facts, ${p.character_count} chars)
    </button>
  `).join("");

  const pageContentsHtml = pages.map((p, idx) => `
    <div id="${uid}_page_${p.page_number}" class="page-content-pane" style="display: ${idx === 0 ? 'block' : 'none'};">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="font-size: 12px; font-weight: 600; color: var(--text-subtle);">Exact Text Content — Page ${p.page_number} (${p.character_count} characters)</span>
        <span class="tag tag-page">${p.facts_count} Grounded Facts on this Page</span>
      </div>
      <div class="page-text-card">${escapeHtml(p.text)}</div>
    </div>
  `).join("");

  container.innerHTML = `
    <div class="dossier-header">
      <div class="dossier-title-area">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
          <span style="font-size: 26px;">${icon}</span>
          <h2>${escapeHtml(profile.title)}</h2>
        </div>
        <div class="dossier-meta-chips">
          <span class="meta-chip meta-chip-primary">📁 ${escapeHtml(profile.category)}</span>
          <span class="meta-chip">🏢 Entity: ${escapeHtml(profile.entity)}</span>
          <span class="meta-chip">📅 Period: ${escapeHtml(profile.reporting_period)}</span>
          <span class="meta-chip">📄 ${doc.page_count} Pages</span>
          <span class="meta-chip">💾 ${formatBytes(doc.file_size_bytes)}</span>
          <span class="meta-chip">🏷️ ${stats.total_facts} Grounded Facts</span>
          <span class="meta-chip meta-chip-corrob">✅ ${stats.corroborations_count} Corroborations</span>
          <span class="meta-chip meta-chip-contra">⚠️ ${stats.contradictions_count} Contradictions</span>
          <span class="meta-chip meta-chip-reconc">🔄 ${stats.reconciled_count} Reconciled</span>
        </div>
      </div>
    </div>

    <!-- Executive Briefing & Knowledge Layer Role -->
    <div class="dossier-briefing-box">
      <div class="briefing-row">
        <div class="briefing-label"><span>📌</span> Executive Document Briefing</div>
        <div class="briefing-text">${escapeHtml(profile.executive_summary)}</div>
      </div>
      <div class="briefing-row" style="margin-top: 14px;">
        <div class="briefing-label"><span>🎯</span> Role & Significance in Knowledge Layer</div>
        <div class="briefing-text">${escapeHtml(profile.role_in_knowledge_layer)}</div>
      </div>
      <div class="briefing-row" style="margin-top: 14px;">
        <div class="briefing-label"><span>⭐</span> Key Highlights & Stated Metrics</div>
        <div class="highlights-grid">
          ${highlightsHtml}
        </div>
      </div>
    </div>

    <!-- Sub-tabs Navigation -->
    <div class="dossier-subtabs">
      <button class="dossier-tab-btn active" data-subtab="${uid}_tab_facts">
        <span>🏷️</span> Extracted Facts (${facts.length})
      </button>
      <button class="dossier-tab-btn" data-subtab="${uid}_tab_rels">
        <span>🔗</span> Cross-Doc Connections (${rels.length})
      </button>
      <button class="dossier-tab-btn" data-subtab="${uid}_tab_source">
        <span>📖</span> Verbatim Source Pages (${pages.length})
      </button>
    </div>

    <!-- Sub-tab 1: Facts -->
    <div id="${uid}_tab_facts" class="dossier-tab-pane">
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Page</th>
              <th>Attribute</th>
              <th>Extracted Value</th>
              <th>Temporal Scope</th>
              <th>Verbatim Evidence Quote</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody>
            ${factsRowsHtml || '<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No facts extracted from this document.</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>

    <!-- Sub-tab 2: Relationships -->
    <div id="${uid}_tab_rels" class="dossier-tab-pane" style="display: none;">
      ${relsCardsHtml}
    </div>

    <!-- Sub-tab 3: Source Pages -->
    <div id="${uid}_tab_source" class="dossier-tab-pane" style="display: none;">
      <div class="page-pills">
        ${pagePillsHtml}
      </div>
      <div class="page-contents-wrapper">
        ${pageContentsHtml}
      </div>
    </div>
  `;

  // Attach Sub-tab switching events
  const tabBtns = container.querySelectorAll(".dossier-tab-btn");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const targetId = btn.getAttribute("data-subtab");
      container.querySelectorAll(".dossier-tab-pane").forEach(pane => {
        pane.style.display = pane.id === targetId ? "block" : "none";
      });
    });
  });

  // Attach Page Pills switching events
  const pagePills = container.querySelectorAll(".page-pill");
  pagePills.forEach(pill => {
    pill.addEventListener("click", () => {
      pagePills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      const targetPageId = pill.getAttribute("data-target");
      container.querySelectorAll(".page-content-pane").forEach(pane => {
        pane.style.display = pane.id === targetPageId ? "block" : "none";
      });
    });
  });
}

// 8. Filters & Search Handlers
function initFilters() {
  const searchInput = document.getElementById("fact-search-input");
  const docFilter = document.getElementById("fact-doc-filter");
  const entityFilter = document.getElementById("fact-entity-filter");
  const btnInspectFiltered = document.getElementById("btn-inspect-filtered-doc");
  const docQuickSelect = document.getElementById("doc-quick-select");

  function applyFactFilters() {
    const query = searchInput.value.toLowerCase().trim();
    const selectedDoc = docFilter.value;
    const selectedEntity = entityFilter.value;

    if (btnInspectFiltered) {
      if (selectedDoc) {
        btnInspectFiltered.style.display = "inline-flex";
        btnInspectFiltered.innerHTML = `<span>🔍</span> Inspect ${escapeHtml(selectedDoc.replace('.pdf', ''))}`;
      } else {
        btnInspectFiltered.style.display = "none";
      }
    }

    const filtered = cachedFacts.filter(f => {
      const matchDoc = !selectedDoc || f.document_name === selectedDoc;
      const matchEntity = !selectedEntity || f.entity === selectedEntity;
      const matchQuery = !query || (
        f.attribute.toLowerCase().includes(query) ||
        f.value.toLowerCase().includes(query) ||
        f.exact_quote.toLowerCase().includes(query) ||
        f.entity.toLowerCase().includes(query)
      );
      return matchDoc && matchEntity && matchQuery;
    });

    renderFactsTable(filtered);
  }

  searchInput.addEventListener("input", applyFactFilters);
  docFilter.addEventListener("change", applyFactFilters);
  entityFilter.addEventListener("change", applyFactFilters);

  if (btnInspectFiltered) {
    btnInspectFiltered.addEventListener("click", () => {
      if (docFilter.value) {
        openDocumentModal(docFilter.value);
      }
    });
  }

  if (docQuickSelect) {
    docQuickSelect.addEventListener("change", (e) => {
      if (e.target.value) {
        selectDocument(e.target.value, true);
      }
    });
  }

  // Tab 2 Relationship filter pills
  const pills = document.querySelectorAll(".filter-pill");
  pills.forEach(p => {
    p.addEventListener("click", () => {
      pills.forEach(x => x.classList.remove("active"));
      p.classList.add("active");
      const filterVal = p.getAttribute("data-filter");
      loadRelationships(filterVal);
    });
  });

  // Load Starter Dataset Button
  const btnStarter = document.getElementById("btn-load-starter");
  btnStarter.addEventListener("click", async () => {
    btnStarter.disabled = true;
    btnStarter.innerHTML = "<span>⏳</span> Ingesting Starter Set...";
    try {
      const res = await fetch("/api/load-starter", { method: "POST" });
      const data = await res.json();
      btnStarter.innerHTML = "<span>✅</span> Reloaded!";
      setTimeout(() => {
        btnStarter.disabled = false;
        btnStarter.innerHTML = "<span>⚡</span> Load Starter Dataset";
      }, 2000);
      loadAllData();
    } catch (e) {
      alert("Error loading starter dataset: " + e.message);
      btnStarter.disabled = false;
      btnStarter.innerHTML = "<span>⚡</span> Load Starter Dataset";
    }
  });
}

// 9. Modals (Upload, Settings & Document Dossier)
function initModals() {
  const uploadModal = document.getElementById("upload-modal");
  const settingsModal = document.getElementById("settings-modal");
  const docModal = document.getElementById("doc-dossier-modal");

  document.getElementById("btn-open-upload").addEventListener("click", () => {
    uploadModal.classList.add("open");
  });
  document.getElementById("upload-modal-close").addEventListener("click", () => {
    uploadModal.classList.remove("open");
  });
  document.getElementById("btn-cancel-upload").addEventListener("click", () => {
    uploadModal.classList.remove("open");
  });

  document.getElementById("btn-open-settings").addEventListener("click", async () => {
    try {
      const res = await fetch("/api/config");
      const cfg = await res.json();
      document.getElementById("settings-provider-select").value = cfg.provider;
      document.getElementById("settings-model-name").value = cfg.model || "gemini-3.6-flash";
    } catch (e) {}
    settingsModal.classList.add("open");
  });

  document.getElementById("settings-modal-close").addEventListener("click", () => {
    settingsModal.classList.remove("open");
  });

  if (docModal) {
    const docModalClose = document.getElementById("doc-dossier-modal-close");
    if (docModalClose) {
      docModalClose.addEventListener("click", () => {
        docModal.classList.remove("open");
      });
    }
    docModal.addEventListener("click", (e) => {
      if (e.target === docModal) {
        docModal.classList.remove("open");
      }
    });
  }

  document.getElementById("btn-save-settings").addEventListener("click", async () => {
    const provider = document.getElementById("settings-provider-select").value;
    const apiKey = document.getElementById("settings-api-key").value;
    const model = document.getElementById("settings-model-name").value;

    const fd = new FormData();
    fd.append("provider", provider);
    if (apiKey) fd.append("api_key", apiKey);
    if (model) fd.append("model", model);

    await fetch("/api/settings", { method: "POST", body: fd });
    settingsModal.classList.remove("open");
    alert("Settings updated successfully.");
  });
}

// 10. Drag and Drop PDF Upload
function initDropzone() {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("pdf-file-input");
  const submitBtn = document.getElementById("btn-submit-upload");
  const statusDiv = document.getElementById("upload-status");
  const statusText = document.getElementById("upload-status-text");

  let selectedFile = null;

  dropzone.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("click", (e) => e.stopPropagation());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files && fileInput.files[0]) {
      handleFileSelected(fileInput.files[0]);
    }
  });

  function handleFileSelected(file) {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      alert("Please choose a valid PDF file.");
      return;
    }
    selectedFile = file;
    document.getElementById("dropzone-label").innerText = `Selected: ${file.name}`;
    document.getElementById("dropzone-sub").innerText = `${(file.size / 1024).toFixed(1)} KB (Ready to process)`;
    submitBtn.disabled = false;
  }

  function resetDropzoneUI() {
    selectedFile = null;
    fileInput.value = "";
    document.getElementById("dropzone-label").innerText = "Drag and drop your PDF here";
    document.getElementById("dropzone-sub").innerText = "or click anywhere in this box to select a file";
    submitBtn.disabled = true;
    statusDiv.style.display = "none";
  }

  document.getElementById("btn-cancel-upload").addEventListener("click", resetDropzoneUI);
  document.getElementById("upload-modal-close").addEventListener("click", resetDropzoneUI);

  submitBtn.addEventListener("click", async () => {
    if (!selectedFile) return;

    submitBtn.disabled = true;
    statusDiv.style.display = "block";
    statusDiv.style.background = "#eff6ff";
    statusDiv.style.borderColor = "#bfdbfe";
    statusText.style.color = "var(--primary)";
    statusText.innerText = "Parsing PDF & incrementally reconciling facts with knowledge layer...";

    const fd = new FormData();
    fd.append("file", selectedFile);

    try {
      const res = await fetch("/api/upload", {
        method: "POST",
        body: fd
      });
      const data = await res.json();

      if (res.ok) {
        statusDiv.style.background = "#ecfdf5";
        statusDiv.style.borderColor = "#a7f3d0";
        statusText.style.color = "var(--corrob-color)";
        statusText.innerText = `✅ Ingested successfully! Extracted ${data.facts_extracted} facts.`;
        setTimeout(() => {
          document.getElementById("upload-modal").classList.remove("open");
          resetDropzoneUI();
          loadAllData();
        }, 1200);
      } else {
        statusDiv.style.background = "#fff1f2";
        statusDiv.style.borderColor = "#fecdd3";
        statusText.style.color = "var(--contra-color)";
        statusText.innerText = `Upload failed: ${data.detail || 'Unknown error'}`;
        submitBtn.disabled = false;
      }
    } catch (err) {
      statusDiv.style.background = "#fff1f2";
      statusDiv.style.borderColor = "#fecdd3";
      statusText.style.color = "var(--contra-color)";
      statusText.innerText = `Error: ${err.message}`;
      submitBtn.disabled = false;
    }
  });
}

// Utility Functions
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}
