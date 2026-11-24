/**
 * @file admin.js
 * @description Single Page Application controller for Montazh Imperiya Admin Dashboard.
 * Includes XSS prevention, 401 token expiration interception, inline image previews,
 * lead triage with internal notes, and persistent upload history.
 */

const API_BASE = "";
let currentToken = localStorage.getItem("admin_token");
let allSections = [];
let activeSectionKey = null;
let hasUnsavedChanges = false;
let currentLeadFilter = "all";
let currentMediaGroup = "all";
let currentHistoryFilter = "all";
let allServerMedia = [];
let allFetchedLeads = [];
let activeModalLeadId = null;
const loadedLeadsMap = new Map();

const FIELD_LIMITS = {
  title: 120,
  subtitle: 300,
  description: 400,
  subtext: 300,
  lead: 300,
  cta_button: 40,
  button_text: 40,
  working_hours: 60,
  hours: 60,
  phone: 25,
  phone_clean: 16,
  email: 100,
  address: 200,
  inn: 250,
  tg_link: 250,
  wa_link: 250,
  name: 80,
  desc: 400,
  scope: 500,
  q: 200,
  a: 1500,
  val: 6,
  unit: 15,
  step: 10,
  features: 80
};

/**
 * Identifies media-only keys (managed exclusively in the "Медиа сайта" tab).
 */
function isMediaFieldKey(key) {
  return (
    key.includes("image") ||
    key.includes("photo") ||
    key.includes("logo") ||
    key.includes("icon") ||
    key.includes("poster") ||
    key.includes("video") ||
    key === "worker_yellow" ||
    key === "cables" ||
    key === "worker_helmet"
  );
}

function setUnsavedState(dirty) {
  hasUnsavedChanges = dirty;
  const pill = document.getElementById("unsaved-indicator");
  if (pill) pill.classList.toggle("show", dirty);
}

// ==========================================
// UTILITIES & SECURITY
// ==========================================

/**
 * Escapes unsafe characters to prevent Stored XSS attacks.
 * @param {string|any} str
 * @returns {string}
 */
function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Centralized fetch wrapper that intercepts 401 Unauthorized and network errors.
 */
async function authFetch(url, options = {}) {
  const token = localStorage.getItem("admin_token");
  if (!token) {
    redirectToLogin();
    throw new Error("No token");
  }

  const headers = Object.assign({}, options.headers || {}, {
    "Authorization": `Bearer ${token}`
  });

  try {
    const response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
      showToast("Срок сессии истек. Перенаправление на страницу входа...", true);
      localStorage.removeItem("admin_token");
      setTimeout(redirectToLogin, 1500);
      throw new Error("Session expired");
    }

    return response;
  } catch (err) {
    if (err.name === "TypeError" && String(err.message).toLowerCase().includes("fetch")) {
      showToast("Сервер бэкенда недоступен. Проверьте интернет-соединение.", true);
    }
    throw err;
  }
}

function redirectToLogin() {
  window.location.href = "/admin/login.html";
}

function showToast(message, isError = false) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.style.background = isError ? "#E02D37" : "#10B981";
  toast.classList.add("show");
  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

function formatDate(isoStr) {
  if (!isoStr) return "—";
  const d = new Date(isoStr);
  return d.toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });
}

// ==========================================
// INITIALIZATION & AUTH
// ==========================================
async function initAuth() {
  if (!currentToken) {
    redirectToLogin();
    return;
  }

  try {
    const res = await authFetch(`${API_BASE}/api/v1/auth/me`);
    if (!res.ok) throw new Error("Auth verification failed");
    const user = await res.json();
    const displayEl = document.getElementById("current-user-display");
    if (displayEl) {
      displayEl.textContent = user.username;
      displayEl.title = user.username;
      if (displayEl.parentElement) {
        displayEl.parentElement.title = `Вы вошли как: ${user.username}`;
      }
    }
  } catch (e) {
    // Handled in authFetch
  }
}

// ==========================================
// TABS NAVIGATION
// ==========================================
function setupTabs() {
  const tabButtons = document.querySelectorAll(".nav-tab-btn");
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      tabButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      const targetTab = btn.getAttribute("data-tab");
      document.querySelectorAll(".tab-pane").forEach(pane => {
        pane.style.display = (pane.id === targetTab) ? "block" : "none";
      });

      if (targetTab === "tab-leads") loadLeads();
      if (targetTab === "tab-content") {
        if (allSections.length === 0) {
          loadSections(true);
        } else if (!document.querySelector("#sections-list .section-menu-item")) {
          renderSectionsMenu(true);
        }
      }
      if (targetTab === "tab-media") {
        Promise.all([ensureSectionsLoaded(), fetchServerMediaList()])
          .then(() => renderSiteMediaSlots())
          .catch(() => renderSiteMediaSlots());
      }
      if (targetTab === "tab-media-history") {
        renderStoredMedia();
      }
    });
  });

  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      setUnsavedState(false);
      localStorage.removeItem("admin_token");
      localStorage.removeItem("admin_username");
      redirectToLogin();
    });
  }
}

// ==========================================
// TAB 1: LEADS DASHBOARD & CRM
// ==========================================
async function loadLeads() {
  const tbody = document.getElementById("leads-tbody");
  tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 2.5rem;">Загрузка списка заявок...</td></tr>`;

  try {
    const res = await authFetch(`${API_BASE}/api/v1/admin/leads?limit=200`);
    if (!res.ok) throw new Error("Failed to load leads");
    const data = await res.json();

    allFetchedLeads = data.leads || [];

    // Update stats counters
    document.getElementById("stat-total").textContent = data.total;
    document.getElementById("stat-new").textContent = data.new_count;
    document.getElementById("stat-processed").textContent = data.processed_count;

    const badge = document.getElementById("badge-new-leads");
    if (data.new_count > 0) {
      badge.textContent = data.new_count;
      badge.style.display = "inline-block";
    } else {
      badge.style.display = "none";
    }

    renderLeadsTable();
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: #ff6b74; padding: 2rem;">Ошибка загрузки заявок</td></tr>`;
  }
}

/**
 * Renders the leads table combining the active status filter and search query.
 */
