const lapChart = document.querySelector('#lap-chart');
const pixelChart = document.querySelector('#pixel-chart');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function mean(values) {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function animatedNumber(value, decimals, suffix, className = 'animated-number') {
  const initial = reducedMotion ? value.toFixed(decimals) : (0).toFixed(decimals);
  const node = el('b', className, `${initial}${suffix}`);
  node.dataset.value = String(value);
  node.dataset.decimals = String(decimals);
  node.dataset.suffix = suffix;
  return node;
}

function countTo(node, delay = 0) {
  const target = Number(node.dataset.value);
  const decimals = Number(node.dataset.decimals || 0);
  const suffix = node.dataset.suffix || '';
  if (reducedMotion) {
    node.textContent = `${target.toFixed(decimals)}${suffix}`;
    return;
  }
  window.setTimeout(() => {
    const started = performance.now();
    const duration = 950;
    const frame = now => {
      const progress = Math.min(1, (now - started) / duration);
      const eased = 1 - Math.pow(1 - progress, 3);
      node.textContent = `${(target * eased).toFixed(decimals)}${suffix}`;
      if (progress < 1) requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  }, delay);
}

function activateChart(chart) {
  if (chart.dataset.animated === 'true') return;
  chart.dataset.animated = 'true';
  chart.classList.add('chart-animate');
  chart.querySelectorAll('[data-value]').forEach((node, index) => countTo(node, index * 90));
}

const chartObserver = 'IntersectionObserver' in window && !reducedMotion
  ? new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        activateChart(entry.target);
        chartObserver.unobserve(entry.target);
      });
    }, { threshold: 0.28 })
  : null;

function prepareChart(chart) {
  if (chartObserver) chartObserver.observe(chart);
  else activateChart(chart);
}

function lapSeries(name, values, className) {
  const row = el('div', `lap-series ${className}`);
  row.append(el('strong', 'lap-series-name', name));
  const axis = el('div', 'lap-axis');
  values.forEach((value, index) => {
    const dot = el('button', 'lap-dot');
    dot.type = 'button';
    dot.style.setProperty('--dot-left', `${((value - 10) / 10) * 100}%`);
    dot.style.setProperty('--dot-delay', `${index * 110}ms`);
    dot.style.top = `${index % 2 ? 33 : 17}px`;
    dot.title = `${name} trial ${index + 1}: ${value.toFixed(2)} seconds`;
    dot.setAttribute('aria-label', dot.title);
    axis.append(dot);
  });
  row.append(axis, animatedNumber(mean(values), 3, ' s mean', 'lap-mean'));
  return row;
}

function renderLap(data) {
  const opencv = data.opencv_phone_times_s;
  const cnn = data.cnn_runs.map(run => run.phone_lap_time_s);
  if (opencv.length !== 5 || cnn.length !== 5 || [...opencv, ...cnn].some(v => !Number.isFinite(v))) throw new Error('Unexpected lap data');
  lapChart.replaceChildren();
  const scale = el('div', 'lap-scale');
  for (let second = 10; second <= 20; second += 2) scale.append(el('span', '', `${second} s`));
  lapChart.append(scale, lapSeries('OpenCV', opencv, 'opencv'), lapSeries('CNN', cnn, 'cnn'));
  const details = el('details', 'chart-details');
  details.append(el('summary', '', 'Show exact lap times'));
  const table = el('table', 'data-table');
  const head = el('thead');
  const hr = el('tr');
  ['Run order', 'OpenCV (s)', 'CNN (s)'].forEach(label => hr.append(el('th', '', label)));
  head.append(hr);
  const body = el('tbody');
  opencv.forEach((value, i) => {
    const row = el('tr');
    [String(i + 1), value.toFixed(2), cnn[i].toFixed(2)].forEach(cell => row.append(el('td', '', cell)));
    body.append(row);
  });
  table.append(head, body);
  details.append(table);
  lapChart.append(details);
  prepareChart(lapChart);
}

function renderPixel(data) {
  const rows = [...data].sort((a, b) => a.trial.localeCompare(b.trial, 'en'));
  if (rows.length !== 6 || rows.some(row => !Number.isFinite(row.rmse_px) || !Number.isFinite(row.measured))) throw new Error('Unexpected pixel data');
  pixelChart.replaceChildren();
  rows.forEach((row, index) => {
    const line = el('div', 'pixel-row');
    line.tabIndex = 0;
    line.setAttribute('aria-label', `${row.trial.replace('_', ' ')}: RMSE ${row.rmse_px.toFixed(2)} pixels, ${row.measured} of ${row.selected} frames measurable`);
    line.style.setProperty('--bar-delay', `${index * 95}ms`);
    line.append(el('span', 'pixel-label', row.trial.replace('_', ' ')));
    const track = el('div', 'pixel-track');
    const bar = el('span', row.trial.startsWith('OpenCV') ? 'opencv' : 'cnn');
    bar.style.setProperty('--bar-width', `${Math.min(100, (row.rmse_px / 25) * 100)}%`);
    track.append(bar);
    line.append(track, animatedNumber(row.rmse_px, 2, ' px', 'pixel-value'), el('small', 'pixel-n', `${row.measured}/${row.selected} frames`));
    pixelChart.append(line);
  });
  const scale = el('div', 'pixel-scale');
  ['0', '5', '10', '15', '20', '25 px'].forEach(value => scale.append(el('span', '', value)));
  pixelChart.append(scale);
  prepareChart(pixelChart);
}

Promise.all([
  fetch('./data/phone-comparison.json').then(r => { if (!r.ok) throw new Error('Lap data unavailable'); return r.json(); }),
  fetch('./data/pixel-summary.json').then(r => { if (!r.ok) throw new Error('Pixel data unavailable'); return r.json(); })
]).then(([lap, pixel]) => { renderLap(lap); renderPixel(pixel); })
  .catch(() => {
    lapChart.textContent = 'The source data could not load. Open the linked report for the recorded values.';
    pixelChart.textContent = 'The source data could not load. Open the linked report for the recorded values.';
  });
