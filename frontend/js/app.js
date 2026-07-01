/**
 * Narrative Arc Intelligence Suite — Frontend Application
 * Pure Vanilla JS ES6+  |  No frameworks  |  Escalent EVForward
 */

'use strict';

// ═══════════════════════════════════════════════════════════════════════════
// Constants & Config
// ═══════════════════════════════════════════════════════════════════════════

const API = {
  health:    '/api/v1/health',
  config:    '/api/v1/config',
  scenarios: '/api/v1/scenarios',
  analyze:   '/api/v1/analyze',
  backtest:  '/api/v1/backtest',
  reports:   '/api/v1/evidence/reports',
  exportPdf: '/api/export/pdf',
};

// ═══════════════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════════════

const State = {
  currentScenario:   'baseline',
  currentNarrative:  null,
  currentQuestion:   '',
  reports:           [],
  activeFilter:      'all',
  isLoading:         false,
};

// ═══════════════════════════════════════════════════════════════════════════
// DOM helpers
// ═══════════════════════════════════════════════════════════════════════════

const $  = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

function el(tag, attrs = {}, ...children) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class')    e.className = v;
    else if (k === 'html') e.innerHTML = v;  // Only used for safe, non-user content
    else                   e.setAttribute(k, v);
  }
  for (const c of children) {
    if (c == null) continue;
    e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
  }
  return e;
}

function setText(sel, text) {
  const node = $(sel);
  if (node) node.textContent = text;
}

function show(sel) { const n = $(sel); if (n) n.hidden = false; n && n.classList.remove('hidden'); }
function hide(sel) { const n = $(sel); if (n) n.hidden = true;  n && n.classList.add('hidden'); }

// ═══════════════════════════════════════════════════════════════════════════
// API helpers
// ═══════════════════════════════════════════════════════════════════════════

async function apiFetch(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// ═══════════════════════════════════════════════════════════════════════════
// Status chip
// ═══════════════════════════════════════════════════════════════════════════

function setStatus(text, type = 'ready') {
  const chip = $('#status-chip');
  if (!chip) return;
  chip.textContent = `● ${text}`;
  chip.className = 'status-chip' + (type !== 'ready' ? ` ${type}` : '');
}

// ═══════════════════════════════════════════════════════════════════════════
// Loading overlay
// ═══════════════════════════════════════════════════════════════════════════

function showLoading(msg = 'Processing…', progressId = null) {
  State.isLoading = true;
  if (progressId) {
    const wrap = document.getElementById(progressId);
    if (wrap) {
      wrap.hidden = false;
      const msgEl = wrap.querySelector('.inline-progress-msg');
      if (msgEl) msgEl.textContent = msg;
    }
  }
}

function hideLoading(progressId = null) {
  State.isLoading = false;
  if (progressId) {
    const wrap = document.getElementById(progressId);
    if (wrap) wrap.hidden = true;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Toast notifications
// ═══════════════════════════════════════════════════════════════════════════

function toast(message, type = 'info', duration = 4000) {
  const container = $('#toast-container');
  if (!container) return;
  const t = el('div', { class: `toast toast--${type}`, role: 'alert' }, message);
  container.appendChild(t);
  setTimeout(() => {
    t.style.opacity = '0';
    t.style.transform = 'translateY(12px)';
    t.style.transition = '300ms ease';
    setTimeout(() => t.remove(), 320);
  }, duration);
}

// ═══════════════════════════════════════════════════════════════════════════
// Navigation: active link + scroll shadow
// ═══════════════════════════════════════════════════════════════════════════

function initNav() {
  const nav = $('#main-nav');

  // Shadow on scroll
  window.addEventListener('scroll', () => {
    if (window.scrollY > 10) nav.classList.add('scrolled');
    else nav.classList.remove('scrolled');
  }, { passive: true });

  // Active link via IntersectionObserver
  const sections = $$('section[id]');
  const links = $$('.nav-link');

  const obs = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        links.forEach(l => l.classList.remove('active'));
        const active = links.find(l => l.getAttribute('href') === `#${entry.target.id}`);
        if (active) active.classList.add('active');
      }
    }
  }, { rootMargin: `-${62}px 0px -55% 0px` });

  sections.forEach(s => obs.observe(s));
}