function renderLeadsTable() {
  const tbody = document.getElementById("leads-tbody");
  const searchInput = document.getElementById("lead-search-input");
  const query = (searchInput ? searchInput.value : "").trim().toLowerCase();

  let filtered = allFetchedLeads;

  // Filter by status tab
  if (currentLeadFilter !== "all") {
    filtered = filtered.filter(l => l.status === currentLeadFilter);
  }

  // Filter by search query (name, phone, source, notes)
  if (query) {
    filtered = filtered.filter(l => {
      const name = (l.name || "").toLowerCase();
      const phone = (l.phone || "").toLowerCase();
      const source = (l.source || "").toLowerCase();
      const notes = (l.notes || "").toLowerCase();
      return name.includes(query) || phone.includes(query) || source.includes(query) || notes.includes(query);
    });
  }

  loadedLeadsMap.clear();

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 3rem;">Заявок не найдено.</td></tr>`;
    return;
  }

  tbody.innerHTML = "";
  filtered.forEach(lead => {
    loadedLeadsMap.set(lead.id, lead);
    const tr = document.createElement("tr");

    const isNew = lead.status === "new";
    const statusSelect = `
      <select class="status-select ${isNew ? 'new' : 'processed'}" onchange="changeLeadStatus(${lead.id}, this.value)" title="Нажмите, чтобы переключить статус заявки">
        <option value="new" ${isNew ? 'selected' : ''}>● Новая</option>
        <option value="processed" ${!isNew ? 'selected' : ''}>✓ Обработана</option>
      </select>
    `;

    // Phone with quick WhatsApp communication helper
    const safePhone = escapeHtml(lead.phone);
    const cleanDigits = String(lead.phone || '').replace(/\D/g, '');
    const waNumber = cleanDigits.startsWith('8') ? '7' + cleanDigits.slice(1) : cleanDigits;
    const waLink = waNumber.length >= 10
      ? `<a href="https://wa.me/${waNumber}" target="_blank" rel="noopener noreferrer" title="Написать клиенту в WhatsApp" style="text-decoration: none; font-size: 0.95rem; filter: drop-shadow(0 0 2px rgba(16,185,129,0.5));">💬</a>`
      : '';

    const safeName = escapeHtml(lead.name || '—');
    const safeSource = escapeHtml(lead.source);
    const safeNotes = escapeHtml(lead.notes || '');

    tr.innerHTML = `
      <td style="font-family: var(--font-mono); font-size: 0.8125rem;">#${lead.id}</td>
      <td style="color: var(--text-secondary);">${formatDate(lead.created_at)}</td>
      <td><strong>${safeName}</strong></td>
      <td>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <a href="tel:${safePhone}" style="color: #60A5FA; text-decoration: none; font-weight: 600;">${safePhone}</a>
          ${waLink}
        </div>
      </td>
      <td><span style="font-size: 0.75rem; background: var(--bg-input); padding: 0.2rem 0.5rem; border-radius: 4px; border: 1px solid var(--border-color);">${safeSource}</span></td>
      <td>${statusSelect}</td>
      <td>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <span style="font-size: 0.8125rem; color: ${safeNotes ? 'var(--text-primary)' : 'var(--text-muted)'}; max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${safeNotes}">
            ${safeNotes || '—'}
          </span>
          <button class="btn btn-secondary btn-sm" onclick="openNotesModal(${lead.id})" title="Изменить заметку" style="padding: 0.2rem 0.4rem;">
            ✏️
          </button>
        </div>
      </td>
      <td>
        <button class="btn btn-danger btn-sm" onclick="deleteLead(${lead.id})" title="Удалить заявку">✕</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

async function changeLeadStatus(leadId, newStatus) {
  try {
    const res = await authFetch(`${API_BASE}/api/v1/admin/leads/${leadId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus })
    });
    if (res.ok) {
      showToast(newStatus === "processed" ? "Заявка переведена в статус «Обработана»" : "Заявка возвращена в статус «Новая»");
      loadLeads();
    }
  } catch (e) {
    showToast("Не удалось обновить статус заявки", true);
    loadLeads();
  }
}

// ------------------------------------------
// MODAL: LEAD MANAGER NOTES
// ------------------------------------------
function openNotesModal(leadId) {
  activeModalLeadId = leadId;
  const lead = loadedLeadsMap.get(leadId);
  const currentNotes = (lead && lead.notes) ? lead.notes : "";

  const modal = document.getElementById("notes-modal");
  const title = document.getElementById("notes-modal-title");
  const textarea = document.getElementById("notes-modal-textarea");

  if (!modal || !textarea) return;

  title.textContent = `Заметка к заявке #${leadId}${lead && lead.name ? ' (' + lead.name + ')' : ''}`;
  textarea.value = currentNotes;
  modal.style.display = "flex";
  textarea.focus();
}

function closeNotesModal() {
  const modal = document.getElementById("notes-modal");
  if (modal) modal.style.display = "none";
  activeModalLeadId = null;
}

async function saveNotesFromModal() {
  if (!activeModalLeadId) return;
  const textarea = document.getElementById("notes-modal-textarea");
  const saveBtn = document.getElementById("notes-modal-save");
  const newNotes = textarea.value.trim();

  if (saveBtn) {
    saveBtn.disabled = true;
    saveBtn.innerHTML = "<span>Сохранение...</span>";
  }

  try {
    const res = await authFetch(`${API_BASE}/api/v1/admin/leads/${activeModalLeadId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ notes: newNotes })
    });
    if (res.ok) {
      showToast("Заметка менеджера успешно сохранена!");
      closeNotesModal();
      loadLeads();
    }
  } catch (e) {
    showToast("Ошибка сохранения заметки", true);
  } finally {
    if (saveBtn) {
      saveBtn.disabled = false;
      saveBtn.innerHTML = "<span>Сохранить заметку</span>";
    }
  }
}

function setupNotesModal() {
  const modal = document.getElementById("notes-modal");
  const closeBtn = document.getElementById("notes-modal-close");
  const cancelBtn = document.getElementById("notes-modal-cancel");
  const saveBtn = document.getElementById("notes-modal-save");

  if (closeBtn) closeBtn.addEventListener("click", closeNotesModal);
  if (cancelBtn) cancelBtn.addEventListener("click", closeNotesModal);
  if (saveBtn) saveBtn.addEventListener("click", saveNotesFromModal);

  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeNotesModal();
    });
  }
}

async function deleteLead(leadId) {
  if (!confirm(`Удалить заявку #${leadId}? Это действие нельзя отменить.`)) return;

  try {
    const res = await authFetch(`${API_BASE}/api/v1/admin/leads/${leadId}`, {
      method: "DELETE"
    });
    if (res.ok) {
      showToast(`Заявка #${leadId} удалена`);
      loadLeads();
    }
  } catch (e) {
    showToast("Ошибка при удалении заявки", true);
  }
}

function setupLeadFilters() {
  document.querySelectorAll(".filter-lead-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-lead-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentLeadFilter = btn.getAttribute("data-filter");
      renderLeadsTable();
    });
  });

  const searchInput = document.getElementById("lead-search-input");
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      renderLeadsTable();
    });
  }

  const refreshBtn = document.getElementById("refresh-leads-btn");
  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => {
      loadLeads();
      showToast("Список заявок обновлен");
    });
  }

  document.getElementById("export-csv-btn").addEventListener("click", async () => {
    try {
      const res = await authFetch(`${API_BASE}/api/v1/admin/leads/export-csv`);
      if (!res.ok) throw new Error("CSV Export failed");
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `leads_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      showToast("CSV файл с заявками успешно скачан!");
    } catch (e) {
      showToast("Ошибка экспорта CSV", true);
    }
  });
}

// ==========================================
// TAB 2: CONTENT EDITOR
// ==========================================
function renderSectionsMenu(selectFirst = true) {
  const menu = document.getElementById("sections-list");
  if (!menu) return;
  menu.innerHTML = `<div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700; margin-bottom: 0.75rem; padding-left: 0.5rem;">Секции страницы</div>`;

  allSections.forEach((sec, idx) => {
    const btn = document.createElement("button");
    const isActive = activeSectionKey ? (sec.section_key === activeSectionKey) : (idx === 0);
    btn.className = "section-menu-item" + (isActive ? " active" : "");
    btn.textContent = `${sec.order ? sec.order + '. ' : ''}${sec.title}`;
    btn.dataset.key = sec.section_key;
    btn.addEventListener("click", () => selectSection(sec.section_key));
    menu.appendChild(btn);
  });

  if (allSections.length > 0 && selectFirst) {
    selectSection(activeSectionKey || allSections[0].section_key, true);
  }
}

async function loadSections(selectFirst = true) {
  try {
    const res = await authFetch(`${API_BASE}/api/v1/admin/content`);
    if (!res.ok) throw new Error("Failed to load sections");
    allSections = await res.json();
    renderSectionsMenu(selectFirst);
  } catch (e) {
    showToast("Ошибка загрузки секций сайта", true);
  }
}

function selectSection(sectionKey, skipUnsavedCheck = false) {
  if (!skipUnsavedCheck && hasUnsavedChanges && activeSectionKey && activeSectionKey !== sectionKey) {
    if (!confirm("В текущей секции есть несохранённые изменения. Перейти без сохранения?")) {
      return;
    }
  }

  activeSectionKey = sectionKey;
  setUnsavedState(false);

  document.querySelectorAll(".section-menu-item").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.key === sectionKey);
  });

  const sec = allSections.find(s => s.section_key === sectionKey);
  if (!sec) return;

  document.getElementById("active-section-title").textContent = sec.title;
  renderSectionForm(sec);
}

