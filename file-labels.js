/* Human-readable labels keep repeated filenames tied to their experiment. */
const knownRuns = {
  '20260908_152243_132290': 'OpenCV completed lap 1 · 8 Sep 2026',
  '20260908_152535_389653': 'OpenCV completed lap 2 · 8 Sep 2026',
  '20260908_152627_147979': 'OpenCV completed lap 3 · 8 Sep 2026',
  '20260912_075420_928124': 'OpenCV camera-only check · 12 Sep 2026, 07:54',
  '20260912_080948_647069': 'CNN trial 01 · 12 Sep 2026, 08:09',
  '20260912_081536_739891': 'OpenCV trial 01 · 12 Sep 2026, 08:15',
  '20260912_081811_635511': 'CNN trial 02 · 12 Sep 2026, 08:18',
  '20260912_082301_535034': 'OpenCV trial 02 · 12 Sep 2026, 08:23',
  '20260912_082503_192901': 'CNN trial 03 · 12 Sep 2026, 08:25',
  '20260912_082750_454344': 'OpenCV trial 03 · 12 Sep 2026, 08:27',
  '20260912_083059_817688': 'CNN trial 01 repeat · 12 Sep 2026, 08:30',
  '20260912_083241_823654': 'OpenCV trial 01 repeat · 12 Sep 2026, 08:32',
  '20260912_083630_427620': 'CNN trial 02 repeat · 12 Sep 2026, 08:36'
};

const featuredLabels = {
  'reports/OpenCV阶段总结_2026-09-07至09-08.md': 'OpenCV development and three completed laps',
  'experiment_data/2026-09-09/phone_timing/phone_comparison_report.md': 'Five OpenCV and five CNN phone-timed laps',
  'reports/pixel_evaluation_2026-09-12/像素偏差评价_复核后汇总.md': 'Reviewed pixel-offset evaluation · six runs'
};

function inferContext(path) {
  for (const [runId, label] of Object.entries(knownRuns)) {
    if (path.includes(runId)) return label;
  }
  if (path.includes('/phone_timing/')) return 'Phone-timed comparison · 9 Sep 2026';
  if (path.includes('/demo_videos/')) return 'Demonstration videos · 12 Sep 2026';
  if (path.includes('/setup_photos/')) return 'Experimental setup · 12 Sep 2026';
  const stamped = path.match(/(20\d{6})_(\d{6})/);
  if (stamped) {
    const d = stamped[1];
    const t = stamped[2];
    const method = /cnn/i.test(path) ? 'CNN' : /opencv/i.test(path) ? 'OpenCV' : 'Experiment';
    return `${method} run · ${d.slice(0,4)}-${d.slice(4,6)}-${d.slice(6,8)} ${t.slice(0,2)}:${t.slice(2,4)}`;
  }
  if (path.includes('/pixel_evaluation_20260912/')) return 'Pixel evaluation · 12 Sep 2026';
  if (path.startsWith('experiment_backups/')) return 'Historical backup';
  if (path.startsWith('raspi_backup_')) return 'Raspberry Pi source archive';
  if (path.startsWith('reports/')) return 'Research report';
  if (path.startsWith('experiments/')) return 'Experiment code and analysis';
  if (path.startsWith('scripts/')) return 'Project script';
  return 'Research archive';
}

function inferRole(path) {
  const name = path.split('/').at(-1);
  const lower = name.toLowerCase();
  if (lower === 'summary.json') return 'Run summary';
  if (lower === 'settings.json') return 'Run settings';
  if (lower === 'frames.csv') return 'Frame-by-frame log';
  if (lower === 'manifest.json') return 'File manifest';
  if (lower === 'readme.md') return 'Archive notes';
  if (lower === 'verification.json') return 'Verification record';
  if (lower === 'pixel_annotations_draft.csv') return 'Frame annotations';
  if (/^\d+_raw\.(png|jpe?g)$/i.test(name)) return `Raw camera frame ${name.split('_')[0]}`;
  if (/^\d+_debug\.(png|jpe?g)$/i.test(name)) return `Debug frame ${name.split('_')[0]}`;
  if (/cam_image_array_/i.test(name)) return `Camera image ${name.split('_')[0]}`;
  if (/\.mov$|\.mp4$/i.test(name)) return `Video · ${name.replace(/\.(mov|mp4)$/i, '')}`;
  if (/\.tflite$|\.h5$|\.onnx$/i.test(name)) return `Model file · ${name}`;
  if (/\.tar\.gz$|\.zip$/i.test(name)) return `Backup package · ${name}`;
  if (/\.py$/i.test(name)) return `Python source · ${name}`;
  if (/\.md$/i.test(name)) return `Report / notes · ${name}`;
  if (/\.csv$/i.test(name)) return `Data table · ${name}`;
  return name;
}

function describeFile(item) {
  if (featuredLabels[item.path]) return { title: featuredLabels[item.path], context: 'Featured evidence', role: 'Source report' };
  const context = inferContext(item.path);
  const role = inferRole(item.path);
  return { title: `${context} — ${role}`, context, role };
}

let packagedUrls = new Map();
function register(records) { packagedUrls = new Map(records.map(item => [item.path, item.url])); }
function sourceUrl(path) {
  if (packagedUrls.has(path)) return packagedUrls.get(path);
  return '#attachment-unavailable';
}

function openUrl(path) {
  if (/\.(md|txt|json|csv|py|js|html|css|sh|ipynb|toml|ya?ml|f90|c|h)$/i.test(path)) return './reader.html?file=' + encodeURIComponent(path);
  return sourceUrl(path);
}

window.ArchiveUI = { describeFile, sourceUrl, openUrl, featuredLabels, register };