// ═══════════════════════════════════════════════════════════════════════════
// Scenario selector
// ═══════════════════════════════════════════════════════════════════════════

async function loadScenarios() {
  try {
    const data = await apiFetch(API.scenarios);
    renderScenarios(data.scenarios);
  } catch (e) {
    console.error('Failed to load scenarios:', e);
    renderScenariosFallback();
  }
}

function renderScenarios(scenarios) {
  const container = $('#scenario-selector');
  if (!container) return;
  container.innerHTML = '';

  for (const s of scenarios) {
    const isSelected = s.id === State.currentScenario;
    const wrapper = el('label', { class: `scenario-option${isSelected ? ' selected' : ''}` });

    const radio = el('input');
    radio.type = 'radio';
    radio.name = 'scenario';
    radio.value = s.id;
    radio.checked = isSelected;
    radio.setAttribute('aria-label', s.label);

    const textDiv = el('div', { class: 'scenario-text' });
    textDiv.appendChild(el('div', { class: 'scenario-option-label' }, s.label));
    textDiv.appendChild(el('div', { class: 'scenario-option-desc' }, s.description));

    wrapper.appendChild(radio);
    wrapper.appendChild(textDiv);

    wrapper.addEventListener('click', () => {
      State.currentScenario = s.id;
      $$('.scenario-option').forEach(o => o.classList.remove('selected'));
      wrapper.classList.add('selected');
    });

    container.appendChild(wrapper);
  }
}

function renderScenariosFallback() {
  const fallback = [
    { id: 'baseline',              label: 'Baseline — Current Market Conditions', description: '' },
    { id: 'ev_subsidies_rollback', label: 'Federal EV Subsidies Roll Back',       description: '' },
    { id: 'gas_prices_spike',      label: 'Gas Prices Spike 20 %',               description: '' },
  ];
  renderScenarios(fallback);
}

// ═══════════════════════════════════════════════════════════════════════════
// Question input
// ═══════════════════════════════════════════════════════════════════════════