/**
 * Validates a single editor input/textarea against backend schema rules.
 * Displays or clears inline error styling immediately.
 * @param {HTMLInputElement|HTMLTextAreaElement} input
 * @returns {string|null} Error message string or null if valid
 */
function validateEditorField(input) {
  const key = input.dataset.fieldKey || "";
  const val = (input.value || "").trim();
  const maxLen = FIELD_LIMITS[key] || 500;
  let err = null;

  if (!val) {
    err = "Поле не может быть пустым";
  } else if (val.toLowerCase().includes("<script")) {
    err = "Запрещены HTML-теги <script>";
  } else if (val.length > maxLen) {
    err = `Максимум ${maxLen} символов (сейчас ${val.length})`;
  } else if (key === "phone") {
    if (!/^[+\d\s()\-]+$/.test(val)) {
      err = "Допустимы только цифры, +, пробелы, скобки и дефисы";
    } else {
      const digits = val.replace(/\D/g, "");
      if (digits.length < 10 || digits.length > 15) {
        err = `Телефон должен содержать от 10 до 15 цифр (сейчас ${digits.length})`;
      }
    }
  } else if (key === "phone_clean") {
    const normalized = val.replace(/[\s()-]/g, "");
    if (!/^\+?\d{10,15}$/.test(normalized)) {
      err = "Формат для ссылки tel: +74232000000 (10–15 цифр без букв)";
    }
  } else if (key === "email") {
    if (!/^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,63}$/.test(val)) {
      err = "Некорректный Email (пример: info@montazh-imperia.ru)";
    }
  } else if (key === "tg_link" || key === "wa_link") {
    const low = val.toLowerCase();
    if (low.startsWith("javascript:") || low.startsWith("data:") || (!low.startsWith("https://") && !low.startsWith("http://"))) {
      err = "Ссылка должна начинаться с https:// или http://";
    }
  } else if (key === "val") {
    if (!/^\d{1,6}$/.test(val)) {
      err = "Введите только целое число (например: 12, 450, 98)";
    }
  }

  const errorEl = input.closest(".form-group, .sub-form-group")?.querySelector(".field-error-text");
  input.classList.toggle("is-invalid", Boolean(err));
  if (errorEl) {
    errorEl.textContent = err || "";
    errorEl.classList.toggle("show", Boolean(err));
  }
  return err;
}

/**
 * Normalizes a display phone string into tel: link format (+7XXXXXXXXXX).
 */
function normalizeCleanPhone(displayPhone) {
  let digits = String(displayPhone || "").replace(/\D/g, "");
  if (!digits) return "";
  if (digits.length === 11 && digits.startsWith("8")) {
    digits = "7" + digits.slice(1);
  }
  return "+" + digits;
}

/**
 * Shared helper that builds a validated text/contact input or textarea field.
 */
function createFieldControl({ key, path, value, compact = false }) {
  const isLongText = String(value).length > 70 || key.includes("desc") || key.includes("sub") || key.includes("scope") || key.includes("lead") || key === "a";
  const maxLen = FIELD_LIMITS[key] || 500;

  const wrapper = document.createElement("div");
  wrapper.className = compact ? "sub-form-group" : "form-group";
  if (compact) wrapper.style.marginBottom = "0.75rem";

  const label = document.createElement("label");
  if (compact) {
    label.style.cssText = "font-size: 0.75rem; color: var(--text-secondary); display: block; margin-bottom: 0.25rem;";
  }
  label.textContent = humanizeKey(key);
  wrapper.appendChild(label);

  const control = document.createElement(isLongText ? "textarea" : "input");
  if (!isLongText) control.type = key === "email" ? "email" : "text";
  control.className = "form-control";
  control.value = value ?? "";
  control.maxLength = maxLen;
  control.dataset.path = path;
  control.dataset.fieldKey = key;

  if (key === "phone") control.placeholder = "+7 (423) 200-00-00";
  if (key === "phone_clean") control.placeholder = "+74232000000";
  if (key === "val") control.placeholder = "Только число (например 450)";

  control.addEventListener("input", () => {
    setUnsavedState(true);
    validateEditorField(control);

    // Auto-sync phone_clean from display phone if present in the same form
    if (key === "phone") {
      const cleanInput = document.querySelector('#editor-fields-container [data-field-key="phone_clean"]');
      if (cleanInput && cleanInput.dataset.manualOverride !== "true") {
        const synced = normalizeCleanPhone(control.value);
        cleanInput.value = synced.slice(0, FIELD_LIMITS.phone_clean || 16);
        validateEditorField(cleanInput);
      }
    } else if (key === "phone_clean") {
      control.dataset.manualOverride = "true";
    }
  });

  control.addEventListener("blur", () => validateEditorField(control));
  wrapper.appendChild(control);

  if (key === "phone_clean") {
    const hint = document.createElement("div");
    hint.className = "field-hint";
    hint.textContent = "Синхронизируется автоматически при вводе телефона выше (формат: +7XXXXXXXXXX)";
    wrapper.appendChild(hint);
  }

  const errEl = document.createElement("div");
  errEl.className = "field-error-text";
  wrapper.appendChild(errEl);

  return wrapper;
}

