const titleNode = document.querySelector('#document-title');
const pathNode = document.querySelector('#document-path');
const contextNode = document.querySelector('#document-context');
const bodyNode = document.querySelector('#reader-body');
const noticeNode = document.querySelector('#reader-notice');
const rawLink = document.querySelector('#raw-link');
const copyButton = document.querySelector('#copy-code');
const copyStatus = document.querySelector('#copy-status');
const archive = window.ArchiveUI;
const filePath = new URLSearchParams(location.search).get('file');
let sourceText = '';
let indexedPaths = new Set();

function escapeHtml(value) {
  return String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');
}

function safeLink(href, sourcePath) {
  try {
    if (/^https?:\/\//i.test(href)) return href;
    const resolved = new URL(href, 'https://archive.invalid/' + sourcePath);
    const path = decodeURIComponent(resolved.pathname).replace(/^\/+/, '');
    return indexedPaths.has(path) ? archive.openUrl(path) + resolved.hash : null;
  } catch { return null; }
}

function inline(text, sourcePath) {
  return escapeHtml(text)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, href) => {
      const target = safeLink(href.replaceAll('&amp;', '&'), sourcePath);
      return target ? `<a href="${escapeHtml(target)}" target="_blank" rel="noopener">${label}</a>` : label;
    });
}

function tableCells(line) {
  return line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(cell => cell.trim());
}

function isSeparator(line) {
  return tableCells(line).every(cell => /^:?-{3,}:?$/.test(cell));
}