function initQuestionInput() {
  const ta = $('#question-input');
  const cc = $('#char-count');
  if (!ta) return;

  ta.addEventListener('input', () => {
    const len = ta.value.length;
    if (cc) cc.textContent = `${len} / 500`;
  });

  // Quick-start buttons
  $$('.ql-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      ta.value = btn.dataset.q;
      ta.dispatchEvent(new Event('input'));
      ta.focus();
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Narrative generation
// ═══════════════════════════════════════════════════════════════════════════

async function analyzeNarrative() {
  const question = ($('#question-input') || {}).value?.trim();
  if (!question || question.length < 10) {
    toast('Please enter a question of at least 10 characters.', 'error');
    $('#question-input')?.focus();
    return;
  }

  State.currentQuestion = question;
  showLoading('Generating your strategic narrative…', 'analyze-progress');

  try {
    const data = await apiFetch(API.analyze, {
      method: 'POST',
      body: JSON.stringify({ question, scenario: State.currentScenario }),
    });

    State.currentNarrative = data;
    renderNarrative(data);

    // Enable PDF export
    const exportBtn = $('#export-btn');
    if (exportBtn) exportBtn.disabled = false;

    toast('Narrative generated successfully!', 'success');
    // Scroll to narrative section
    document.getElementById('narrative')?.scrollIntoView({ behavior: 'smooth' });

  } catch (err) {
    console.error('Analysis error:', err);
    toast(`Analysis failed: ${err.message}`, 'error');
  } finally {
    hideLoading('analyze-progress');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Narrative rendering
// ═══════════════════════════════════════════════════════════════════════════

function renderNarrative(data) {
  // Show results, hide empty state
  hide('#narrative-empty');
  show('#narrative-results');

  // Meta bar
  renderNarrativeMeta(data.meta);

  // Summary
  if (data.narrative_summary) {
    const bar = $('#narrative-summary-bar');
    const txt = $('#narrative-summary-text');
    if (bar) bar.hidden = false;
    if (txt) txt.textContent = data.narrative_summary;
  }

  // Acts
  renderAct('act1-content', data.act1, 'FACT');
  renderAct('act2-content', data.act2, 'SIGNAL');
  renderAct('act3-content', data.act3, 'RECOMMENDATION');

  // Sources
  renderSources(data.sources);
}

function renderNarrativeMeta(meta) {
  const container = $('#narrative-meta');
  if (!container) return;
  container.innerHTML = '';

  const chips = [
    { label: meta.provider },
    { label: meta.model },
    { label: `${meta.latency_ms.toFixed(0)} ms` },
    { label: new Date(meta.generated_at_utc).toLocaleTimeString() },
  ];

  for (const c of chips) {
    container.appendChild(el('span', { class: 'meta-chip' }, c.label));
  }
}

function renderAct(containerId, items, primaryType) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = '';

  if (!items || items.length === 0) {
    container.appendChild(el('p', { class: 'empty-desc' }, 'No items in this act.'));
    return;
  }

  for (const item of items) {
    const card = buildNarrativeItem(item);
    container.appendChild(card);
  }
}

function buildNarrativeItem(item) {
  const wrapper = el('div', { class: `narrative-item narrative-item--${item.type}` });

  const topRow = el('div', { class: 'item-top-row' });

  // Type tag
  topRow.appendChild(el('span', { class: `item-tag tag--${item.type}` }, item.type));

  // Priority badge for recommendations
  if (item.type === 'RECOMMENDATION' && item.priority != null) {
    topRow.appendChild(el('span', { class: 'item-priority' }, `P${item.priority}`));
  }

  wrapper.appendChild(topRow);
  wrapper.appendChild(el('p', { class: 'item-text' }, item.text));

  // Source chip
  if (item.source) {
    const srcEl = el('span', { class: 'item-source', tabindex: '0', role: 'button',
      'aria-label': `Jump to source: ${item.source}` }, `↗ ${item.source}`);
    srcEl.addEventListener('click', () => jumpToSourceReport(item.source));
    srcEl.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') jumpToSourceReport(item.source); });
    wrapper.appendChild(srcEl);
  }

  return wrapper;
}

function renderSources(sources) {
  const section = document.getElementById('sources-section');
  const list    = document.getElementById('sources-list');
  if (!section || !list) return;

  if (!sources || sources.length === 0) {
    section.hidden = true;
    return;
  }

  section.hidden = false;
  list.innerHTML = '';

  for (const src of sources) {
    const isEv  = src.category === 'EVForward Research';
    const chip  = el('button', {
      class: `source-chip ${isEv ? 'source-chip--evforward' : 'source-chip--market'}`,
      type: 'button',
      'aria-label': `Jump to ${src.title}`,
      'data-report-id': isEv ? `evforward-${src.year}` : `market-events-${src.year}`,
    });

    chip.appendChild(el('span', {}, src.title));
    chip.appendChild(el('span', { class: 'sc-year' }, ` (${src.year})`));

    chip.addEventListener('click', () => {
      const reportId = chip.dataset.reportId;
      openReportOverlayById(reportId);
    });

    list.appendChild(chip);
  }
}

function jumpToSourceReport(sourceText) {
  // Try to extract year from source string like "EVForward 2024 / Section"
  const yearMatch = sourceText.match(/20\d{2}/);
  if (!yearMatch) return;
  const year = yearMatch[0];
  const isEv = /evforward|research/i.test(sourceText);
  const reportId = isEv ? `evforward-${year}` : `market-events-${year}`;
  openReportOverlayById(reportId);
}

function openReportOverlayById(reportId) {
  const report = State.reports.find(r => r.report_id === reportId);
  if (report) openReportOverlay(report);
}

// ═══════════════════════════════════════════════════════════════════════════
// Evidence Hub
// ═══════════════════════════════════════════════════════════════════════════

async function loadReports() {
  try {
    const data = await apiFetch(API.reports);
    State.reports = data.reports || [];
    renderReportChips(State.reports);
    renderReportPanels(State.reports);
  } catch (e) {
    console.error('Failed to load reports:', e);
    const chips = $('#report-chips');
    if (chips) chips.innerHTML = '<p style="color:var(--text-muted);font-size:13px;">Reports unavailable.</p>';
  }
}

function renderReportChips(reports) {
  const container = $('#report-chips');
  if (!container) return;
  container.innerHTML = '';

  const filtered = State.activeFilter === 'all'
    ? reports
    : reports.filter(r => r.category === State.activeFilter);

  for (const report of filtered) {
    const isEv  = report.category === 'EVForward Research';
    const chip  = el('button', {
      class: `report-chip ${isEv ? 'report-chip--ev' : 'report-chip--mkt'}`,
      type: 'button',
      'data-report-id': report.report_id,
      'aria-label': `Jump to ${report.title}`,
    });
    chip.appendChild(el('span', {}, isEv ? '📊' : '📈'));
    chip.appendChild(el('span', {}, report.title.replace(' Core Report', '').replace(' Market Event Bank', '')));
    chip.appendChild(el('span', { class: 'chip-year' }, report.year));

    chip.addEventListener('click', () => jumpToReportPanel(report.report_id));
    container.appendChild(chip);
  }
}

function renderReportPanels(reports) {
  const container = $('#report-panels');
  if (!container) return;
  container.innerHTML = '';

  const filtered = State.activeFilter === 'all'
    ? reports
    : reports.filter(r => r.category === State.activeFilter);

  for (const report of filtered) {
    container.appendChild(buildReportPanel(report));
  }
}

function buildReportPanel(report) {
  const isEv      = report.category === 'EVForward Research';
  const panelId   = `panel-${report.report_id}`;
  const headClass = isEv ? 'rp-header--ev' : 'rp-header--mkt';

  const panel = el('div', {
    class: 'report-panel',
    id: panelId,
    'data-report-id': report.report_id,
  });

  // Header (clickable)
  const header = el('div', { class: `rp-header ${headClass}`, tabindex: '0',
    role: 'button', 'aria-expanded': 'false', 'aria-controls': `body-${report.report_id}` });

  const titleGroup = el('div', { class: 'rp-title-group' });
  titleGroup.appendChild(el('span', { class: 'rp-badge' }, isEv ? 'EVForward' : 'Market Signals'));
  const titleMeta = el('div');
  titleMeta.appendChild(el('div', { class: 'rp-title' }, report.title));
  titleMeta.appendChild(el('div', { class: 'rp-meta' }, `${report.entry_count} data points · ${report.year}`));
  titleGroup.appendChild(titleMeta);

  const toggle = el('span', { class: 'rp-toggle', 'aria-hidden': 'true' }, '›');
  header.appendChild(titleGroup);
  header.appendChild(toggle);

  const body = el('div', { class: 'rp-body', id: `body-${report.report_id}` });

  // Highlights
  if (report.highlights && report.highlights.length > 0) {
    const hlSection = el('div', { class: 'rp-highlights' });
    hlSection.appendChild(el('div', { class: 'rp-hl-title' }, 'Key Highlights'));
    for (const hl of report.highlights) {
      hlSection.appendChild(el('div', { class: 'rp-hl-item' }, hl));
    }
    body.appendChild(hlSection);
  }

  // "Open full report" button
  const openBtn = el('button', { class: 'rp-open-btn', type: 'button',
    'aria-label': `Open full report: ${report.title}` },
    '📄 Open full report');
  openBtn.addEventListener('click', e => {
    e.stopPropagation();
    openReportOverlay(report);
  });
  body.appendChild(openBtn);

  panel.appendChild(header);
  panel.appendChild(body);

  // Toggle behaviour
  const doToggle = () => {
    const isOpen = body.classList.toggle('open');
    toggle.classList.toggle('open', isOpen);
    header.setAttribute('aria-expanded', String(isOpen));
  };
  header.addEventListener('click', doToggle);
  header.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); doToggle(); } });

  return panel;
}