function renderSectionForm(section) {
  const container = document.getElementById("editor-fields-container");
  container.innerHTML = "";

  const data = section.data || {};

  function buildFields(obj, prefix = "") {
    Object.entries(obj).forEach(([key, val]) => {
      // Media fields belong exclusively in the "Медиа сайта" tab
      if (isMediaFieldKey(key)) return;

      const fullPath = prefix ? `${prefix}.${key}` : key;

      if (typeof val === "string") {
        container.appendChild(createFieldControl({ key, path: fullPath, value: val }));
      } else if (Array.isArray(val)) {
        const arrayCard = document.createElement("div");
        arrayCard.style.cssText = "background: var(--bg-input); border: 1px solid var(--border-color); border-radius: 8px; padding: 1.25rem; margin-bottom: 1.5rem;";
        const header = document.createElement("div");
        header.style.cssText = "font-weight: 700; font-size: 0.875rem; margin-bottom: 1rem; color: var(--text-primary); text-transform: uppercase;";
        header.textContent = `Список: ${humanizeKey(key)} (${val.length} элементов)`;
        arrayCard.appendChild(header);

        let renderedItems = 0;
        val.forEach((item, itemIdx) => {
          const itemBox = document.createElement("div");
          itemBox.style.cssText = "background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 6px; padding: 1rem; margin-bottom: 0.75rem;";

          if (typeof item === "string") {
            itemBox.appendChild(createFieldControl({
              key,
              path: `${fullPath}.${itemIdx}`,
              value: item,
              compact: true
            }));
            renderedItems++;
            arrayCard.appendChild(itemBox);
          } else if (item && typeof item === "object") {
            const textEntries = Object.entries(item).filter(([subKey]) => !isMediaFieldKey(subKey));
            if (textEntries.length > 0) {
              textEntries.forEach(([subKey, subVal]) => {
                itemBox.appendChild(createFieldControl({
                  key: subKey,
                  path: `${fullPath}.${itemIdx}.${subKey}`,
                  value: subVal,
                  compact: true
                }));
              });
              renderedItems++;
              arrayCard.appendChild(itemBox);
            }
          }
        });

        if (renderedItems > 0) {
          container.appendChild(arrayCard);
        }
      } else if (val && typeof val === "object") {
        const textEntries = Object.entries(val).filter(([subKey]) => !isMediaFieldKey(subKey));
        if (textEntries.length === 0) return;

        const groupCard = document.createElement("div");
        groupCard.style.cssText = "background: var(--bg-input); border: 1px solid var(--border-color); border-radius: 8px; padding: 1.25rem; margin-bottom: 1.5rem;";
        const header = document.createElement("div");
        header.style.cssText = "font-weight: 700; font-size: 0.875rem; margin-bottom: 1rem; color: var(--text-primary); text-transform: uppercase;";
        header.textContent = humanizeKey(key);
        groupCard.appendChild(header);

        textEntries.forEach(([subKey, subVal]) => {
          groupCard.appendChild(createFieldControl({
            key: subKey,
            path: `${fullPath}.${subKey}`,
            value: subVal,
            compact: true
          }));
        });
        container.appendChild(groupCard);
      }
    });
  }

  buildFields(data);
}

function humanizeKey(key) {
  const dict = {
    title: "Заголовок",
    description: "Описание",
    subtitle: "Подзаголовок",
    subtext: "Поясняющий текст",
    cta_button: "Текст на кнопке",
    button_text: "Текст на кнопке",
    phone: "Номер телефона (для отображения)",
    phone_clean: "Номер телефона (для ссылки tel:)",
    working_hours: "Режим работы",
    email: "Электронная почта (Email)",
    address: "Фактический адрес",
    hours: "Часы работы",
    inn: "Реквизиты (ИНН / ОГРН)",
    lead: "Вводный текст (Lead)",
    name: "Название услуги / этапа",
    price: "Стоимость (тариф)",
    term: "Срок выполнения",
    desc: "Подробное описание",
    val: "Значение показателя (только число)",
    unit: "Единица измерения (лет, +, %)",
    step: "Номер шага",
    scope: "Состав выполненных работ",
    q: "Вопрос",
    a: "Ответ",
    tg_link: "Ссылка на Telegram",
    wa_link: "Ссылка на WhatsApp",
    features: "Ключевые преимущества",
    items: "Элементы"
  };
  return dict[key] || key;
}

/**
 * Extracts a human-readable error message from FastAPI JSON responses.
 */
function parseApiErrorMessage(errData, fallback) {
  if (!errData) return fallback;
  if (errData.detail) {
    if (typeof errData.detail === "string") return errData.detail;
    if (errData.detail.message) return errData.detail.message;
    if (Array.isArray(errData.detail) && errData.detail[0]?.msg) return errData.detail[0].msg;
  }
  return errData.message || fallback;
}

// Save active section
async function saveActiveSection() {
  if (!activeSectionKey) return;
  const sec = allSections.find(s => s.section_key === activeSectionKey);
  if (!sec) return;

  const inputs = Array.from(document.querySelectorAll("#editor-fields-container [data-path]"));
  let firstInvalid = null;
  let firstErrMsg = null;

  inputs.forEach(input => {
    const err = validateEditorField(input);
    if (err && !firstInvalid) {
      firstInvalid = input;
      firstErrMsg = err;
    }
  });

  if (firstInvalid) {
    firstInvalid.focus();
    firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
    showToast(`Ошибка валидации: ${firstErrMsg}`, true);
    return;
  }

  const saveBtn = document.getElementById("save-content-btn");
  saveBtn.disabled = true;
  saveBtn.innerHTML = "<span>Сохранение...</span>";

  // Deep clone data and strip any deprecated keys safely via validated assignment
  const updatedData = JSON.parse(JSON.stringify(sec.data));
  inputs.forEach(input => {
    const path = input.dataset.path.split(".");
    let target = updatedData;
    for (let i = 0; i < path.length - 1; i++) {
      target = target[path[i]];
    }
    target[path[path.length - 1]] = input.value.trim();
  });

  try {
    const res = await authFetch(`${API_BASE}/api/v1/admin/content/${activeSectionKey}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data: updatedData })
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      const msg = parseApiErrorMessage(errData, "Проверьте корректность введенных данных");
      if (errData?.detail?.errors && Array.isArray(errData.detail.errors)) {
        errData.detail.errors.forEach(e => {
          const matchInput = document.querySelector(`#editor-fields-container [data-path="${e.field}"]`);
          if (matchInput) {
            matchInput.classList.add("is-invalid");
            const errEl = matchInput.closest(".form-group, .sub-form-group")?.querySelector(".field-error-text");
            if (errEl) {
              errEl.textContent = e.message;
              errEl.classList.add("show");
            }
          }
        });
      }
      showToast(msg, true);
      return;
    }

    const savedSection = await res.json();
    sec.data = savedSection.data || updatedData;
    setUnsavedState(false);
    showToast(`Секция «${sec.title}» успешно сохранена и опубликована!`);
  } catch (e) {
    showToast("Ошибка соединения при сохранении данных", true);
  } finally {
    saveBtn.disabled = false;
    saveBtn.innerHTML = "<span>💾 Сохранить секцию</span>";
  }
}

// ==========================================
// TAB 3: SITE MEDIA MANAGER & SERVER ARCHIVE
// ==========================================

/**
 * Resolves a dotted object path safely (e.g. "items.0.image").
 */
function getByPath(obj, path) {
  return path.split(".").reduce((acc, part) => (acc != null ? acc[part] : undefined), obj);
}

/**
 * Sets a dotted object path inside a cloned section data object.
 */
function setByPath(obj, path, val) {
  const parts = path.split(".");
  let target = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    if (target[parts[i]] == null) return false;
    target = target[parts[i]];
  }
  target[parts[parts.length - 1]] = val;
  return true;
}

/**
 * Builds the catalog of every editable image, icon, logo, and video slot on the landing page.
 */