function markdown(text, sourcePath) {
  const lines = text.replaceAll('\r\n', '\n').split('\n');
  const out = [];
  let paragraph = [];
  let list = '';
  let inCode = false;
  let code = [];
  const flushParagraph = () => {
    if (paragraph.length) out.push(`<p>${inline(paragraph.join(' '), sourcePath)}</p>`);
    paragraph = [];
  };
  const closeList = () => { if (list) out.push(`</${list}>`); list = ''; };
  const flushCode = () => { out.push(`<pre><code>${escapeHtml(code.join('\n'))}</code></pre>`); code = []; };
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();
    if (/^```/.test(trimmed)) {
      flushParagraph(); closeList();
      if (inCode) flushCode();
      inCode = !inCode;
      continue;
    }
    if (inCode) { code.push(line); continue; }
    if (!trimmed) { flushParagraph(); closeList(); continue; }
    if (trimmed.includes('|') && lines[i + 1] && isSeparator(lines[i + 1])) {
      flushParagraph(); closeList();
      const headers = tableCells(trimmed);
      const rows = [];
      i += 2;
      while (i < lines.length && lines[i].trim().includes('|')) { rows.push(tableCells(lines[i])); i++; }
      i--;
      out.push('<table><thead><tr>' + headers.map(cell => `<th>${inline(cell, sourcePath)}</th>`).join('') + '</tr></thead><tbody>' + rows.map(row => '<tr>' + row.map(cell => `<td>${inline(cell, sourcePath)}</td>`).join('') + '</tr>').join('') + '</tbody></table>');
      continue;
    }
    const heading = trimmed.match(/^(#{1,4})\s+(.+)$/);
    if (heading) { flushParagraph(); closeList(); const level = heading[1].length; out.push(`<h${level}>${inline(heading[2], sourcePath)}</h${level}>`); continue; }
    if (/^(-{3,}|\*{3,})$/.test(trimmed)) { flushParagraph(); closeList(); out.push('<hr>'); continue; }
    const bullet = trimmed.match(/^[-*+]\s+(.+)$/);
    const number = trimmed.match(/^\d+[.)]\s+(.+)$/);
    if (bullet || number) {
      flushParagraph();
      const wanted = bullet ? 'ul' : 'ol';
      if (list !== wanted) { closeList(); out.push(`<${wanted}>`); list = wanted; }
      out.push(`<li>${inline((bullet || number)[1], sourcePath)}</li>`);
      continue;
    }
    if (trimmed.startsWith('>')) { flushParagraph(); closeList(); out.push(`<blockquote>${inline(trimmed.replace(/^>\s?/, ''), sourcePath)}</blockquote>`); continue; }
    closeList(); paragraph.push(trimmed);
  }
  flushParagraph(); closeList();
  if (inCode) flushCode();
  return out.join('\n');
}

function showError(message) {
  titleNode.textContent = 'Unable to preview this file';
  bodyNode.replaceChildren();
  const paragraph = document.createElement('p');
  paragraph.className = 'encoding-error';
  paragraph.textContent = message;
  bodyNode.append(paragraph);
}

async function load() {
  if (!filePath || filePath.startsWith('/') || filePath.includes('..')) { showError('The file path is missing or invalid.'); return; }
  try {
    const catalogResponse = await fetch('./catalog.json');
    if (!catalogResponse.ok) throw new Error('The file index is unavailable.');
    const records = await catalogResponse.json();
    archive.register(records);
    indexedPaths = new Set(records.map(record => record.path));
    const item = records.find(record => record.path === filePath);
    if (!item) throw new Error('This file is not in the research index.');
    const details = archive.describeFile(item);
    titleNode.textContent = details.title;
    document.title = `${details.title} · Lane / Lab`;
    pathNode.textContent = item.path;
    rawLink.href = archive.sourceUrl(item.path);
    rawLink.download = item.path.split('/').at(-1);
    const response = await fetch(archive.sourceUrl(item.path));
    if (!response.ok) throw new Error(`The original file returned HTTP ${response.status}.`);
    const bytes = await response.arrayBuffer();
    try { sourceText = new TextDecoder('utf-8', { fatal: true }).decode(bytes); }
    catch { throw new Error('This file is not UTF-8 text. Open the original file in a suitable application.'); }
    const extension = item.path.split('.').at(-1).toLowerCase();
    if (extension === 'md') {
      bodyNode.innerHTML = markdown(sourceText, item.path);
      const status = document.querySelector('#translation-status');
      if (/[\u4e00-\u9fff]/.test(sourceText)) {
        const translations = await fetch('./translations/index.json').then(r => r.json());
        const edition = translations[item.path];
        status.hidden = false;
        if (edition) {
          const englishText = await fetch(edition.file).then(r => { if (!r.ok) throw new Error('English edition unavailable'); return r.text(); });
          const englishHeading = englishText.match(/^#\s+(.+)$/m)?.[1];
          if (englishHeading) {
            titleNode.textContent = englishHeading;
            document.title = `${englishHeading} · Lane / Lab`;
          }
          const controls = document.querySelector('#language-switch');
          controls.hidden = false;
          controls.style.display = 'flex';
          const english = document.querySelector('#english-version');
          const original = document.querySelector('#original-version');
          function setLanguage(isEnglish) {
            bodyNode.innerHTML = markdown(isEnglish ? englishText : sourceText, item.path);
            document.documentElement.lang = isEnglish ? 'en' : 'zh-CN';
            english.setAttribute('aria-pressed', String(isEnglish));
            original.setAttribute('aria-pressed', String(!isEnglish));
            status.textContent = isEnglish ? edition.note : 'Unmodified Chinese source. Switch to the English edition for the research findings.';
            if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
              bodyNode.animate([{opacity:.35, transform:'translateY(5px)'},{opacity:1, transform:'translateY(0)'}], {duration:220, easing:'ease-out'});
            }
          }
          english.addEventListener('click', () => setLanguage(true));
          original.addEventListener('click', () => setLanguage(false));
          setLanguage(true);
        } else {
          status.textContent = 'An English edition has not yet been prepared for this historical record. The English project website presents the main methods and findings.';
          const link = document.createElement('a');
          link.href = './index.html#methods';
          link.textContent = ' Explore methods and equations.';
          status.append(link);
        }
      }
      const summaries = {
        'reports/OpenCV阶段总结_2026-09-07至09-08.md': 'English context: three separately started OpenCV laps were confirmed. The 16-second setting was a stop limit, not an independently measured lap time.',
        'experiment_data/2026-09-09/phone_timing/phone_comparison_report.md': 'English context: five listed laps per method were completed. Stopwatch timing, test order and a battery change limit the comparison.',
        'reports/pixel_evaluation_2026-09-12/像素偏差评价_复核后汇总.md': 'English context: 34 of 60 sampled frames were measurable. The pixel results apply only to those frames; review was visual, not independent blind annotation.'
      };
      noticeNode.textContent = summaries[item.path] || 'Historical research record. The source file is unchanged; language availability is shown below.';
      noticeNode.hidden = false;
    } else if (extension === 'json') {
      let value;
      try { value = JSON.stringify(JSON.parse(sourceText), null, 2); }
      catch { value = sourceText; }
      const pre = document.createElement('pre');
      pre.className = 'plain-source';
      pre.textContent = value;
      bodyNode.replaceChildren(pre);
      contextNode.textContent = 'Structured data preview · original file available above.';
    } else {
      const pre = document.createElement('pre');
      const code = document.createElement('code');
      code.textContent = sourceText;
      pre.append(code);
      bodyNode.replaceChildren(pre);
      if (/\.(py|js|html|css|sh|ipynb|toml|ya?ml|f90|c|h)$/i.test(item.path)) {
        bodyNode.classList.add('code-view');
        copyButton.hidden = false;
        contextNode.textContent = 'Read-only source preview. Copying preserves the exact file text.';
      } else {
        contextNode.textContent = 'Original text preview · UTF-8 decoded.';
      }
    }
  } catch (error) {
    showError(error.message || 'The file could not be loaded.');
  }
}

copyButton.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(sourceText);
    copyStatus.textContent = 'Code copied.';
    copyButton.textContent = 'Copied';
  } catch {
    copyStatus.textContent = 'Copy was blocked by the browser. Select the code below to copy it.';
  }
});

load();