function jumpToReportPanel(reportId) {
  const panel = document.getElementById(`panel-${reportId}`);
  if (!panel) return;

  // Highlight
  panel.classList.add('panel-highlight');
  setTimeout(() => panel.classList.remove('panel-highlight'), 2200);

  // Open body
  const body   = panel.querySelector('.rp-body');
  const toggle = panel.querySelector('.rp-toggle');
  const header = panel.querySelector('.rp-header');
  if (body && !body.classList.contains('open')) {
    body.classList.add('open');
    toggle && toggle.classList.add('open');
    header && header.setAttribute('aria-expanded', 'true');
  }

  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });

  // Activate chip
  $$('.report-chip').forEach(c => c.classList.remove('chip-active'));
  const chip = $(`.report-chip[data-report-id="${reportId}"]`);
  if (chip) chip.classList.add('chip-active');
}

// ═══════════════════════════════════════════════════════════════════════════
// Report Overlay
// ═══════════════════════════════════════════════════════════════════════════

function openReportOverlay(report) {
  const overlay  = $('#report-overlay');
  const titleEl  = $('#overlay-title');
  const metaEl   = $('#overlay-meta');
  const bodyEl   = $('#overlay-body');
  if (!overlay) return;

  if (titleEl) titleEl.textContent = report.title;
  if (metaEl)  metaEl.textContent  = `${report.category} · ${report.year} · ${report.entry_count} data points`;

  if (bodyEl) {
    // Display full content with highlighted matches if a question is active
    const content = report.full_content || '(Content not available)';
    bodyEl.innerHTML = '';
    bodyEl.appendChild(buildHighlightedContent(content, State.currentQuestion));
  }

  overlay.hidden = false;
  document.body.style.overflow = 'hidden';

  // Focus the close button
  setTimeout(() => $('#overlay-close')?.focus(), 80);
}

