const state = { records: [], filtered: [], page: 0, pageSize: 40, translations: new Set() };
const search = document.querySelector('#search');
const kind = document.querySelector('#kind');
const list = document.querySelector('#file-list');
const count = document.querySelector('#archive-count');
const pageInfo = document.querySelector('#page-info');
const prev = document.querySelector('#prev');
const next = document.querySelector('#next');
const archive = window.ArchiveUI;

function rank(item) {
  const featuredIndex = Object.keys(archive.featuredLabels).indexOf(item.path);
  if (featuredIndex >= 0) return featuredIndex;
  const name = item.path.split('/').at(-1).toLowerCase();
  if (name === 'summary.json') return 10;
  if (name === 'frames.csv') return 11;
  if (name === 'settings.json' || name === 'manifest.json') return 12;
  if (item.kind === 'report') return 20;
  if (item.kind === 'code') return 30;
  if (item.kind === 'data') return 40;
  if (item.kind === 'media') return 50;
  return 60;
}

function order(a, b) {
  return rank(a) - rank(b) || a.path.localeCompare(b.path, 'en');
}

function humanSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function render() {
  const pages = Math.max(1, Math.ceil(state.filtered.length / state.pageSize));
  state.page = Math.min(state.page, pages - 1);
  const visible = state.filtered.slice(state.page * state.pageSize, (state.page + 1) * state.pageSize);
  list.replaceChildren();
  if (!visible.length) {
    const empty = document.createElement('p');
    empty.className = 'file-empty';
    empty.textContent = 'No matching files. Try a run ID, method, date, or file type.';
    list.append(empty);
  }
  for (const item of visible) {
    const details = archive.describeFile(item);
    const row = document.createElement('a');
    row.className = 'file-row';
    row.href = archive.openUrl(item.path);
    row.target = '_blank';
    row.rel = 'noopener';
    row.setAttribute('aria-label', `${details.title}. ${item.path}`);
    const title = document.createElement('span');
    title.className = 'file-name';
    title.textContent = details.title;
    const sub = document.createElement('small');
    sub.className = 'file-path';
    sub.textContent = item.path;
    title.append(sub);
    if (state.translations.has(item.path)) {
      const badge = document.createElement('span');
      badge.className = 'translation-badge';
      badge.textContent = 'EN';
      badge.title = 'English reading edition available';
      title.append(badge);
    }
    const type = document.createElement('span');
    type.className = 'file-kind';
    type.textContent = ({data:'Data',code:'Code',report:'Report',media:'Media',backup:'Backup'})[item.kind] || item.kind;
    const size = document.createElement('span');
    size.className = 'file-size';
    size.textContent = humanSize(item.size);
    row.append(title, type, size);
    list.append(row);
  }
  count.textContent = `${state.filtered.length.toLocaleString('en-US')} files found · ${state.records.length.toLocaleString('en-US')} indexed`;
  pageInfo.textContent = `Page ${state.page + 1} of ${pages}`;
  prev.disabled = state.page === 0;
  next.disabled = state.page + 1 >= pages;
}

function filter() {
  const term = search.value.trim().toLocaleLowerCase();
  const selectedKind = kind.value;
  state.filtered = state.records.filter(item => {
    if (selectedKind !== 'all' && item.kind !== selectedKind) return false;
    if (!term) return true;
    const details = archive.describeFile(item);
    return `${item.path} ${details.title} ${details.context} ${details.role}`.toLocaleLowerCase().includes(term);
  }).sort(order);
  state.page = 0;
  render();
}

search.addEventListener('input', filter);
kind.addEventListener('change', filter);
prev.addEventListener('click', () => { state.page--; render(); });
next.addEventListener('click', () => { state.page++; render(); });

Promise.all([
  fetch('./catalog.json').then(response => { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.json(); }),
  fetch('./translations/index.json').then(response => response.ok ? response.json() : {})
])
  .then(([records, translations]) => { archive.register(records); state.records = records; state.translations = new Set(Object.keys(translations)); state.filtered = [...records].sort(order); render(); })
  .catch(() => {
    count.textContent = 'The file index could not load';
    list.innerHTML = '<p class="file-empty">The research index is unavailable. Please reload this page.</p>';
    pageInfo.textContent = '';
    prev.disabled = next.disabled = true;
  });

function prepareMotion() {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.documentElement.classList.add('motion-ready');
  const targets = document.querySelectorAll('.section-head, .result-grid article, .chart-panel, .findings, .method-card, .timeline article, .video-card, .code-section>*, .archive-controls, .archive-meta');
  targets.forEach((node, index) => {
    node.dataset.reveal = '';
    node.style.setProperty('--reveal-delay', `${Math.min(index % 4, 3) * 70}ms`);
  });
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    });
  }, {threshold:.12, rootMargin:'0px 0px -6%'});
  targets.forEach(node => observer.observe(node));
}

prepareMotion();