function getSiteMediaSlots() {
  const secMap = new Map(allSections.map(s => [s.section_key, s]));
  const slots = [];

  const addSlot = ({ group, badge, title, sectionKey, path, defaultSrc, kind = "image", cover = false }) => {
    const sec = secMap.get(sectionKey);
    const currentSrc = (sec && sec.data) ? getByPath(sec.data, path) : defaultSrc;
    slots.push({
      id: `${sectionKey}:${path}`,
      group,
      badge,
      title,
      sectionKey,
      path,
      defaultSrc,
      currentSrc: currentSrc || defaultSrc,
      kind,
      cover
    });
  };

  // Hero & Branding
  addSlot({ group: "brand", badge: "Шапка", title: "Логотип в шапке и мобильном меню", sectionKey: "header", path: "logo_image", defaultSrc: "/icons/logo-header-hd.png" });
  addSlot({ group: "brand", badge: "Hero", title: "Фоновое loop-видео (главный экран)", sectionKey: "hero", path: "bg_video", defaultSrc: "/videos/hero-bg.mp4", kind: "video", cover: true });
  addSlot({ group: "brand", badge: "Hero", title: "Постер-заставка (до загрузки видео Hero)", sectionKey: "hero", path: "bg_poster", defaultSrc: "/images/hero-rack-bg.jpg", cover: true });
  addSlot({ group: "brand", badge: "Подвал", title: "Логотип компании в подвале", sectionKey: "contacts", path: "footer_logo", defaultSrc: "/images/footer-logo-mi.png" });

  // 01 Expertise (3 cards)
  const expItems = secMap.get("expertise")?.data?.items || [];
  const expDefaults = ["/images/clean-icon-shield.png", "/images/clean-icon-doc.png", "/images/clean-icon-box.png"];
  expItems.forEach((item, idx) => {
    addSlot({
      group: "services",
      badge: "01 Экспертиза",
      title: `Иконка карточки: ${item.title || `#${idx + 1}`}`,
      sectionKey: "expertise",
      path: `items.${idx}.image`,
      defaultSrc: expDefaults[idx] || "/images/clean-icon-shield.png"
    });
  });

  // 02 Services (7 cards) + CTA banner
  const srvItems = secMap.get("services")?.data?.items || [];
  const srvDefaults = [
    "/images/service-cctv.png", "/images/service-skud.png", "/images/service-alarm.png",
    "/images/service-intercom.png", "/images/service-fire.png", "/images/service-sks.png", "/images/service-electro.png"
  ];
  srvItems.forEach((item, idx) => {
    addSlot({
      group: "services",
      badge: "02 Услуги",
      title: `Услуга: ${item.name || `#${idx + 1}`}`,
      sectionKey: "services",
      path: `items.${idx}.image`,
      defaultSrc: srvDefaults[idx] || "/images/service-cctv.png"
    });
  });
  addSlot({ group: "services", badge: "CTA-баннеры", title: "3D-рендер оборудования на красных баннерах", sectionKey: "services", path: "banner_image", defaultSrc: "/images/banner-3d-hardware.png" });

  // 03 Why Us (3 ticker photos) & 04 Steps (3D illustration)
  addSlot({ group: "steps", badge: "03 Почему мы", title: "Лента фото #1 (монтажник в жёлтой каске)", sectionKey: "why_us", path: "ticker_photos.worker_yellow", defaultSrc: "/images/section03-worker-yellow.png", cover: true });
  addSlot({ group: "steps", badge: "03 Почему мы", title: "Лента фото #2 (кабельные трассы)", sectionKey: "why_us", path: "ticker_photos.cables", defaultSrc: "/images/section03-cables.png", cover: true });
  addSlot({ group: "steps", badge: "03 Почему мы", title: "Лента фото #3 (инженер в белой каске)", sectionKey: "why_us", path: "ticker_photos.worker_helmet", defaultSrc: "/images/section03-worker-helmet.png", cover: true });
  addSlot({ group: "steps", badge: "04 Этапы", title: "Большая 3D-композиция справа в «Этапах работы»", sectionKey: "steps", path: "illustration_image", defaultSrc: "/images/section04-installation-3d.png" });

  // 05 Sectors (4 photos + 4 icons + 5 partner logos)
  const sectorItems = secMap.get("sectors")?.data?.items || [];
  const sectorImgDefaults = ["/images/sector-commercial.png", "/images/sector-social.png", "/images/sector-admin.png", "/images/sector-industrial.png"];
  const sectorIconDefaults = ["/images/sector-icon-home.png", "/images/sector-icon-building.png", "/images/sector-icon-factory.png", "/images/sector-icon-cube.png"];
  sectorItems.forEach((item, idx) => {
    addSlot({
      group: "sectors",
      badge: "05 Сферы",
      title: `Фото сферы: ${item.title || `#${idx + 1}`}`,
      sectionKey: "sectors",
      path: `items.${idx}.image`,
      defaultSrc: sectorImgDefaults[idx] || "/images/sector-commercial.png",
      cover: true
    });
    addSlot({
      group: "sectors",
      badge: "05 Иконки",
      title: `Иконка сферы: ${item.title || `#${idx + 1}`}`,
      sectionKey: "sectors",
      path: `items.${idx}.icon`,
      defaultSrc: sectorIconDefaults[idx] || "/images/sector-icon-home.png"
    });
  });

  const partnerLogos = secMap.get("sectors")?.data?.partner_logos || [];
  const partnerNames = ["ФССП", "Сбербанк", "МЧС", "Газпром", "Т-Банк"];
  const partnerDefaults = [
    "/images/logos/logo-fssp.png", "/images/logos/logo-sber.png", "/images/logos/logo-mchs.png",
    "/images/logos/logo-gazprom.png", "/images/logos/logo-tbank.png"
  ];
  partnerLogos.forEach((_, idx) => {
    addSlot({
      group: "sectors",
      badge: "Партнёры",
      title: `Логотип партнёра #${idx + 1} (${partnerNames[idx] || "бегущая строка"})`,
      sectionKey: "sectors",
      path: `partner_logos.${idx}`,
      defaultSrc: partnerDefaults[idx] || "/images/logos/logo-sber.png"
    });
  });

  // 06 Cases (3 cards) & 07 Engineer CTA + Success modal
  const caseItems = secMap.get("cases")?.data?.items || [];
  const caseDefaults = ["/images/case-1.jpg", "/images/case-2.jpg", "/images/case-3.png"];
  caseItems.forEach((item, idx) => {
    addSlot({
      group: "cases",
      badge: "06 Кейсы",
      title: `Кейс #${idx + 1}: ${item.title || "Объект"}`,
      sectionKey: "cases",
      path: `items.${idx}.image`,
      defaultSrc: caseDefaults[idx] || "/images/case-1.jpg",
      cover: true
    });
  });
  addSlot({ group: "cases", badge: "07 Формы", title: "Фото инженера (секция 07 и окно заявки)", sectionKey: "engineer_cta", path: "engineer_photo", defaultSrc: "/images/section07-engineer.jpg", cover: true });
  addSlot({ group: "cases", badge: "Модалка", title: "3D-фон окна «Заявка отправлена»", sectionKey: "engineer_cta", path: "success_bg_image", defaultSrc: "/images/success-3d-bg.png", cover: true });

  return slots;
}

/**
 * Collects every media URL currently referenced by all site sections.
 */
function collectActiveMediaUrls() {
  const urls = new Set();
  function walk(val) {
    if (typeof val === "string" && (val.startsWith("/uploads/") || val.startsWith("/images/") || val.startsWith("/videos/") || val.startsWith("/icons/"))) {
      urls.add(val);
    } else if (Array.isArray(val)) {
      val.forEach(walk);
    } else if (val && typeof val === "object") {
      Object.values(val).forEach(walk);
    }
  }
  allSections.forEach(sec => walk(sec.data));
  return urls;
}

async function fetchServerMediaList() {
  const res = await authFetch(`${API_BASE}/api/v1/admin/upload`);
  if (!res.ok) throw new Error("Failed to fetch media");
  const data = await res.json();
  allServerMedia = data.files || [];
  return allServerMedia;
}