function closeReportOverlay() {
  const overlay = $('#report-overlay');
  if (overlay) overlay.hidden = true;
  document.body.style.overflow = '';
}

function buildHighlightedContent(text, query) {
  if (!query) {
    const pre = el('pre');
    pre.style.cssText = 'white-space:pre-wrap;word-break:break-word;font-size:12px;line-height:1.7';
    pre.textContent = text;
    return pre;
  }

  // Highlight query keywords in content
  const keywords = query
    .replace(/[^a-zA-Z0-9 ]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 3)
    .slice(0, 8);

  if (keywords.length === 0) {
    const pre = el('pre');
    pre.style.cssText = 'white-space:pre-wrap;word-break:break-word;font-size:12px;line-height:1.7';
    pre.textContent = text;
    return pre;
  }

  const pattern = new RegExp(`(${keywords.map(escapeRe).join('|')})`, 'gi');
  const container = el('div');
  container.style.cssText = 'white-space:pre-wrap;word-break:break-word;font-size:12px;line-height:1.7';

  const parts = text.split(pattern);
  for (const part of parts) {
    if (pattern.test(part)) {
      pattern.lastIndex = 0;
      const mark = el('mark', { class: 'highlight-match' }, part);
      container.appendChild(mark);
    } else {
      container.appendChild(document.createTextNode(part));
    }
  }
  return container;
}

