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
            <span class="doc-name">📄 ${escapeHtml(evA.document_name)}</span>
            <span class="page-tag">Page ${evA.page_number}</span>
          </div>
          <div class="evidence-quote">"${escapeHtml(evA.exact_quote)}"</div>
          <div class="evidence-value">Extracted Value: <span style="color: var(--accent-cyan);">${escapeHtml(evA.value)}</span></div>
        </div>

        ${evB ? `
        <div class="evidence-box">
          <div class="evidence-source">
            <span class="doc-name">📄 ${escapeHtml(evB.document_name)}</span>
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
            <span class="doc-name">📄 ${escapeHtml(r.fact_a.document_name)}</span>
            <span class="page-tag">P.${r.fact_a.page_number}</span>
          </div>
          <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">${escapeHtml(r.fact_a.attribute)}</div>
          <div class="evidence-value">${escapeHtml(r.fact_a.value)}</div>
          <div class="evidence-quote" style="margin-top: 6px;">"${escapeHtml(r.fact_a.exact_quote)}"</div>
        </div>

        <div class="evidence-box">
          <div class="evidence-source">
            <span class="doc-name">📄 ${escapeHtml(r.fact_b.document_name)}</span>
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
        <span class="tag tag-doc">${escapeHtml(f.document_name)}</span><br/>
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

// 7. Documents List Loader
async function loadDocuments() {
  try {
    const res = await fetch("/api/documents");
    cachedDocuments = await res.json();
    const tbody = document.getElementById("docs-table-body");

    if (cachedDocuments.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No documents ingested yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = cachedDocuments.map(d => `
      <tr>
        <td style="font-family: var(--font-mono); font-weight: 600; color: var(--accent-cyan);">📄 ${escapeHtml(d.filename)}</td>
        <td>${d.page_count} pages</td>
        <td><b style="color: #10b981;">${d.fact_count} facts</b></td>
        <td style="font-size: 12px; color: var(--text-muted);">${formatBytes(d.file_size_bytes)}</td>
        <td style="font-size: 12px; color: var(--text-muted);">${escapeHtml(d.uploaded_at)}</td>
        <td style="font-size: 12px; color: #94a3b8; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
          ${escapeHtml(d.text_preview || '')}
        </td>
      </tr>
    `).join("");
  } catch (e) {
    console.error("Error loading documents:", e);
  }
}

// 8. Filters & Search Handlers
function initFilters() {
  const searchInput = document.getElementById("fact-search-input");
  const docFilter = document.getElementById("fact-doc-filter");
  const entityFilter = document.getElementById("fact-entity-filter");

  function applyFactFilters() {
    const query = searchInput.value.toLowerCase().trim();
    const selectedDoc = docFilter.value;
    const selectedEntity = entityFilter.value;

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

// 9. Modals (Upload & Settings)
function initModals() {
  const uploadModal = document.getElementById("upload-modal");
  const settingsModal = document.getElementById("settings-modal");

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
    if (!file.name.toLowerCase().endswith(".pdf")) {
      alert("Please choose a valid PDF file.");
      return;
    }
    selectedFile = file;
    dropzone.querySelector("p").innerText = `Selected: ${file.name}`;
    dropzone.querySelector(".stat-sub").innerText = `${(file.size / 1024).toFixed(1)} KB`;
    submitBtn.disabled = false;
  }

  submitBtn.addEventListener("click", async () => {
    if (!selectedFile) return;

    submitBtn.disabled = true;
    statusDiv.style.display = "block";
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
        statusText.innerText = `Ingested successfully! Extracted ${data.facts_extracted} facts.`;
        setTimeout(() => {
          document.getElementById("upload-modal").classList.remove("open");
          statusDiv.style.display = "none";
          selectedFile = null;
          fileInput.value = "";
          submitBtn.disabled = true;
          loadAllData();
        }, 1200);
      } else {
        statusText.innerText = `Upload failed: ${data.detail || 'Unknown error'}`;
        submitBtn.disabled = false;
      }
    } catch (err) {
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