function findSlotMeta(sectionKey, fieldPath) {
  if (!sectionKey || !fieldPath) return null;
  return getSiteMediaSlots().find(s => s.sectionKey === sectionKey && s.path === fieldPath) || null;
}

function setupMediaUploader() {
  const filterContainer = document.getElementById("media-group-filters");
  if (filterContainer) {
    filterContainer.querySelectorAll("button[data-group]").forEach(btn => {
      btn.addEventListener("click", () => {
        filterContainer.querySelectorAll("button").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        currentMediaGroup = btn.getAttribute("data-group") || "all";
        renderSiteMediaSlots();
      });
    });
  }

  const searchInput = document.getElementById("media-slot-search");
  if (searchInput) {
    searchInput.addEventListener("input", () => renderSiteMediaSlots());
  }

  const refreshSlotsBtn = document.getElementById("refresh-site-media-btn");
  if (refreshSlotsBtn) {
    refreshSlotsBtn.addEventListener("click", async () => {
      await Promise.all([loadSections(false), fetchServerMediaList().catch(() => [])]);
      await renderSiteMediaSlots();
      showToast("Медиа-карта сайта обновлена");
    });
  }

  // History tab filters, search & refresh
  const histFilters = document.getElementById("history-filters");
  if (histFilters) {
    histFilters.querySelectorAll("button[data-hfilter]").forEach(btn => {
      btn.addEventListener("click", () => {
        histFilters.querySelectorAll("button").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        currentHistoryFilter = btn.getAttribute("data-hfilter") || "all";
        renderStoredMedia(false);
      });
    });
  }

  const histSearch = document.getElementById("history-search-input");
  if (histSearch) {
    histSearch.addEventListener("input", () => renderStoredMedia(false));
  }

  const refreshHistBtn = document.getElementById("refresh-media-btn");
  if (refreshHistBtn) {
    refreshHistBtn.addEventListener("click", async () => {
      await renderStoredMedia(true);
      showToast("История медиа обновлена");
    });
  }

  // Slot Quick History Picker modal controls
  const modal = document.getElementById("slot-history-modal");
  const closeBtn = document.getElementById("slot-history-close");
  const cancelBtn = document.getElementById("slot-history-cancel");
  if (closeBtn) closeBtn.addEventListener("click", closeSlotHistoryModal);
  if (cancelBtn) cancelBtn.addEventListener("click", closeSlotHistoryModal);
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeSlotHistoryModal();
    });
  }
}

function closeSlotHistoryModal() {
  const modal = document.getElementById("slot-history-modal");
  if (modal) modal.style.display = "none";
}

function openSlotHistoryModal(slot, historyItems) {
  const modal = document.getElementById("slot-history-modal");
  const titleEl = document.getElementById("slot-history-title");
  const listEl = document.getElementById("slot-history-list");
  if (!modal || !listEl) return;

  titleEl.textContent = `Прошлые версии: ${slot.title}`;
  listEl.innerHTML = "";

  historyItems.forEach(item => {
    const card = document.createElement("div");
    card.className = "preview-card";
    const isVideo = item.content_type.startsWith("video/");
    const mediaHtml = isVideo
      ? `<video src="${escapeHtml(item.url)}" muted loop autoplay playsinline style="width:100%;height:125px;object-fit:cover;background:#000;"></video>`
      : `<img src="${escapeHtml(item.url)}" alt="${escapeHtml(item.original_name || item.filename)}" style="width:100%;height:125px;object-fit:cover;background:#0B0D11;" onerror="this.src='/favicon.ico';">`;

    const displayName = item.original_name || item.filename;
    const whenText = formatDate(item.last_used_at || item.created_at);

    card.innerHTML = `
      ${mediaHtml}
      <div class="preview-info">
        <div class="history-file-name" title="${escapeHtml(displayName)}">
          ${escapeHtml(displayName)}
        </div>
        <div style="color: var(--text-muted); font-size: 0.72rem; margin-bottom: 0.65rem;">
          ${escapeHtml(whenText)} • ${Math.max(1, Math.round(item.size_bytes / 1024))} КБ
        </div>
        <button type="button" class="btn btn-primary btn-sm btn-block restore-picker-btn" style="margin-top: auto;">
          ⚡ Вернуть на сайт
        </button>
      </div>
    `;

    card.querySelector(".restore-picker-btn").addEventListener("click", async (e) => {
      const btn = e.currentTarget;
      btn.disabled = true;
      btn.textContent = "⏳ Возврат...";
      try {
        await replaceSiteMediaSlot(slot, item.url);
        closeSlotHistoryModal();
        showToast(`Вернули прошлую версию: ${slot.title}`);
        await Promise.all([fetchServerMediaList(), renderSiteMediaSlots()]);
      } catch (err) {
        showToast(`Ошибка возврата: ${err.message}`, true);
        btn.disabled = false;
        btn.textContent = "⚡ Вернуть на сайт";
      }
    });

    listEl.appendChild(card);
  });

  modal.style.display = "flex";
}

/**
 * Ensures sections are loaded before rendering site media slots.
 */
async function ensureSectionsLoaded() {
  if (allSections.length > 0) return;
  const res = await authFetch(`${API_BASE}/api/v1/admin/content`);
  if (!res.ok) throw new Error("Failed to load content");
  allSections = await res.json();
}

/**
 * Saves an updated media URL straight into the target section on the backend.
 */