function escapeRe(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// ═══════════════════════════════════════════════════════════════════════════
// Filter bar (Evidence Hub)
// ═══════════════════════════════════════════════════════════════════════════

function initFilterBar() {
  $$('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      State.activeFilter = btn.dataset.filter;
      $$('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderReportChips(State.reports);
      renderReportPanels(State.reports);
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Validation / Backtest
// ═══════════════════════════════════════════════════════════════════════════

async function runBacktest() {
  const yearEl  = $('#backtest-year');
  const questEl = $('#backtest-question');
  const year     = yearEl?.value;
  const question = questEl?.value?.trim() || 'What were the key EV market developments?';

  if (!year) { toast('Please select a year.', 'error'); return; }

  showLoading(`Running validation for ${year}…`, 'backtest-progress');

  try {
    const data = await apiFetch(API.backtest, {
      method: 'POST',
      body: JSON.stringify({ year, question }),
    });
    renderBacktest(data);
    toast(`Validation for ${year} complete.`, 'success');
    document.getElementById('validation')?.scrollIntoView({ behavior: 'smooth' });
  } catch (err) {
    toast(`Validation failed: ${err.message}`, 'error');
  } finally {
    hideLoading('backtest-progress');
  }
}

function renderBacktest(data) {
  hide('#validation-empty');
  show('#validation-results');

  // Accuracy note
  const noteEl = $('#accuracy-note');
  if (noteEl) {
    if (data.accuracy_note) {
      noteEl.hidden  = false;
      noteEl.textContent = `Analysis Note: ${data.accuracy_note}`;
    } else {
      noteEl.hidden = true;
    }
  }

  renderBacktestItems('#predicted-list', data.predicted);
  renderBacktestItems('#actual-list',    data.actual);

  const metaEl = $('#validation-meta');
  if (metaEl && data.meta) {
    metaEl.textContent =
      `${data.meta.provider} · ${data.meta.latency_ms.toFixed(0)} ms · ${data.meta.request_id.slice(0, 8)}`;
  }
}

function renderBacktestItems(containerSel, items) {
  const container = $(containerSel);
  if (!container) return;
  container.innerHTML = '';

  if (!items || items.length === 0) {
    container.appendChild(el('p', { class: 'empty-desc' }, 'No items.'));
    return;
  }

  for (const item of items) {
    const card = el('div', { class: 'vp-item' });
    card.appendChild(el('div', { class: 'vp-label' }, item.label));
    card.appendChild(el('div', { class: 'vp-text'  }, item.text));
    if (item.source) card.appendChild(el('div', { class: 'vp-source' }, item.source));
    container.appendChild(card);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// PDF Export
// ═══════════════════════════════════════════════════════════════════════════

async function exportPDF() {
  const question = State.currentQuestion || ($('#question-input') || {}).value?.trim();
  if (!question) {
    toast('Run an analysis first before exporting.', 'error');
    return;
  }

  showLoading('Generating PDF report…', 'analyze-progress');
  try {
    const res = await fetch(API.exportPdf, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, scenario: State.currentScenario }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = `narrative_arc_${new Date().toISOString().slice(0,10)}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast('PDF downloaded!', 'success');
  } catch (err) {
    toast(`PDF export failed: ${err.message}`, 'error');
  } finally {
    hideLoading('analyze-progress');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Health check on startup
// ═══════════════════════════════════════════════════════════════════════════

async function checkHealth() {
  try {
    const data = await apiFetch(API.health);
    setStatus(`Ready · ${data.provider}`, 'ready');
  } catch {
    setStatus('API offline', 'error');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Wire event listeners
// ═══════════════════════════════════════════════════════════════════════════

function wireEvents() {
  // Analyze button
  $('#analyze-btn')?.addEventListener('click', analyzeNarrative);

  // Export button
  $('#export-btn')?.addEventListener('click', exportPDF);

  // Backtest button
  $('#backtest-btn')?.addEventListener('click', runBacktest);

  // Overlay close
  $('#overlay-close')?.addEventListener('click', closeReportOverlay);
  $('#overlay-backdrop')?.addEventListener('click', closeReportOverlay);

  // Escape key closes overlay
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      const ov = $('#report-overlay');
      if (ov && !ov.hidden) closeReportOverlay();
    }
  });

  // Enter key on question textarea → analyze
  $('#question-input')?.addEventListener('keydown', e => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      analyzeNarrative();
    }
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Bootstrap
// ═══════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', async () => {
  initNav();
  initQuestionInput();
  wireEvents();
  initFilterBar();

  // Parallel load
  await Promise.allSettled([
    checkHealth(),
    loadScenarios(),
    loadReports(),
  ]);
});