async function replaceSiteMediaSlot(slot, newUrl) {
  await ensureSectionsLoaded();
  const sec = allSections.find(s => s.section_key === slot.sectionKey);
  if (!sec) throw new Error(`Секция ${slot.sectionKey} не найдена`);

  const updatedData = JSON.parse(JSON.stringify(sec.data));
  setByPath(updatedData, slot.path, newUrl);

  const res = await authFetch(`${API_BASE}/api/v1/admin/content/${slot.sectionKey}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ data: updatedData })
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(parseApiErrorMessage(errData, "Не удалось обновить медиа в секции"));
  }

  const saved = await res.json();
  sec.data = saved.data || updatedData;

  // Keep open section editor synchronized if it is displaying this section
  if (activeSectionKey === slot.sectionKey && !hasUnsavedChanges) {
    renderSectionForm(sec);
  }
}

/**
 * Renders the visual Site Media Manager grid (every image/icon/logo/video slot on the landing page).
 */
async function renderSiteMediaSlots() {
  const grid = document.getElementById("site-media-slots-grid");
  if (!grid) return;

  try {
    await ensureSectionsLoaded();
    if (allServerMedia.length === 0) {
      await fetchServerMediaList().catch(() => []);
    }
  } catch (e) {
    grid.innerHTML = `<p style="color: #ff6b74; padding: 1.5rem 0;">Не удалось загрузить секции сайта с сервера.</p>`;
    return;
  }

  const query = (document.getElementById("media-slot-search")?.value || "").trim().toLowerCase();
  const slots = getSiteMediaSlots().filter(slot => {
    const matchGroup = currentMediaGroup === "all" || slot.group === currentMediaGroup;
    const matchQuery = !query || slot.title.toLowerCase().includes(query) || slot.badge.toLowerCase().includes(query) || slot.currentSrc.toLowerCase().includes(query);
    return matchGroup && matchQuery;
  });

  if (slots.length === 0) {
    grid.innerHTML = `<p style="color: var(--text-muted); padding: 1.5rem 0;">Подходящих медиа-слотов не найдено.</p>`;
    return;
  }

  grid.innerHTML = "";
  slots.forEach(slot => {
    const card = document.createElement("div");
    card.className = "media-slot-card";
    const isCustom = slot.currentSrc !== slot.defaultSrc;
    const isVideo = slot.kind === "video";
    const slotHistory = allServerMedia.filter(
      m => m.section_key === slot.sectionKey && m.field_path === slot.path && m.url !== slot.currentSrc
    );

    const previewWrap = document.createElement("div");
    previewWrap.className = `media-slot-preview${slot.cover ? " cover-mode" : ""}`;

    if (isVideo) {
      const vid = document.createElement("video");
      vid.src = slot.currentSrc;
      vid.autoplay = true;
      vid.loop = true;
      vid.muted = true;
      vid.playsInline = true;
      previewWrap.appendChild(vid);
    } else {
      const img = document.createElement("img");
      img.src = slot.currentSrc;
      img.alt = slot.title;
      img.onerror = () => { img.src = "/favicon.ico"; };
      previewWrap.appendChild(img);
    }

    const badge = document.createElement("span");
    badge.className = "media-slot-badge";
    badge.textContent = slot.badge;
    previewWrap.appendChild(badge);

    if (isCustom) {
      const dot = document.createElement("span");
      dot.className = "media-slot-custom-dot";
      dot.textContent = "ЗАМЕНЕНО";
      previewWrap.appendChild(dot);
    }

    const body = document.createElement("div");
    body.className = "media-slot-body";

    const titleEl = document.createElement("div");
    titleEl.className = "media-slot-title";
    titleEl.textContent = slot.title;

    const pathEl = document.createElement("div");
    pathEl.className = "media-slot-path";
    pathEl.title = slot.currentSrc;
    pathEl.textContent = slot.currentSrc;

    const actions = document.createElement("div");
    actions.className = "media-slot-actions";

    const replaceBtn = document.createElement("button");
    replaceBtn.type = "button";
    replaceBtn.className = "btn btn-primary btn-sm";
    replaceBtn.style.flex = "1";
    replaceBtn.textContent = isVideo ? "🎬 Заменить" : "📁 Заменить";

    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.style.display = "none";
    fileInput.accept = isVideo ? "video/mp4,video/webm" : "image/jpeg,image/png,image/webp";

    const handleSlotUpload = async (file) => {
      replaceBtn.disabled = true;
      replaceBtn.textContent = "⏳ Загрузка...";
      try {
        const uploaded = await uploadFileDirect(file, isVideo ? "video" : "image", slot);
        await replaceSiteMediaSlot(slot, uploaded.url);
        showToast(`Обновлено на сайте: ${slot.title}`);
        await fetchServerMediaList();
        await renderSiteMediaSlots();
      } catch (err) {
        showToast(`Ошибка: ${err.message}`, true);
        replaceBtn.disabled = false;
        replaceBtn.textContent = isVideo ? "🎬 Заменить" : "📁 Заменить";
      }
    };

    replaceBtn.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", () => {
      if (fileInput.files && fileInput.files[0]) {
        handleSlotUpload(fileInput.files[0]);
        fileInput.value = "";
      }
    });

    // Support intuitive Drag & Drop straight onto the target card
    card.addEventListener("dragover", (e) => {
      e.preventDefault();
      card.classList.add("dragover");
    });
    card.addEventListener("dragleave", () => card.classList.remove("dragover"));
    card.addEventListener("drop", (e) => {
      e.preventDefault();
      card.classList.remove("dragover");
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleSlotUpload(e.dataTransfer.files[0]);
      }
    });

    actions.appendChild(replaceBtn);
    actions.appendChild(fileInput);

    if (slotHistory.length > 0) {
      const historyBtn = document.createElement("button");
      historyBtn.type = "button";
      historyBtn.className = "btn btn-secondary btn-sm";
      historyBtn.title = `Прошлые загруженные версии (${slotHistory.length})`;
      historyBtn.textContent = `🕘 ${slotHistory.length}`;
      historyBtn.addEventListener("click", () => openSlotHistoryModal(slot, slotHistory));
      actions.appendChild(historyBtn);
    }

    if (isCustom) {
      const resetBtn = document.createElement("button");
      resetBtn.type = "button";
      resetBtn.className = "btn btn-secondary btn-sm";
      resetBtn.title = "Вернуть стандартный файл сайта";
      resetBtn.textContent = "↺ Сбросить";
      resetBtn.addEventListener("click", async () => {
        resetBtn.disabled = true;
        try {
          await replaceSiteMediaSlot(slot, slot.defaultSrc);
          showToast(`Восстановлено стандартное медиа: ${slot.title}`);
          await fetchServerMediaList();
          await renderSiteMediaSlots();
        } catch (err) {
          showToast(`Ошибка сброса: ${err.message}`, true);
          resetBtn.disabled = false;
        }
      });
      actions.appendChild(resetBtn);
    }

    body.appendChild(titleEl);
    body.appendChild(pathEl);
    body.appendChild(actions);

    card.appendChild(previewWrap);
    card.appendChild(body);
    grid.appendChild(card);
  });
}

/**
 * Direct file upload handler that validates type/size, optimizes images into WebP,
 * and records target landing slot metadata when provided.
 */
async function uploadFileDirect(file, expectedKind = "any", slotMeta = null) {
  if (file.size > 25 * 1024 * 1024) {
    throw new Error("Размер файла превышает 25 МБ");
  }
  const type = (file.type || "").toLowerCase();
  if (expectedKind === "video" && !type.startsWith("video/")) {
    throw new Error("Для этого слота требуется видео (MP4 или WebM)");
  }
  if (expectedKind === "image" && !type.startsWith("image/")) {
    throw new Error("Для этого слота требуется изображение (JPG, PNG или WebP)");
  }

  const formData = new FormData();
  formData.append("file", file);
  if (slotMeta?.sectionKey) formData.append("section_key", slotMeta.sectionKey);
  if (slotMeta?.path) formData.append("field_path", slotMeta.path);

  const res = await authFetch(`${API_BASE}/api/v1/admin/upload`, {
    method: "POST",
    body: formData
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(parseApiErrorMessage(err, "Ошибка загрузки файла"));
  }

  return await res.json();
}

async function deleteMediaFromHistory(filenameToDelete) {
  const targetItem = allServerMedia.find(f => f.filename === filenameToDelete);
  const inUseUrls = collectActiveMediaUrls();
  const isUsed = Boolean(targetItem?.is_active) || inUseUrls.has(`/uploads/${filenameToDelete}`);
  const promptMsg = isUsed
    ? `ВНИМАНИЕ: файл «${targetItem?.original_name || filenameToDelete}» сейчас ИСПОЛЬЗУЕТСЯ на сайте! Сначала замените его или сбросьте слот, иначе на сайте пропадёт картинка/видео. Всё равно удалить навсегда?`
    : `Удалить файл «${targetItem?.original_name || filenameToDelete}» с сервера и из истории?`;

  if (!confirm(promptMsg)) return;

  try {
    const res = await authFetch(`${API_BASE}/api/v1/admin/upload/${encodeURIComponent(filenameToDelete)}`, {
      method: "DELETE"
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(parseApiErrorMessage(err, "Не удалось удалить файл"));
    }
    showToast("Файл удален с сервера и из истории");
    await renderStoredMedia(true);
  } catch (e) {
    showToast(e.message, true);
  }
}

async function restoreMediaFromHistory(fileData) {
  if (!fileData.section_key || !fileData.field_path) {
    showToast("У этого файла нет сохранённой привязки к слоту", true);
    return;
  }
  const slotMeta = findSlotMeta(fileData.section_key, fileData.field_path) || {
    sectionKey: fileData.section_key,
    path: fileData.field_path,
    title: `${fileData.section_key} → ${fileData.field_path}`
  };

  await replaceSiteMediaSlot(slotMeta, fileData.url);
  showToast(`Восстановлено на сайт: ${slotMeta.title}`);
  await renderStoredMedia(true);
}

async function renderStoredMedia(forceFetch = true) {
  const grid = document.getElementById("uploaded-grid");
  if (!grid) return;

  try {
    await ensureSectionsLoaded().catch(() => {});
    if (forceFetch || allServerMedia.length === 0) {
      await fetchServerMediaList();
    }

    const query = (document.getElementById("history-search-input")?.value || "").trim().toLowerCase();
    const filtered = allServerMedia.filter(fileData => {
      if (currentHistoryFilter === "active" && !fileData.is_active) return false;
      if (currentHistoryFilter === "archived" && fileData.is_active) return false;
      if (query) {
        const slotMeta = findSlotMeta(fileData.section_key, fileData.field_path);
        const hay = `${fileData.original_name || ""} ${fileData.filename} ${slotMeta?.title || ""} ${slotMeta?.badge || ""} ${fileData.section_key || ""}`.toLowerCase();
        if (!hay.includes(query)) return false;
      }
      return true;
    });

    if (allServerMedia.length === 0) {
      grid.innerHTML = `<p style="color: var(--text-muted); padding: 1rem 0;">История пока пуста — здесь появятся все загруженные вами фото и видео для блоков сайта.</p>`;
      return;
    }

    if (filtered.length === 0) {
      grid.innerHTML = `<p style="color: var(--text-muted); padding: 1rem 0;">По выбранному фильтру файлов не найдено.</p>`;
      return;
    }

    grid.innerHTML = "";
    filtered.forEach(fileData => {
      const card = document.createElement("div");
      card.className = "preview-card";
      const isVideo = fileData.content_type.startsWith("video/");
      const slotMeta = findSlotMeta(fileData.section_key, fileData.field_path);
      const slotLabel = slotMeta
        ? `${slotMeta.badge}: ${slotMeta.title}`
        : (fileData.section_key ? `${fileData.section_key} → ${fileData.field_path || ""}` : "Без привязки к слоту");
      const displayName = fileData.original_name || fileData.filename;
      const whenLabel = formatDate(fileData.last_used_at || fileData.created_at);

      const mediaPreview = isVideo
        ? `<video src="${escapeHtml(fileData.url)}" muted loop playsinline></video>`
        : `<img src="${escapeHtml(fileData.url)}" alt="${escapeHtml(displayName)}" onerror="this.src='/favicon.ico';">`;

      card.innerHTML = `
        <button class="preview-delete-btn" onclick="deleteMediaFromHistory('${escapeHtml(fileData.filename)}')" title="Удалить файл с сервера">✕</button>
        ${mediaPreview}
        <div class="preview-info">
          <div class="history-slot-badge" title="${escapeHtml(slotLabel)}">📌 ${escapeHtml(slotLabel)}</div>
          <div class="history-file-name" title="${escapeHtml(fileData.filename)}">
            ${escapeHtml(displayName)}
          </div>
          <div style="color: var(--text-muted); font-size: 0.72rem; margin-bottom: 0.45rem;">
            ${escapeHtml(whenLabel)} • ${Math.max(1, Math.round(fileData.size_bytes / 1024))} КБ
          </div>
          <div class="history-actions-slot"></div>
        </div>
      `;

      const actionsSlot = card.querySelector(".history-actions-slot");
      if (fileData.is_active) {
        const activeTag = document.createElement("span");
        activeTag.className = "media-in-use-tag";
        activeTag.style.marginBottom = "0";
        activeTag.style.flex = "1";
        activeTag.style.textAlign = "center";
        activeTag.textContent = "● Сейчас на сайте";
        actionsSlot.appendChild(activeTag);
      } else if (fileData.section_key && fileData.field_path) {
        const restoreBtn = document.createElement("button");
        restoreBtn.type = "button";
        restoreBtn.className = "btn btn-primary btn-sm";
        restoreBtn.style.flex = "1";
        restoreBtn.textContent = "⚡ Вернуть на сайт";
        restoreBtn.addEventListener("click", async () => {
          restoreBtn.disabled = true;
          restoreBtn.textContent = "⏳...";
          try {
            await restoreMediaFromHistory(fileData);
          } catch (err) {
            showToast(`Ошибка возврата: ${err.message}`, true);
            restoreBtn.disabled = false;
            restoreBtn.textContent = "⚡ Вернуть на сайт";
          }
        });
        actionsSlot.appendChild(restoreBtn);
      }

      const copyBtn = document.createElement("button");
      copyBtn.type = "button";
      copyBtn.className = "btn btn-secondary btn-sm";
      copyBtn.title = "Скопировать URL файла";
      copyBtn.textContent = "📋";
      copyBtn.addEventListener("click", () => copyToClipboard(fileData.url));
      actionsSlot.appendChild(copyBtn);

      grid.appendChild(card);
    });
  } catch (e) {
    grid.innerHTML = `<p style="color: #ff6b74; padding: 1rem 0;">Ошибка загрузки истории медиафайлов с сервера.</p>`;
  }
}

function copyToClipboard(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      showToast(`Скопировано: ${text}`);
    }).catch(() => {
      prompt("Скопируйте URL вручную:", text);
    });
  } else {
    prompt("Скопируйте URL вручную:", text);
  }
}

// ==========================================
// BACKGROUND NEW LEADS NOTIFIER
// ==========================================
function startLeadNotifier() {
  // Silent background check every 30 seconds
  setInterval(async () => {
    if (!localStorage.getItem("admin_token")) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/admin/leads?limit=1`, {
        headers: { "Authorization": `Bearer ${localStorage.getItem("admin_token")}` }
      });
      if (res.ok) {
        const data = await res.json();
        const badge = document.getElementById("badge-new-leads");
        if (badge) {
          if (data.new_count > 0) {
            badge.textContent = data.new_count;
            badge.style.display = "inline-block";
          } else {
            badge.style.display = "none";
          }
        }
      }
    } catch (e) {}
  }, 30000);
}

// ==========================================
// INIT & EVENT BINDINGS
// ==========================================
document.addEventListener("DOMContentLoaded", async () => {
  await initAuth();
  setupTabs();
  setupLeadFilters();
  setupNotesModal();
  setupMediaUploader();
  loadLeads();
  renderStoredMedia();
  startLeadNotifier();

  const saveBtn = document.getElementById("save-content-btn");
  if (saveBtn) {
    saveBtn.addEventListener("click", saveActiveSection);
  }

  // Keyboard shortcut: Ctrl+S / Cmd+S to save content section, Esc to close modal
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
      const contentTab = document.getElementById("tab-content");
      if (contentTab && contentTab.style.display !== "none") {
        e.preventDefault();
        saveActiveSection();
      }
    }
    if (e.key === "Escape") {
      closeNotesModal();
      closeSlotHistoryModal();
    }
  });

  window.addEventListener("beforeunload", (e) => {
    if (hasUnsavedChanges) {
      e.preventDefault();
      e.returnValue = "";
    }
  });
});
